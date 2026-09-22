"""Unit tests for the AI test-generation agent itself (testing the tester)."""
from ai_testgen.coverage_tools import CoverageSnapshot, FileCoverage, annotated_source
from ai_testgen.prompts import bug_reports, extract_code, forbidden_usage


def test_extract_code_takes_the_python_block():
    """Only the fenced Python code is extracted from a model answer."""
    answer = "Some reasoning.\n```python\ndef test_x():\n    assert True\n```\nThanks"
    assert extract_code(answer) == "def test_x():\n    assert True\n"


def test_extract_code_accepts_a_cut_off_block():
    """An answer truncated before the closing fence is still usable."""
    assert extract_code("```python\nimport pytest\n") == "import pytest\n"


def test_extract_code_returns_none_without_code():
    """Answers without code are detected so the agent can ask again."""
    assert extract_code("I cannot help with that.") is None


def test_forbidden_usage_blocks_dangerous_code():
    """The safety guard rejects subprocess calls and real SMTP."""
    code = "import subprocess\nsettings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'"
    assert len(forbidden_usage(code)) == 2
    assert forbidden_usage("from unittest import mock") == []


def test_bug_reports_are_collected_from_xfail_reasons():
    """Bugs flagged by the model through xfail reasons end up in the report."""
    code = '@pytest.mark.xfail(strict=True, reason="BUG: pisa is not imported")'
    assert bug_reports(code) == ["BUG: pisa is not imported"]


def test_annotated_source_marks_missing_lines():
    """Uncovered lines are marked with '>>' in the prompt."""
    lines = annotated_source("manage.py", [1]).splitlines()
    assert lines[0].startswith(">>")
    assert not lines[1].startswith(">>")


def test_candidates_skip_boilerplate_and_sort_by_missing_lines():
    """Targets are ordered by uncovered lines; migrations and __init__ are skipped."""
    snapshot = CoverageSnapshot(True, 0, 0, 0.0, files={
        "a/views.py": FileCoverage("a/views.py", 10, [1, 2]),
        "b/views.py": FileCoverage("b/views.py", 10, [1, 2, 3]),
        "a/migrations/0001.py": FileCoverage("a/migrations/0001.py", 10, [1, 2, 3, 4]),
        "c/models.py": FileCoverage("c/models.py", 10, []),
    })
    assert [c.path for c in snapshot.candidates()] == ["b/views.py", "a/views.py"]
