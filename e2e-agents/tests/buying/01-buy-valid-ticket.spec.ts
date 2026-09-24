import { test, expect } from '@playwright/test';

test.describe('Buying tickets', () => {
  test('Buy a valid ticket from the event page', async ({ page }) => {
    await page.goto('/events/1/');

    const quantity = page.getByRole('spinbutton').first();
    await expect(quantity).toBeVisible();
    await quantity.fill('2');

    const buyButton = page.getByRole('button', { name: 'Buy tickets' }).first();
    await expect(buyButton).toBeVisible();
    await buyButton.click();

    await expect(page.getByText('Дали сакате да го додадете билетот во кошничката?')).toBeVisible();

    await page.getByRole('button', { name: 'Додади' }).click();

    await expect(page.locator('[data-cart-count]')).toContainText('2');

    await page.goto('/cart/');
    await expect(page.getByText('E2E Rock Night')).toBeVisible();
    await expect(page.getByText('Regular')).toBeVisible();
    await expect(page.getByText('x2 × 900.00 =')).toBeVisible();
        // Reviewer: one item in the cart, so the amount must appear twice (line subtotal and cart total)
    await expect(page.getByText('1800.00', { exact: true })).toHaveCount(2);
  });
});
