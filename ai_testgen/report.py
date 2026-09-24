"""Markdown report for one agent run (ready to paste into the project documentation)."""
from __future__ import annotations

from pathlib import Path


def write_reports(summary: dict, run_dir: Path) -> None:
    base, final = summary["baseline"], summary["final"]
    iterations = summary["iterations"]
    kept = [i for i in iterations if i["outcome"] == "kept"]
    tokens_in = sum(i["input_tokens"] for i in iterations)
    tokens_out = sum(i["output_tokens"] for i in iterations)

    lines = [
        f"# AI test generation run {summary['run_id']}",
        "",
        f"- Model: `{summary['provider']}` / `{summary['model']}`",
        f"- Coverage: **{base['percent']}% -> {final['percent']}%** "
        f"({base['covered']} -> {final['covered']} of {final['statements']} statements)",
        f"- Iterations: {len(iterations)}, test files kept: {len(kept)}",
        f"- Tokens: {tokens_in} in / {tokens_out} out",
        "",
        "## Iterations",
        "",
        "| # | Target | Uncovered before | Attempts | Outcome | Lines gained | Time (s) | Note |",
        "|---|--------|------------------|----------|---------|--------------|----------|------|",
    ]
    for i in iterations:
        lines.append(
            f"| {i['number']} | `{i['target']}` | {i['missing_before']} | {i['attempts']} | "
            f"{i['outcome']} | {i['lines_gained']} | {i['seconds']} | {i['note']} |"
        )

    bugs = [(i["test_file"], bug) for i in kept for bug in i["bugs_flagged"]]
    lines += ["", "## Suspected application bugs (tests marked xfail by the agent)", ""]
    lines += [f"- `{file}`: {bug}" for file, bug in bugs] or ["- none"]

    before, after = summary["per_file_before"], summary["per_file_after"]
    changed = [p for p in before if after.get(p, 0) != before[p]]
    lines += ["", "## Uncovered lines per file", "", "| File | Before | After |", "|------|--------|-------|"]
    lines += [f"| `{p}` | {before[p]} | {after.get(p, 0)} |" for p in sorted(changed)] or ["| (no change) | | |"]

    lines += [
        "",
        "## Outcome legend",
        "",
        "kept = passed, stable, suite still green and coverage increased; "
        "no-gain = passed but covered nothing new; failing = still failing after repairs; "
        "flaky = failed on a repeated run; broke-suite = passed alone but not with the full suite; "
        "unsafe = used forbidden APIs; no-code / llm-error = unusable model answer.",
        "",
        "Prompts and raw model answers are stored next to this report (prompts/, responses/), "
        "and rejected files in rejected/. Re-run this exact session without an API key with:",
        "",
        f"`python -m ai_testgen --provider replay --replay-dir ai_testgen/runs/{summary['run_id']}/responses`",
    ]
    (run_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
