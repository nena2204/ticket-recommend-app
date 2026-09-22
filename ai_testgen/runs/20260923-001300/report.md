# AI test generation run 20260923-001300

- Model: `openai` / `gemini-flash-latest`
- Coverage: **56.55% -> 56.55%** (354 -> 354 of 626 statements)
- Iterations: 1, test files kept: 0
- Tokens: 0 in / 0 out

## Iterations

| # | Target | Uncovered before | Attempts | Outcome | Lines gained | Time (s) | Note |
|---|--------|------------------|----------|---------|--------------|----------|------|
| 1 | `events/views_profile.py` | 32 | 1 | llm-error | 0 | 30.1 | HTTP 503 from https://generativelanguage.googleapis.com/v1beta/openai/chat/completions: [{
  "error": {
    "code": 503,
    "message": "This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.",
    "status": "UNAVAILABLE"
  }
}
] |

## Suspected application bugs (tests marked xfail by the agent)

- none

## Uncovered lines per file

| File | Before | After |
|------|--------|-------|
| (no change) | | |

## Outcome legend

kept = passed, stable, suite still green and coverage increased; no-gain = passed but covered nothing new; failing = still failing after repairs; flaky = failed on a repeated run; broke-suite = passed alone but not with the full suite; unsafe = used forbidden APIs; no-code / llm-error = unusable model answer.

Prompts and raw model answers are stored next to this report (prompts/, responses/), and rejected files in rejected/. Re-run this exact session without an API key with:

`python -m ai_testgen --provider replay --replay-dir ai_testgen/runs/20260923-001300/responses`
