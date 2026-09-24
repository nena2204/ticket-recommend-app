import { defineConfig, devices } from '@playwright/test';

const PORT = process.env.E2E_PORT ?? '8001';
const PYTHON = process.env.PYTHON ?? 'python';

export default defineConfig({
  testDir: './tests',
  fullyParallel: false, // one shared SQLite database, so keep tests sequential
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  forbidOnly: !!process.env.CI,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  // Starts Django with a fresh database and demo data (see start_server.py).
  webServer: {
    command: `${PYTHON} start_server.py`,
    url: `http://127.0.0.1:${PORT}/`,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    env: { E2E_PORT: PORT },
  },
});
