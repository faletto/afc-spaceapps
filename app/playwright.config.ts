import { defineConfig } from '@playwright/test';

// Test the production bundle (what gets deployed, including the bundled worker); the dev server's
// dependency re-optimisation can reload the page mid-test and cause flakes.
export default defineConfig({
  testDir: 'e2e',
  timeout: 60_000, // long journeys (D-6) take >30 s under headless software GL
  // Headless software GL keeps the main thread busy uploading the 8192x4096 basemap, which delays worker replies;
  // the default 5 s expect timeout is too tight for that (not an app bug).
  expect: { timeout: 15_000 },
  webServer: { command: 'npm run build && npm run preview -- --port 4173 --strictPort', url: 'http://localhost:4173', reuseExistingServer: !process.env.CI, timeout: 120_000 },
  use: { baseURL: 'http://localhost:4173' },
});
