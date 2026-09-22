"""Prompt construction and parsing of the model's answer."""
from __future__ import annotations

import re
from pathlib import Path

from .coverage_tools import PROJECT_ROOT, annotated_source

SYSTEM_PROMPT = """You are a senior QA engineer who writes pytest tests for a Django 5.2 project
(a ticket-selling and event-recommendation site called Ticketo).

Rules for every test file you write:
- Use pytest style with pytest-django: the `client`, `rf`, `settings`, `django_user_model`
  and `mailoutbox` fixtures, `pytest.mark.django_db`, and `django.urls.reverse`.
- Reuse the factories and fixtures from tests/conftest.py (import factories with
  `from tests.conftest import EventFactory, ...`). Do not redefine them.
- An autouse fixture already switches e-mail to Django's in-memory backend. Never send real
  e-mail, never open network connections, never call subprocess or delete files.
- Anything unavailable or slow (PDF libraries, file system writes) must be replaced with
  unittest.mock.patch. The package xhtml2pdf is NOT installed.
- Tests must be deterministic and independent of each other and of the order they run in.
- Assert on real behaviour (status codes, database state, response content, JSON, e-mails),
  not only that code "does not crash".
- Give every test a short docstring saying what behaviour it checks.
- If the code under test is genuinely broken for valid input (for example it raises
  NameError because of a missing import), still write the test for the CORRECT behaviour and
  mark it with @pytest.mark.xfail(strict=True, reason="BUG: <one-line explanation>").
  Never weaken an assertion just to make a buggy path pass.

Answer with exactly one ```python fenced code block containing the complete test file
and nothing after it. You may write at most three sentences of reasoning before the block."""

# Code the agent refuses to execute, whatever the model says.
FORBIDDEN_PATTERNS = [
    r"\bsubprocess\b", r"\bos\.system\b", r"\bshutil\.rmtree\b", r"\bsmtplib\b",
    r"\bsocket\b", r"\burllib\.request\b", r"\brequests\.", r"EMAIL_BACKEND\s*=\s*['\"].*smtp",
    r"\bos\.remove\b", r"\bunlink\(",
]

# Context in order of importance. With a prompt budget (small free-tier models) the agent
# adds files from the top of this list until the budget is used up.
def _context_files(target: str) -> list[str]:
    app = target.split("/")[0]
    ordered = [
        "tests/conftest.py",
        "TicketRecommend/urls.py",
        f"{app}/models.py",
        f"{app}/urls.py",
        f"{app}/forms.py",
        "events/models.py",
        "orders/models.py",
        "tickets_addons/models.py",
        "orders/forms.py",
        "tickets_addons/forms.py",
        "events/urls.py",
        "orders/urls.py",
        "tickets_addons/urls.py",
        "tests/test_cart_flow.py",
    ]
    unique = []
    for path in ordered:
        if path != target and path not in unique and (PROJECT_ROOT / path).exists():
            unique.append(path)
    return unique


MAX_TEMPLATE_CHARS = 3500


def _read(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def _templates_used_by(source: str) -> list[str]:
    names = sorted(set(re.findall(r"[\"']([\w/\-]+\.(?:html|txt))[\"']", source)))
    found = []
    for name in names:
        path = PROJECT_ROOT / "templates" / name
        if path.exists():
            found.append(f"templates/{name}")
    return found


def _compact_source(target: str, missing_lines: list[int], context: int = 3) -> str:
    """Only the imports and the uncovered lines with a few lines around them."""
    lines = annotated_source(target, missing_lines).splitlines()
    keep = set(range(min(15, len(lines))))
    for number in missing_lines:
        keep.update(range(max(0, number - 1 - context), min(len(lines), number + context)))
    out, previous = [], -1
    for index in sorted(keep):
        if index != previous + 1:
            out.append("   ....")
        out.append(lines[index])
        previous = index
    return "\n".join(out)


def build_generation_prompt(target: str, missing_lines: list[int], existing_ai_tests: list[str],
                            budget: int | None = None) -> str:
    source = _read(target)
    annotated = annotated_source(target, missing_lines)
    if budget and len(annotated) > budget * 0.45:
        annotated = _compact_source(target, missing_lines)
    parts = [
        f"Write NEW pytest tests that execute the uncovered lines of `{target}`.",
        "Lines marked with `>>` are not executed by the current test suite. Cover as many of "
        "them as you can with meaningful assertions.",
        f"\n### Target file: {target}\n```\n{annotated}\n```",
    ]
    if existing_ai_tests:
        listing = "\n".join(f"- {name}" for name in existing_ai_tests)
        parts.append(
            "\nThese AI-generated test files already exist; do not duplicate their tests:\n" + listing
        )

    optional = [(f"Context: {path}", "python", _read(path)) for path in _context_files(target)]
    optional += [(f"Template: {t} (may be truncated)", "html", _read(t)[:MAX_TEMPLATE_CHARS])
                 for t in _templates_used_by(source)]
    used = sum(len(part) for part in parts)
    skipped = []
    for index, (title, language, text) in enumerate(optional):
        block = f"\n### {title}\n```{language}\n{text}\n```"
        # conftest.py (index 0) is always included: the tests cannot work without factories.
        if budget and index > 0 and used + len(block) > budget:
            skipped.append(title.split(": ", 1)[1])
            continue
        parts.append(block)
        used += len(block)
    if skipped:
        parts.append("\n(Other project files were left out to save space: " + ", ".join(skipped) + ")")
    return "\n".join(parts)


def build_repair_prompt(test_output: str, max_chars: int = 6000) -> str:
    return (
        "Running your test file failed. Here is the pytest output (truncated):\n"
        f"```\n{test_output[-max_chars:]}\n```\n"
        "Fix the TEST, not the application. If the failure proves the application itself is "
        "broken, keep the correct assertion and mark that test xfail(strict=True) with a "
        "'BUG: ...' reason. Reply with the complete corrected file in one ```python block."
    )


def extract_code(text: str) -> str | None:
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text, flags=re.DOTALL)
    if not blocks:
        # Tolerate an answer whose last fence was cut off (for example by max_tokens).
        blocks = re.findall(r"```(?:python|py)\s*\n(.*)$", text, flags=re.DOTALL)
    if not blocks:
        return None
    return max(blocks, key=len).strip() + "\n"


def forbidden_usage(code: str) -> list[str]:
    return [pattern for pattern in FORBIDDEN_PATTERNS if re.search(pattern, code)]


def bug_reports(code: str) -> list[str]:
    return re.findall(r"reason\s*=\s*[\"'](BUG:[^\"']*)[\"']", code)
