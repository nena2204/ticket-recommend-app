# AI test generation run 20260923-003346

- Model: `openai` / `gemini-3.8-flash`
- Coverage: **60.06% -> 66.45%** (376 -> 416 of 626 statements)
- Iterations: 1, test files kept: 1
- Tokens: 7381 in / 1502 out

## Iterations

| # | Target | Uncovered before | Attempts | Outcome | Lines gained | Time (s) | Note |
|---|--------|------------------|----------|---------|--------------|----------|------|
| 1 | `events/views_profile.py` | 32 | 1 | kept | 40 | 129.7 |  |

## Suspected application bugs (tests marked xfail by the agent)

- none

## Uncovered lines per file

| File | Before | After |
|------|--------|-------|
| `events/views_profile.py` | 32 | 0 |
| `orders/context_processors.py` | 3 | 2 |
| `orders/signals.py` | 1 | 0 |
| `orders/utils.py` | 28 | 22 |

## Outcome legend

kept = passed, stable, suite still green and coverage increased; no-gain = passed but covered nothing new; failing = still failing after repairs; flaky = failed on a repeated run; broke-suite = passed alone but not with the full suite; unsafe = used forbidden APIs; no-code / llm-error = unusable model answer.

Prompts and raw model answers are stored next to this report (prompts/, responses/), and rejected files in rejected/. Re-run this exact session without an API key with:

`python -m ai_testgen --provider replay --replay-dir ai_testgen/runs/20260923-003346/responses`
