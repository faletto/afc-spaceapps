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
  await page.mouse.move(384, 350);
  for (let i = 0; i < 5; i++) { await page.mouse.wheel(0, -300); await page.waitForTimeout(200); }
  await page.waitForTimeout(1000);
  await page.mouse.click(465, 323);
  await expect(page.getByTestId('selected')).toBeVisible();
});

test('results list is capped, hover highlights, click selects', async ({ page }) => {
  await page.setViewportSize({ width: 1400, height: 800 });
  await page.goto('/');
  const count = page.getByTestId('count');
  await expect(count).toContainText('results');
  await expect(count).toContainText('showing 200');
  const n = await page.getByTestId('card').count();
  expect(n).toBeGreaterThan(0);
  expect(n).toBeLessThanOrEqual(200);
  const card = page.getByTestId('card').first();
  const plot = await card.getAttribute('data-plot');
  await card.click();
  await expect(page.getByTestId('selected')).toHaveText('Selected plot #' + plot);
});

test('list follows the map view and sort', async ({ page }) => {
  await page.setViewportSize({ width: 1400, height: 800 });
  await page.goto('/');
  await page.waitForTimeout(1500);
  const text = async () => (await page.getByTestId('count').textContent())!;
  const before = await text();
  await page.mouse.move(400, 400);
  for (let i = 0; i < 4; i++) { await page.mouse.wheel(0, -300); await page.waitForTimeout(150); }
  await page.waitForTimeout(800);
  expect(await text()).not.toBe(before);
  await page.getByRole('combobox', { name: /Sort/ }).selectOption('price_asc');
  const first = await page.getByTestId('card').first().textContent();
  expect(first).toContain('$');
});

test('card opens listing, back returns to results (state kept)', async ({ page }) => {
  await page.setViewportSize({ width: 1400, height: 800 });
  await page.goto('/');
  await expect(page.getByTestId('count')).toContainText('results');
  // Sorting runs in the worker, so wait for the list to actually re-sort before reading a card.
  const firstPrice = page.getByTestId('card').first().locator('div >> text=/^\\$/').first();
  await expect(firstPrice).toBeVisible();
  const descTop = await firstPrice.textContent();
  await page.getByRole('combobox', { name: /Sort/ }).selectOption('price_asc');
  await expect(firstPrice).not.toHaveText(descTop!);
  const countBefore = await page.getByTestId('count').textContent();
  const card = page.getByTestId('card').first();
  const plot = await card.getAttribute('data-plot');
  const priceText = (await card.locator('div >> text=/^\\$/').first().textContent())!;

  await card.click();
  await expect(page.getByRole('article', { name: 'Listing' })).toBeVisible();
  await expect(page.getByTestId('listing-price')).toContainText(priceText);
  await expect(page.getByTestId('viability')).toBeVisible();
  await expect(page.getByTestId('fineprint').first()).toBeVisible();
  await expect(page.getByTestId('card')).toHaveCount(0);
  await expect(page.getByTestId('selected')).toHaveText('Selected plot #' + plot);

  await page.getByRole('button', { name: '← Back to results' }).click();
  await expect(page.getByRole('article', { name: 'Listing' })).toHaveCount(0);
  await expect(page.getByTestId('count')).toHaveText(countBefore!);
  await expect(page.getByRole('combobox', { name: /Sort/ })).toHaveValue('price_asc');
  await expect(page.getByTestId('selected')).toHaveCount(0);
});

test('Escape closes the listing; notice is dismissible', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByTestId('notice')).toBeVisible();
  await page.getByRole('button', { name: 'Got it' }).click();
  await expect(page.getByTestId('notice')).toHaveCount(0);
  await page.reload();
  await expect(page.getByTestId('notice')).toHaveCount(0);
  await page.getByTestId('card').first().click();
  await expect(page.getByRole('article', { name: 'Listing' })).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.getByTestId('card').first()).toBeVisible();
});

test('overlay: select shows legend with unit/range, opacity works, ice is polar-only', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text())); // deck.gl logs layer errors here
  await page.setViewportSize({ width: 1400, height: 800 });
  await page.goto('/');
  const sel = page.getByRole('combobox', { name: 'Overlay' });
  await expect(page.getByTestId('legend')).toHaveCount(0);
  await expect(sel.locator('option[value="ice"]')).toHaveCount(0);
  await sel.selectOption('sunlit');
  const legend = page.getByTestId('legend');
  await expect(legend).toContainText('Sunlight');
  await expect(legend).toContainText('(%)');
  await expect(legend).toContainText('100');
  await page.getByRole('slider', { name: 'Overlay opacity' }).fill('0.3');
  await page.getByRole('button', { name: 'South Pole District' }).click();
  await expect(sel.locator('option[value="ice"]')).toHaveCount(1);
  await sel.selectOption('ice');
  await expect(legend).toContainText('Ice access');
  await sel.selectOption('');
  await expect(legend).toHaveCount(0);
  await page.waitForTimeout(300);
  expect(errors).toEqual([]);
});

test('glossary tooltip opens on focus and closes on Escape without closing the listing', async ({ page }) => {
  await page.goto('/');
  await page.getByTestId('card').first().click();
  const term = page.locator('[data-term="sunlight"]');
  await term.focus();
  await expect(page.getByRole('tooltip')).toContainText('Sun is above');
  await page.keyboard.press('Escape');
  await expect(page.getByRole('tooltip')).toHaveCount(0);
  await expect(page.getByRole('article', { name: 'Listing' })).toBeVisible();
});
