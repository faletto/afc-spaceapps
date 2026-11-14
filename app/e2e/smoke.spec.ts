import { test, expect } from '@playwright/test';

test('map loads both tiers', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('/');
  await expect(page.locator('canvas').first()).toBeVisible();
  await page.getByRole('button', { name: 'South Pole District' }).click();
  await expect(page.locator('canvas').first()).toBeVisible();
  await page.waitForTimeout(500);
  expect(errors).toEqual([]);
});

test('zooming shows pills and clicking one selects a plot', async ({ page }) => {
  await page.setViewportSize({ width: 1200, height: 700 });
  await page.goto('/');
  await page.waitForTimeout(2500);
  await page.mouse.move(600, 350);
  for (let i = 0; i < 5; i++) { await page.mouse.wheel(0, -300); await page.waitForTimeout(200); }
  await page.waitForTimeout(1000);
  await page.mouse.click(558, 308);
  await expect(page.getByTestId('selected')).toBeVisible();
});
