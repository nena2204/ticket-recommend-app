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


def test_prompt_budget_keeps_prompt_small_but_keeps_factories():
    """With a budget (GitHub Models free tier) the prompt shrinks but still has conftest.py."""
    from ai_testgen.prompts import build_generation_prompt

    missing = list(range(1, 400))
    full = build_generation_prompt("orders/views.py", missing, [], None)
    small = build_generation_prompt("orders/views.py", [60, 61, 62], [], 12000)

    assert len(small) < len(full)
    assert len(small) <= 12000 + 3000  # conftest.py is always included
    assert "tests/conftest.py" in small


def test_llm_client_retries_when_server_is_busy(monkeypatch):
    """A 503 'model overloaded' answer is retried instead of wasting an iteration."""
    import json
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    from ai_testgen import llm

    calls = []

    class FakeLLM(BaseHTTPRequestHandler):
        def do_POST(self):
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            calls.append(self.path)
            if len(calls) == 1:
                self.send_response(503)
                self.end_headers()
                self.wfile.write(b'{"error": "high demand"}')
                return
            body = json.dumps({"choices": [{"message": {"content": "ok"}}], "usage": {}}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), FakeLLM)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setattr(llm, "RETRY_WAITS", [0, 0])
    monkeypatch.setattr(llm.time, "sleep", lambda seconds: None)
    monkeypatch.setenv("OPENAI_BASE_URL", f"http://127.0.0.1:{server.server_port}/v1")
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    try:
        answer = llm.make_provider("openai", "fake-model").complete("system", [{"role": "user", "content": "hi"}])
    finally:
        server.shutdown()

    assert answer.text == "ok"
    assert calls == ["/v1/chat/completions", "/v1/chat/completions"]
