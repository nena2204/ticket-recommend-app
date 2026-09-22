# Prompt for the healer agent

Select the **healer** agent and send:

---

Run the Playwright tests in `tests/` and fix the ones that fail. The application was
redesigned, so button labels may have changed. Update locators and assertions to match
the current UI, but do NOT change what a test verifies. If a test fails because the
application itself is broken, mark it with `test.fixme()` and explain why in a comment.
Re-run the tests after every fix.

---

Demo of self-healing (for the documentation):
1. `npx playwright test` -> everything passes
2. `python healer_demo.py break` -> renames "Buy tickets", "Додади" and "Send" in the templates
3. `npx playwright test` -> tests fail (screenshot this)
4. run the healer with the prompt above, then `npx playwright test` again -> passing
5. `git diff tests/` shows exactly which locators the healer changed (screenshot this)
6. `python healer_demo.py restore`
