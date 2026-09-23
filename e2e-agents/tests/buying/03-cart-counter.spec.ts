import { test, expect } from '@playwright/test';

test.describe('Buying tickets', () => {
  test('Cart counter reflects the added item', async ({ page }) => {
    await page.goto('/events/1/');

    const quantity = page.getByRole('spinbutton').first();
    const cartBadge = page.locator('[data-cart-count]');

    await quantity.fill('1');
    await page.getByRole('button', { name: 'Buy tickets' }).first().click();

    await expect(page.getByText('Дали сакате да го додадете билетот во кошничката?')).toBeVisible();
    await page.getByRole('button', { name: 'Додади' }).click();

    await expect(cartBadge).toContainText('1');

    await page.goto('/cart/');
    await expect(page.getByText('E2E Rock Night')).toBeVisible();
    await expect(page.getByText('Regular')).toBeVisible();
    await expect(page.getByText('x1 × 900.00 =')).toBeVisible();
    await expect(page.getByText('900.00')).toBeVisible();
  });
});
