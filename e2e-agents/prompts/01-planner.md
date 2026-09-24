# Prompt for the planner agent

Select the **planner** agent (VS Code: the "🎭 planner" chat mode; Claude Code: mention
`playwright-test-planner`) and send:

---

Explore the Ticketo application and write a test plan to `specs/ticketo-plan.md`.
Use `tests/seed.spec.ts` as the seed. The app is a Django site for buying event tickets.
Demo data: events "E2E Rock Night", "E2E Summer Festival", "E2E Hamlet",
"E2E Vardar Derby", "E2E Philharmonic Gala", and user `e2e_user` / `E2e-Pass-2026!`.

Cover these areas, each as its own section with numbered scenarios:
1. Home page and event list (sections per category, links to event details).
2. Event details and buying tickets: choosing a quantity, the confirmation dialog,
   the cart counter/mini cart, invalid quantities (0, negative, very large).
3. Cart page: changing the quantity, removing items, the total price.
4. Accounts: registration (valid and invalid passwords), login, logout, and that
   checkout and the profile page require login.
5. Profile page: recommendations after a purchase.
6. Contact form: successful submit and validation errors.
7. The "How to buy" page and the 404 page for an unknown event.

For every scenario give the starting state, the steps, and the expected result.
Mark scenarios where the current behaviour looks like a bug.
