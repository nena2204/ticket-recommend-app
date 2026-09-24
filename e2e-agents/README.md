# Playwright Test Agents for Ticketo

Browser tests that are planned, written and repaired by the three official Playwright
Test Agents (Playwright 1.56+):

| Agent | Input | Output |
|-------|-------|--------|
| planner | the running app + `tests/seed.spec.ts` + a prompt | Markdown test plan in `specs/` |
| generator | a plan from `specs/` | `.spec.ts` tests in `tests/`, checked live in the browser |
| healer | failing tests | fixed locators/assertions, or `test.fixme()` when the app is broken |

The agents run inside an AI coding tool and control a real browser through Playwright's
MCP server (`npx playwright run-test-mcp-server`).

## One-time setup (run inside this folder)

```powershell
cd e2e-agents
npm install
npx playwright install chromium
npx playwright test            # starts Django and runs the seed test -> 1 passed
```

Then create the agent definitions for the tool you use:

```powershell
npm run agents:vscode    # GitHub Copilot in VS Code -> .github/chatmodes + .vscode/mcp.json
npm run agents:claude    # Claude Code -> .claude/agents + .mcp.json
```

Open **this folder** (`e2e-agents`) as the workspace in VS Code, or start `claude` in it,
so the tool finds the agent definitions. Re-run the command after updating Playwright.

## How the app is started

`playwright.config.ts` runs `start_server.py`, which deletes `e2e_db.sqlite3`, applies
migrations with `TicketRecommend.settings_e2e`, fills demo data with
`python manage.py seed_demo` and starts Django on port 8001. Your normal `db.sqlite3` is
never touched and e-mails are only printed to the console. Set `PYTHON` if your
interpreter is not called `python` (for example `$env:PYTHON = ".venv\Scripts\python"`).

## Workflow

1. Planner: `prompts/01-planner.md` -> `specs/ticketo-plan.md`
2. Generator: `prompts/02-generator.md` -> `tests/<area>/*.spec.ts`
3. `npx playwright test`, `npx playwright show-report`
4. Healer demo: `prompts/03-healer.md` together with `python healer_demo.py break|restore`

Review everything the agents write before committing it; the generated tests run in
GitHub Actions (job `e2e-agents`) like any other test.
