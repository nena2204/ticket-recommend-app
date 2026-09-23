import { test } from '@playwright/test';

test.describe('Buying tickets', () => {
  test.fixme(
    'Invalid quantities should be rejected',
    true,
    'Known app bug: 0, negative, and oversized quantities continue into the cart confirmation flow without validation.'
  );
});
