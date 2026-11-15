import { test, expect } from '@playwright/test';

test('default view is a zoomed-in area (not the whole map) with a local list; buttons switch views', async ({ page }) => {
  await page.setViewportSize({ width: 1400, height: 800 });
  await page.goto('/');
  await page.getByTestId('card').first().waitFor();
  const count = page.getByTestId('count');
  // The list follows the map view, so a local area has far fewer results than the 64,800-plot whole map.
  await expect.poll(async () => Number((await count.textContent())!.match(/([\d,]+) results/)![1]!.replace(/,/g, ''))).toBeLessThan(2000);
  const local = Number((await count.textContent())!.match(/([\d,]+) results/)![1]!.replace(/,/g, ''));
  expect(local).toBeGreaterThan(0);

  await page.getByRole('button', { name: 'Whole map' }).click();
  await expect.poll(async () => Number((await count.textContent())!.match(/([\d,]+) results/)![1]!.replace(/,/g, ''))).toBeGreaterThan(10000);

  await page.getByRole('button', { name: 'Another area' }).click();
  await expect.poll(async () => Number((await count.textContent())!.match(/([\d,]+) results/)![1]!.replace(/,/g, ''))).toBeLessThan(2000);
});

test('?view=fit starts on the whole map', async ({ page }) => {
  await page.goto('/?view=fit');
  await expect(page.getByTestId('count')).toContainText(/\d{2},\d{3} results/);
});
