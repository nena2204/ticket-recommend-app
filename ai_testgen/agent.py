"""Coverage-guided test generation agent.

The agent repeats an observe -> plan -> act -> verify loop:

1. observe  run the whole fast pytest suite with coverage (coverage.py JSON report)
2. plan     pick the file with the most uncovered lines (or the file given by --target)
3. act      ask an LLM for a pytest file that executes those lines
4. verify   run the new file; on failure send the pytest output back to the LLM and let it
            repair the test (up to --max-repairs times); re-run it for flakiness; run the
            whole suite again and keep the file ONLY if the suite still passes and coverage
            really went up. Everything else is thrown away.

Usage examples (from the project root):
    python -m ai_testgen --iterations 5
    python -m ai_testgen --target events/views_profile.py --iterations 2
    python -m ai_testgen --provider openai --model gpt-4.1-mini
    python -m ai_testgen --provider replay --replay-dir ai_testgen/runs/<run>/responses
"""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from .coverage_tools import PROJECT_ROOT, CoverageSnapshot, measure_coverage, run_pytest
from .llm import LLMError, make_provider
from .prompts import (
    SYSTEM_PROMPT, bug_reports, build_generation_prompt, build_repair_prompt,
    extract_code, forbidden_usage,
)
from .report import write_reports

GENERATED_DIR = PROJECT_ROOT / "tests" / "ai_generated"
RUNS_DIR = PROJECT_ROOT / "ai_testgen" / "runs"


@dataclass
class Iteration:
    number: int
    target: str
    missing_before: int
    outcome: str = "pending"          # kept | no-gain | failing | flaky | unsafe | broke-suite | no-code | llm-error
    attempts: int = 0
    test_file: str | None = None
    lines_gained: int = 0
    coverage_before: float = 0.0
    coverage_after: float = 0.0
    bugs_flagged: list[str] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    seconds: float = 0.0
    note: str = ""


class Agent:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.provider = make_provider(args.provider, args.model, args.replay_dir)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.run_id = stamp
        self.run_dir = RUNS_DIR / stamp
        (self.run_dir / "responses").mkdir(parents=True, exist_ok=True)
        (self.run_dir / "prompts").mkdir(exist_ok=True)
        (self.run_dir / "rejected").mkdir(exist_ok=True)
        self.call_counter = 0
        self.failed_targets: dict[str, int] = {}
        self.attempted: dict[str, int] = {}
        self.iterations: list[Iteration] = []

    # ------------------------------------------------------------------ helpers
    def log(self, message: str) -> None:
        print(f"[ai-testgen] {message}", flush=True)

    def ask(self, messages: list[dict], iteration: Iteration) -> str:
        self.call_counter += 1
        number = f"{self.call_counter:02d}"
        (self.run_dir / "prompts" / f"{number}.md").write_text(messages[-1]["content"], encoding="utf-8")
        response = self.provider.complete(SYSTEM_PROMPT, messages)
        (self.run_dir / "responses" / f"{number}.txt").write_text(response.text, encoding="utf-8")
        iteration.input_tokens += response.input_tokens
        iteration.output_tokens += response.output_tokens
        return response.text

    def choose_target(self, snapshot: CoverageSnapshot) -> str | None:
        wanted = self.args.target or []
        # Files not attempted yet in this run come first, then by most uncovered lines.
        ordered = sorted(snapshot.candidates(),
                         key=lambda c: (self.attempted.get(c.path, 0), -c.missing))
        for candidate in ordered:
            if wanted and candidate.path not in wanted:
                continue
            if self.failed_targets.get(candidate.path, 0) >= 2:
                continue  # the model failed twice on this file; try something else
            self.attempted[candidate.path] = self.attempted.get(candidate.path, 0) + 1
            return candidate.path
        return None

    def existing_ai_tests(self) -> list[str]:
        return sorted(p.name for p in GENERATED_DIR.glob("test_ai_*.py"))

    def reject(self, iteration: Iteration, test_path: Path, outcome: str, note: str = "") -> None:
        iteration.outcome = outcome
        iteration.note = note
        if test_path.exists():
            destination = self.run_dir / "rejected" / test_path.name
            destination.write_text(test_path.read_text(encoding="utf-8"), encoding="utf-8")
            test_path.unlink()
        self.failed_targets[iteration.target] = self.failed_targets.get(iteration.target, 0) + 1

    # --------------------------------------------------------------- one step
    def step(self, number: int, snapshot: CoverageSnapshot) -> CoverageSnapshot:
        target = self.choose_target(snapshot)
        if target is None:
            raise StopIteration
        file_cov = snapshot.files[target]
        iteration = Iteration(number, target, file_cov.missing, coverage_before=snapshot.percent)
        self.iterations.append(iteration)
        started = time.monotonic()
        self.log(f"iteration {number}: target {target} ({file_cov.missing} uncovered lines)")

        slug = target.replace("/", "_").removesuffix(".py")
        test_path = GENERATED_DIR / f"test_ai_{slug}_{self.run_id.replace('-', '_')}_{number}.py"
        iteration.test_file = str(test_path.relative_to(PROJECT_ROOT)).replace("\\", "/")

        messages = [{"role": "user", "content": build_generation_prompt(
            target, file_cov.missing_lines, self.existing_ai_tests())}]
        passed = False
        try:
            for attempt in range(self.args.max_repairs + 1):
                iteration.attempts = attempt + 1
                answer = self.ask(messages, iteration)
                messages.append({"role": "assistant", "content": answer})
                code = extract_code(answer)
                if code is None:
                    feedback = "Your answer had no ```python code block. Send the full test file."
                    messages.append({"role": "user", "content": feedback})
                    iteration.outcome = "no-code"
                    continue
                unsafe = forbidden_usage(code)
                if unsafe:
                    feedback = (f"The file uses forbidden APIs {unsafe}. Remove them (use mocks) "
                                "and send the full file again.")
                    messages.append({"role": "user", "content": feedback})
                    iteration.outcome = "unsafe"
                    continue
                test_path.write_text(code, encoding="utf-8")
                result = run_pytest(["-q", str(test_path)], timeout=self.args.test_timeout)
                if result.passed:
                    passed = True
                    break
                self.log(f"  attempt {attempt + 1} failed, asking the model to repair it")
                messages.append({"role": "user", "content": build_repair_prompt(result.output)})
                iteration.outcome = "failing"
        except LLMError as exc:
            self.reject(iteration, test_path, "llm-error", str(exc))
            iteration.seconds = round(time.monotonic() - started, 1)
            self.log(f"  LLM error: {exc}")
            return snapshot

        if not passed:
            self.reject(iteration, test_path, iteration.outcome, "did not pass after repairs")
        else:
            snapshot = self.verify(iteration, test_path, snapshot)
        iteration.seconds = round(time.monotonic() - started, 1)
        self.log(f"  -> {iteration.outcome} {iteration.note}".rstrip())
        return snapshot

    def verify(self, iteration: Iteration, test_path: Path, before: CoverageSnapshot) -> CoverageSnapshot:
        # Flakiness check: a new test must pass several times in a row.
        for _ in range(self.args.stability_runs):
            if not run_pytest(["-q", str(test_path)], timeout=self.args.test_timeout).passed:
                self.reject(iteration, test_path, "flaky", "failed on a repeated run")
                return before

        after = measure_coverage()
        if not after.passed:
            self.reject(iteration, test_path, "broke-suite", "suite fails together with this file")
            return before
        gained = after.covered_lines - before.covered_lines
        if gained <= 0:
            self.reject(iteration, test_path, "no-gain", "coverage did not increase")
            return before

        header = (
            f"# Generated by ai_testgen ({self.provider.name}: {self.provider.model}) "
            f"on {datetime.now():%Y-%m-%d %H:%M}\n"
            f"# Target: {iteration.target} | +{gained} covered lines | "
            f"{before.percent}% -> {after.percent}%\n"
            "# Reviewed by: TODO (a team member must review AI-generated tests before merging)\n\n"
        )
        test_path.write_text(header + test_path.read_text(encoding="utf-8"), encoding="utf-8")
        iteration.outcome = "kept"
        iteration.lines_gained = gained
        iteration.coverage_after = after.percent
        iteration.bugs_flagged = bug_reports(test_path.read_text(encoding="utf-8"))
        return after

    # --------------------------------------------------------------- main loop
    def run(self) -> int:
        self.log(f"run {self.run_id} with {self.provider.name} ({self.provider.model})")
        baseline = measure_coverage()
        if not baseline.passed:
            self.log("The existing test suite fails. Fix it before running the agent:")
            print(baseline.output[-3000:])
            return 1
        self.log(f"baseline coverage {baseline.percent}% ({baseline.covered_lines}/{baseline.num_statements} lines)")

        snapshot = baseline
        for number in range(1, self.args.iterations + 1):
            if self.args.target_coverage and snapshot.percent >= self.args.target_coverage:
                self.log(f"target coverage {self.args.target_coverage}% reached")
                break
            try:
                snapshot = self.step(number, snapshot)
            except StopIteration:
                self.log("no more files to target")
                break

        summary = {
            "run_id": self.run_id,
            "provider": self.provider.name,
            "model": self.provider.model,
            "baseline": {"percent": baseline.percent, "covered": baseline.covered_lines,
                         "statements": baseline.num_statements},
            "final": {"percent": snapshot.percent, "covered": snapshot.covered_lines,
                      "statements": snapshot.num_statements},
            "per_file_before": {p: f.missing for p, f in baseline.files.items()},
            "per_file_after": {p: f.missing for p, f in snapshot.files.items()},
            "iterations": [asdict(i) for i in self.iterations],
        }
        (self.run_dir / "report.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        write_reports(summary, self.run_dir)
        self.log(f"coverage {baseline.percent}% -> {snapshot.percent}%")
        self.log(f"report: {(self.run_dir / 'report.md').relative_to(PROJECT_ROOT)}")
        return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python -m ai_testgen", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--provider", choices=["anthropic", "openai", "replay"], default="anthropic")
    parser.add_argument("--model", help="model name (default for anthropic: claude-sonnet-5)")
    parser.add_argument("--replay-dir", help="folder with recorded responses for --provider replay")
    parser.add_argument("--iterations", type=int, default=5, help="maximum number of files to generate")
    parser.add_argument("--target", action="append", help="only target this file (repeatable)")
    parser.add_argument("--max-repairs", type=int, default=2, help="repair attempts per test file")
    parser.add_argument("--stability-runs", type=int, default=2, help="extra runs to detect flaky tests")
    parser.add_argument("--target-coverage", type=float, help="stop when this total %% is reached")
    parser.add_argument("--test-timeout", type=int, default=120, help="seconds per pytest run")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        agent = Agent(args)
    except LLMError as exc:
        print(f"[ai-testgen] {exc}")
        return 2
    return agent.run()
