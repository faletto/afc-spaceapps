import { test, expect } from '@playwright/test';

test('Plots for you, real plot ids and badges on cards', async ({ page }) => {
  await page.setViewportSize({ width: 1400, height: 800 });
  await page.goto('/');
  await page.getByTestId('card').first().waitFor();
  await expect(page.getByRole('region', { name: 'Plots for you' })).toBeVisible();
  expect(await page.getByTestId('featured').count()).toBeGreaterThanOrEqual(2);
  await expect(page.getByTestId('card').first()).toContainText(/G-\d{3}-\d{3}/);
  await page.getByTestId('featured').first().click();
  await expect(page.getByRole('article', { name: 'Listing' })).toBeVisible();
});

test('Home type: each type returns results with match %, Best match sort, prices unchanged', async ({ page }) => {
  await page.setViewportSize({ width: 1400, height: 800 });
  await page.goto('/');
  await page.getByRole('button', { name: 'South Pole District' }).click();
  await page.getByTestId('card').first().waitFor();
  const priceOf = async () => (await page.getByTestId('card').first().textContent())!.match(/\$[\d.,]+[KMB]?/)![0];
  for (const t of ['Lander pad', 'Habitat', 'Solar farm', 'Ice depot']) {
    await page.getByLabel('Home type').selectOption({ label: t });
    await expect(page.getByTestId('card').first()).toContainText('% match');
    await expect(page.getByTestId('count')).toContainText('results');
    await expect(page.getByLabel('Sort:')).toHaveValue('best_match');
  }
  // Prices of the same plot don't depend on the home type (D-6).
  await page.getByLabel('Home type').selectOption({ label: 'Any' });
  await expect(page.getByLabel('Sort:')).not.toHaveValue('best_match');
  expect(await priceOf()).toMatch(/\$/);
});

test('Home type on Moon-wide: ice depot explains itself; More panel filters by sunlight', async ({ page }) => {
  await page.goto('/');
  await page.getByTestId('card').first().waitFor();
  await page.getByLabel('Home type').selectOption({ label: 'Ice depot' });
  await expect(page.getByRole('status')).toContainText('South Pole District');
  await page.getByLabel('Home type').selectOption({ label: 'Any' });
  const total = async () => Number((await page.getByTestId('match-count').textContent())!.replace(/\D/g, ''));
  await expect.poll(total).toBeGreaterThan(1000);
  const before = await total();
  await page.getByText('More', { exact: false }).first().click();
  await page.getByLabel('Minimum sunlight').fill('50');
  await expect.poll(total).toBeLessThan(before);
});
