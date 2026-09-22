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

CONTEXT_FILES = [
    "tests/conftest.py",
    "tests/test_cart_flow.py",
    "TicketRecommend/urls.py",
    "events/urls.py",
    "orders/urls.py",
    "tickets_addons/urls.py",
    "events/models.py",
    "orders/models.py",
    "tickets_addons/models.py",
    "orders/forms.py",
    "tickets_addons/forms.py",
]

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


def build_generation_prompt(target: str, missing_lines: list[int], existing_ai_tests: list[str]) -> str:
    source = _read(target)
    parts = [
        f"Write NEW pytest tests that execute the uncovered lines of `{target}`.",
        "Lines marked with `>>` are not executed by the current test suite. Cover as many of "
        "them as you can with meaningful assertions.",
        f"\n### Target file: {target}\n```\n{annotated_source(target, missing_lines)}\n```",
    ]
    for path in CONTEXT_FILES:
        if path != target and (PROJECT_ROOT / path).exists():
            parts.append(f"\n### Context: {path}\n```python\n{_read(path)}\n```")
    for template in _templates_used_by(source):
        text = _read(template)[:MAX_TEMPLATE_CHARS]
        parts.append(f"\n### Template: {template} (may be truncated)\n```html\n{text}\n```")
    if existing_ai_tests:
        listing = "\n".join(f"- {name}" for name in existing_ai_tests)
        parts.append(
            "\nThese AI-generated test files already exist; do not duplicate their tests:\n" + listing
        )
    return "\n".join(parts)


def build_repair_prompt(test_output: str) -> str:
    return (
        "Running your test file failed. Here is the pytest output (truncated):\n"
        f"```\n{test_output[-6000:]}\n```\n"
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
