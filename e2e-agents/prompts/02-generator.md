# Prompt for the generator agent

Select the **generator** agent and send (one section at a time works best):

---

Use the plan in `specs/ticketo-plan.md` and generate Playwright tests for section 2
("Event details and buying tickets"). Save them in `tests/buying/`, one file per scenario.
Use `tests/seed.spec.ts` as the seed. Prefer getByRole / getByLabel / getByText locators
and web-first assertions (`await expect(...)`), never fixed timeouts (`waitForTimeout`).
Run each generated test and make sure it passes before moving on.

---

Repeat for the other sections, for example `tests/cart/`, `tests/accounts/`, `tests/contact/`.
