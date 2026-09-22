# AI test generation run 20260923-005017

- Model: `openai` / `gemini-3.8-flash`
- Coverage: **66.45% -> 73.8%** (416 -> 462 of 626 statements)
- Iterations: 5, test files kept: 1
- Tokens: 41468 in / 7756 out

## Iterations

| # | Target | Uncovered before | Attempts | Outcome | Lines gained | Time (s) | Note |
|---|--------|------------------|----------|---------|--------------|----------|------|
| 1 | `orders/views.py` | 70 | 3 | kept | 46 | 136.3 |  |
| 2 | `tickets_addons/views.py` | 52 | 1 | llm-error | 0 | 233.4 | HTTP 503 from https://generativelanguage.googleapis.com/v1beta/openai/chat/completions: [{
  "error": {
    "code": 503,
    "message": "This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.",
    "status": "UNAVAILABLE"
  }
}
] |
| 3 | `orders/utils.py` | 22 | 1 | llm-error | 0 | 197.7 | HTTP 429 from https://generativelanguage.googleapis.com/v1beta/openai/chat/completions: [{
  "error": {
    "code": 429,
    "message": "You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/rate-limit. \n* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 20, model: gemini-3.8-flash\nPlease retry in 11.029148943s.",
    "status": "RESOURCE_EXHAUSTED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.Help",
        "links": [
          {
            "description": "Learn more about Gemini API quotas",
            "url": "https://ai.google.dev/gemini-api/docs/rate-limits"
          }
        ]
      },
      {
        "@type": "type.googleapis.com/google.rpc.QuotaFailure",
        "violations": [
          {
            "quotaMetric": "generativelanguage.googleapis.com/generate_content_free_tier_requests",
            "quot -> rate limit reached; wait a few minutes (or until tomorrow for the daily limit) |
| 4 | `tickets_addons/signals.py` | 21 | 1 | llm-error | 0 | 193.4 | HTTP 429 from https://generativelanguage.googleapis.com/v1beta/openai/chat/completions: [{
  "error": {
    "code": 429,
    "message": "You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/rate-limit. \n* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 20, model: gemini-3.8-flash\nPlease retry in 57.569122534s.",
    "status": "RESOURCE_EXHAUSTED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.Help",
        "links": [
          {
            "description": "Learn more about Gemini API quotas",
            "url": "https://ai.google.dev/gemini-api/docs/rate-limits"
          }
        ]
      },
      {
        "@type": "type.googleapis.com/google.rpc.QuotaFailure",
        "violations": [
          {
            "quotaMetric": "generativelanguage.googleapis.com/generate_content_free_tier_requests",
            "quot -> rate limit reached; wait a few minutes (or until tomorrow for the daily limit) |
| 5 | `tickets_addons/utils.py` | 17 | 1 | llm-error | 0 | 193.5 | HTTP 429 from https://generativelanguage.googleapis.com/v1beta/openai/chat/completions: [{
  "error": {
    "code": 429,
    "message": "You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/rate-limit. \n* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 20, model: gemini-3.8-flash\nPlease retry in 44.036856028s.",
    "status": "RESOURCE_EXHAUSTED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.Help",
        "links": [
          {
            "description": "Learn more about Gemini API quotas",
            "url": "https://ai.google.dev/gemini-api/docs/rate-limits"
          }
        ]
      },
      {
        "@type": "type.googleapis.com/google.rpc.QuotaFailure",
        "violations": [
          {
            "quotaMetric": "generativelanguage.googleapis.com/generate_content_free_tier_requests",
            "quot -> rate limit reached; wait a few minutes (or until tomorrow for the daily limit) |

## Suspected application bugs (tests marked xfail by the agent)

- `tests/ai_generated/test_ai_orders_views_20260923_005017_1.py`: BUG: checkout_view tries to create Order with fields that exist only on TicketOrder, and missing street_no
- `tests/ai_generated/test_ai_orders_views_20260923_005017_1.py`: BUG: ticket_pdf queries Order instead of TicketOrder; Order has no pdf field

## Uncovered lines per file

| File | Before | After |
|------|--------|-------|
| `orders/context_processors.py` | 2 | 0 |
| `orders/views.py` | 70 | 26 |

## Outcome legend

kept = passed, stable, suite still green and coverage increased; no-gain = passed but covered nothing new; failing = still failing after repairs; flaky = failed on a repeated run; broke-suite = passed alone but not with the full suite; unsafe = used forbidden APIs; no-code / llm-error = unusable model answer.

Prompts and raw model answers are stored next to this report (prompts/, responses/), and rejected files in rejected/. Re-run this exact session without an API key with:

`python -m ai_testgen --provider replay --replay-dir ai_testgen/runs/20260923-005017/responses`
