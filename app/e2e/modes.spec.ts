import { test, expect } from '@playwright/test';


test('?demo=1 scenarios: far-side bargain, Shackleton + 3D Tour', async ({ page }) => {
  await page.setViewportSize({ width: 1400, height: 800 });
  await page.goto('/?demo=1');
  await expect(page.getByTestId('demo-panel')).toBeVisible();
  await page.getByTestId('card').first().waitFor();

  await page.getByTestId('demo-far-side').click();
  await expect(page.getByRole('article', { name: 'Listing' })).toBeVisible();
  await expect(page.getByTestId('listing-title')).toContainText(/Plot G-/);

  await page.getByRole('button', { name: '← Back to results' }).click();
  await page.getByTestId('demo-shackleton').click();
  await expect(page.getByRole('article', { name: 'Listing' })).toBeVisible();
  await expect(page.getByTestId('tour-canvas')).toBeVisible();
  await expect(page.getByTestId('nearby')).toContainText(/Shackleton/);

  await expect(page.getByTestId('demo-rent')).toHaveCount(0);
});

test('demo panel is absent without ?demo=1', async ({ page }) => {
  await page.goto('/');
  await page.getByTestId('card').first().waitFor();
  await expect(page.getByTestId('demo-panel')).toHaveCount(0);
});

test('?present=1: presentation layout hides dev controls', async ({ page }) => {
  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.goto('/?present=1');
  await page.getByTestId('card').first().waitFor();
  await expect(page.locator('[data-mode="present"]')).toHaveCount(1);
  await page.getByRole('combobox', { name: 'Overlay' }).selectOption('sunlit');
  await expect(page.getByRole('combobox', { name: 'Overlay' })).toHaveValue('sunlit');
  await expect(page.getByLabel('Overlay opacity')).toHaveCount(0);
});

test('About dialog: datasets, formulas with sources, validation; Escape closes', async ({ page }) => {
  await page.goto('/');
  await page.getByTestId('card').first().waitFor();
  await page.getByRole('button', { name: 'About' }).click();
  const dlg = page.getByRole('dialog', { name: /About Lunar Listings/ });
  await expect(dlg).toContainText('JPL Horizons');
  await dlg.getByRole('tab', { name: 'Formulas' }).click();
  await expect(page.getByTestId('formulas')).toContainText('Sunlight');
  await expect(page.getByTestId('formulas')).toContainText('Source:');
  await dlg.getByRole('tab', { name: 'Validation' }).click();
  await expect(dlg).toContainText('Horizons');
  await page.keyboard.press('Escape');
  await expect(dlg).toHaveCount(0);
});

test('offline: every request stays on the local origin (no live APIs)', async ({ page, baseURL }) => {
  const origin = new URL(baseURL!).origin;
  const foreign: string[] = [];
  page.on('request', (r) => { const u = r.url(); if (!u.startsWith(origin) && !u.startsWith('data:') && !u.startsWith('blob:')) foreign.push(u); });
  await page.goto('/?demo=1');
  await page.getByTestId('card').first().waitFor();
  await page.getByTestId('demo-shackleton').click();
  await page.getByTestId('tour-canvas').waitFor();
  expect(foreign).toEqual([]);
});
