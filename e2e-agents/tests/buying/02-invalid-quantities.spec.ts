import { test, expect } from '@playwright/test';

// Written by reviewer Nena: the generator only left an empty test.fixme() placeholder.
// test.fail(): the test RUNS and is expected to fail while the bug exists. When the app
// is fixed, the test starts passing and Playwright reports it, so test.fail() can be removed.
test.describe('Buying tickets - invalid quantities (known bug)', () => {
  for (const qty of ['0', '-1', '999999']) {
    test(`quantity ${qty} must not end up in the cart`, async ({ page }) => {
      test.fail(true, 'BUG: 0, negative and oversized quantities are not validated');

      await page.goto('/events/1/');
      const quantity = page.locator('[data-qty-for]').first();
      await expect(quantity).toBeVisible();
      await quantity.fill(qty);
      await page.getByRole('button', { name: 'Buy tickets' }).first().click();

      // A user who gets the confirmation dialog confirms it, as a real user would.
      const confirm = page.getByRole('button', { name: 'Додади', exact: true });
      const dialogOpened = await confirm
        .waitFor({ state: 'visible', timeout: 3000 })
        .then(() => true, () => false);
      if (dialogOpened) {
        await Promise.all([
          page.waitForResponse((response) => response.url().includes('/cart/add/')),
          confirm.click(),
        ]);
      }

      // Correct behaviour: an invalid quantity never reaches the cart.
      await page.goto('/cart/');
      await expect(page.getByText('E2E Rock Night')).toHaveCount(0);
    });
  }
});