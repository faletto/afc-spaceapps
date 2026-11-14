import { test, expect } from '@playwright/test';

test('3D Tour: polar listing has a tour tab with panorama + countdowns; Moon-wide has none', async ({ page }) => {
  await page.setViewportSize({ width: 1400, height: 800 });
  await page.goto('/');
  await page.getByTestId('card').first().click();
  await expect(page.getByRole('article', { name: 'Listing' })).toBeVisible();
  await expect(page.getByRole('tab', { name: '3D Tour' })).toHaveCount(0);
  await page.getByRole('button', { name: '← Back to results' }).click();
  await page.getByRole('button', { name: 'South Pole District' }).click();
  await page.getByTestId('card').first().click();
  await page.getByRole('tab', { name: '3D Tour' }).click();
  await expect(page.getByTestId('tour-canvas')).toBeVisible();
  await expect(page.getByTestId('tour-sun')).toContainText(/Sun (sets|rises|stays)/);
  await expect(page.getByTestId('tour-earth')).toContainText(/Earth (sets|rises|stays)/);
});
