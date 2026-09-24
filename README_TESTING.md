# Automated Testing Guide

## Goal

This test project verifies the ticket recommendation and ordering application at
multiple levels. It covers model calculations, forms, Django views, anonymous
session carts, rendered browser journeys and realistic browsing load, and adds two
AI agent-based testing approaches: browser tests planned, written and repaired by
Playwright Test Agents, and a custom agent that writes unit/integration tests guided
by code coverage.

## Tools

Classic testing:

- **pytest-django** provides concise Django unit and integration tests.
- **factory-boy** creates reusable, realistic database records without repeated setup.
- **pytest-cov / coverage.py** measures tested application code and produces reports.
- **Playwright (pytest-playwright)** exercises the real rendered UI in a browser.
- **Locust** simulates concurrent visitors for performance and load testing.
- **GitHub Actions** runs everything automatically on pushes and pull requests.

Agent-based testing:

- **Playwright Test Agents** (planner, generator, healer) run inside GitHub Copilot or
  Claude Code and drive a real browser through Playwright's MCP server. See `e2e-agents/`.
- **ai_testgen**, our own coverage-guided agent: it reads the coverage report, asks an
  LLM for tests of the uncovered lines, runs and repairs them, and keeps only tests
  that pass, are stable and increase coverage. See `ai_testgen/`.

## Test levels

| Level | Tool | Location | Written by |
|-------|------|----------|------------|
| Unit + integration | pytest-django, factory-boy | `tests/test_*.py` | team |
| Unit + integration | pytest-django | `tests/ai_generated/` | ai_testgen agent, reviewed by team |
| Tests of the agent itself | pytest | `tests/test_ai_testgen_tools.py` | team |
| Browser E2E | pytest-playwright | `tests/e2e/` | team |
| Browser E2E | Playwright Test (TypeScript) | `e2e-agents/tests/` | Playwright agents, reviewed by team |
| Load | Locust | `locustfile.py` | team |

## Setup

From the project root in the PyCharm terminal:

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
python manage.py migrate
```

## Commands

Unit and integration tests (including AI-generated ones), with coverage:

```
pytest
pytest --cov=events --cov=orders --cov=tickets_addons --cov-report=term-missing --cov-report=html
```

Hand-written browser tests:

```
playwright install chromium
pytest -m e2e --browser chromium
```

Agent-written browser tests (details in `e2e-agents/README.md`):

```
cd e2e-agents
npm install
npx playwright install chromium
npx playwright test
```

Coverage-guided AI agent (details in `ai_testgen/README.md`):

```
$env:ANTHROPIC_API_KEY = "sk-ant-..."
python -m ai_testgen --iterations 5
```

Load test against a server with demo data:

```
python e2e-agents/start_server.py
locust -f locustfile.py --host=http://127.0.0.1:8001
```

`e2e-agents/start_server.py` uses `TicketRecommend.settings_e2e`: a separate database
(`e2e_db.sqlite3`) filled by `python manage.py seed_demo`, and console e-mail.

## Continuous integration

`.github/workflows/tests.yml` runs four jobs on every push: `pytest` (with coverage),
`e2e-python`, `e2e-agents` and `load-smoke` (30-second headless Locust run).
`.github/workflows/ai-testgen.yml` is started manually and runs the AI agent with the
`ANTHROPIC_API_KEY` repository secret; its output is uploaded for review and never
committed automatically.

## Suggested division for three team members

1. Unit/integration tests, factories, coverage, and the `ai_testgen` agent.
2. Django Client integration tests, GitHub Actions, Locust.
3. Playwright tests (hand-written and agent-generated) and the healer demo.

## Screenshots and results

Add course-report evidence here:

- Successful `pytest` run and HTML coverage summary: *TODO*
- `ai_testgen` report (coverage before/after, bugs found): *TODO*
- Planner test plan (`e2e-agents/specs/`), generator output, healer before/after diff: *TODO*
- Playwright HTML report: *TODO*
- Locust statistics: *TODO*
- Successful GitHub Actions run: *TODO*
