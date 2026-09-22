// Seed test for the Playwright Test Agents.
//
// The planner and generator run this file first to bring the app into a known state.
// The data comes from `python manage.py seed_demo` (started by playwright.config.ts):
//   events : E2E Rock Night, E2E Summer Festival, E2E Hamlet, E2E Vardar Derby,
//            E2E Philharmonic Gala (each with ticket types)
//   user   : e2e_user / E2e-Pass-2026!
import { test, expect } from '@playwright/test';

test.describe('Seed', () => {
  test('seed', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('E2E Rock Night').first()).toBeVisible();
  });
});
