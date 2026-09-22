# ai_testgen - coverage-guided AI test generation agent

A small autonomous agent (about 500 lines of standard-library Python) that writes pytest
tests for the parts of the application the existing suite does not execute.

## How it works

```
        +--------------------------------------------------------------+
        |                                                              |
        v                                                              |
  1. OBSERVE  pytest + coverage.py (JSON)  -> uncovered lines per file   |
  2. PLAN     choose the file with the most uncovered lines              |
  3. ACT      prompt = source with '>>' on uncovered lines + factories,   |
              urls, models, forms, templates -> LLM -> test file         |
  4. VERIFY   run the file -- fails? --> send pytest output back to the  |
              LLM and let it repair the test (max N times)               |
              run it again (flakiness check)                             |
              run the whole suite: still green AND coverage higher?      |
                  yes -> keep the file     no -> throw it away ----------+
```

Guard rails: forbidden APIs (subprocess, real SMTP, sockets, file deletion) are refused
before any generated code runs; e-mail always goes to Django's in-memory backend; each
pytest run has a timeout; nothing is kept unless it passes, is stable, keeps the rest of
the suite green and really increases coverage. Kept files get a header with the model
name and a `Reviewed by: TODO` line, because a team member must review them before merging.

When the model finds code that is broken for valid input, it writes the test for the
correct behaviour and marks it `xfail(strict=True, reason="BUG: ...")`. These bugs are
listed in the run report.

## Running it

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
python -m ai_testgen --iterations 5
python -m ai_testgen --target events/views_profile.py --iterations 2
```

Other providers: any OpenAI-compatible API, including a local, free Ollama server.

```powershell
$env:OPENAI_API_KEY = "sk-..."; python -m ai_testgen --provider openai --model gpt-4.1-mini
$env:OPENAI_BASE_URL = "http://localhost:11434/v1"; python -m ai_testgen --provider openai --model qwen2.5-coder:14b
```

Every run is stored in `ai_testgen/runs/<timestamp>/`: `report.md` (tables for the
documentation), `report.json`, the raw model answers (`responses/`) and the rejected files.
A recorded run can be replayed without an API key or cost (delete the files that run kept
in `tests/ai_generated/` first, so the agent starts from the same state):

```powershell
python -m ai_testgen --provider replay --replay-dir ai_testgen/runs/<timestamp>/responses
```

## Files

| File | Purpose |
|------|---------|
| `agent.py` | the observe-plan-act-verify loop and command-line options |
| `coverage_tools.py` | runs pytest, reads the coverage.py JSON report, annotates source |
| `prompts.py` | system prompt, context building, code extraction, safety guard |
| `llm.py` | Anthropic, OpenAI-compatible and replay providers (standard library only) |
| `report.py` | Markdown report of a run |

The agent itself is tested in `tests/test_ai_testgen_tools.py`.
