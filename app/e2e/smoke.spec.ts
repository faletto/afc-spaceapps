import { test, expect } from '@playwright/test';
test('canvas renders', async ({ page }) => { await page.goto('/'); await expect(page.locator('canvas').first()).toBeVisible(); });
