"""Running pytest and reading coverage.py JSON reports."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
COVERED_PACKAGES = ["events", "orders", "tickets_addons"]

# Files where more tests add no value (generated code, boilerplate).
IGNORED_PARTS = ("migrations", "tests.py", "__init__.py", "apps.py", "admin.py")


@dataclass
class FileCoverage:
    path: str
    statements: int
    missing_lines: list[int]

    @property
    def missing(self) -> int:
        return len(self.missing_lines)


@dataclass
class CoverageSnapshot:
    passed: bool
    covered_lines: int
    num_statements: int
    percent: float
    files: dict[str, FileCoverage] = field(default_factory=dict)
    output: str = ""

    def candidates(self) -> list[FileCoverage]:
        """Files worth targeting, the ones with the most uncovered lines first."""
        usable = [
            f for f in self.files.values()
            if f.missing and not any(part in f.path for part in IGNORED_PARTS)
        ]
        return sorted(usable, key=lambda f: f.missing, reverse=True)


@dataclass
class RunResult:
    passed: bool
    output: str


def _pytest_env() -> dict:
    env = os.environ.copy()
    env.setdefault("DJANGO_SETTINGS_MODULE", "TicketRecommend.settings")
    return env


def run_pytest(args: list[str], timeout: int = 300) -> RunResult:
    command = [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", *args]
    try:
        completed = subprocess.run(
            command, cwd=PROJECT_ROOT, env=_pytest_env(),
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return RunResult(False, f"TIMEOUT after {timeout}s\n{exc.stdout or ''}")
    # Exit code 0 = all passed. xfail/xpass(non-strict) still give 0.
    return RunResult(completed.returncode == 0, completed.stdout + completed.stderr)


def measure_coverage() -> CoverageSnapshot:
    """Run the whole fast suite (unit + integration + AI tests) with coverage."""
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "coverage.json"
        cov_args = [f"--cov={pkg}" for pkg in COVERED_PACKAGES]
        result = run_pytest(["-q", *cov_args, f"--cov-report=json:{report}", "--cov-report="])
        if not report.exists():
            return CoverageSnapshot(False, 0, 0, 0.0, output=result.output)
        data = json.loads(report.read_text(encoding="utf-8"))

    files = {}
    for path, info in data["files"].items():
        normalized = path.replace("\\", "/")
        files[normalized] = FileCoverage(
            normalized, info["summary"]["num_statements"], info["missing_lines"]
        )
    totals = data["totals"]
    return CoverageSnapshot(
        passed=result.passed,
        covered_lines=totals["covered_lines"],
        num_statements=totals["num_statements"],
        percent=round(totals["percent_covered"], 2),
        files=files,
        output=result.output,
    )


def annotated_source(path: str, missing_lines: list[int]) -> str:
    """Source code with line numbers; uncovered lines are marked with '>>'."""
    missing = set(missing_lines)
    lines = (PROJECT_ROOT / path).read_text(encoding="utf-8").splitlines()
    return "\n".join(
        f"{'>>' if number in missing else '  '} {number:4d} | {text}"
        for number, text in enumerate(lines, start=1)
    )
