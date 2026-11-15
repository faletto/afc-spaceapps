import { test, expect } from '@playwright/test';

test('map loads both tiers', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('/?view=fit');
  await expect(page.locator('canvas').first()).toBeVisible();
  await page.getByRole('button', { name: 'South Pole District' }).click();
  await expect(page.locator('canvas').first()).toBeVisible();
  await page.waitForTimeout(500);
  expect(errors).toEqual([]);
});

test('zooming shows pills and clicking one selects a plot', async ({ page }) => {
  await page.setViewportSize({ width: 1200, height: 700 });
  await page.goto('/?view=fit');
  await page.getByTestId('card').first().waitFor();
  await page.waitForTimeout(4000); // software GL needs time after heavier tests have run before it
  await page.mouse.move(384, 350);
  for (let i = 0; i < 7; i++) { await page.mouse.wheel(0, -300); await page.waitForTimeout(300); } // ~0.9 zoom per step: plots end up ≈ 200 px, pills on
  await page.waitForTimeout(2000);
  // Layout-independent: zoom is anchored at the pointer, so a pill/dot is within ~100 px of it. Try points outward from there;
  // a click selects the hovered plot and does nothing on empty map, so click until something is selected.
  const pts: [number, number][] = [];
  for (let dy = -112; dy <= 112; dy += 16) for (let dx = -112; dx <= 112; dx += 16) pts.push([384 + dx, 350 + dy]);
  pts.sort((p, q) => Math.hypot(p[0] - 384, p[1] - 350) - Math.hypot(q[0] - 384, q[1] - 350));
  for (const [x, y] of pts) {
    await page.mouse.move(x, y);
    await page.waitForTimeout(90);
    await page.mouse.click(x, y);
    await page.waitForTimeout(90);
    if (await page.getByTestId('selected').count()) break;
  }
  await expect(page.getByTestId('selected')).toBeVisible();
});

test('results list is capped, hover highlights, click selects', async ({ page }) => {
  await page.setViewportSize({ width: 1400, height: 800 });
  await page.goto('/?view=fit');
  const count = page.getByTestId('count');
  await expect(count).toContainText('results');
  await expect(count).toContainText('Showing 200 of');
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
  await page.goto('/?view=fit');
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
  await page.goto('/?view=fit');
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
  await page.goto('/?view=fit');
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
  await page.goto('/?view=fit');
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
  await page.goto('/?view=fit');
  await page.getByTestId('card').first().click();
  const term = page.locator('[data-term="sunlight"]').first();
  await term.focus();
  // Text comes from data/glossary.json (pipeline), including its formula and source.
  await expect(page.getByRole('tooltip')).toContainText('visible fraction of the solar disk');
  await expect(page.getByRole('tooltip')).toContainText('Source: Horizons ephemeris');
  await page.keyboard.press('Escape');
  await expect(page.getByRole('tooltip')).toHaveCount(0);
  await expect(page.getByRole('article', { name: 'Listing' })).toBeVisible();
});

test('filters: price range narrows list + map count, land type, hide off-market, clear', async ({ page }) => {
  const errors: string[] = [];
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  await page.setViewportSize({ width: 1400, height: 800 });
  await page.goto('/?view=fit');
  const count = page.getByTestId('count');
  const match = page.getByTestId('match-count');
  await expect(count).toContainText('Showing 200 of');
  const all = (await match.textContent())!;
  const countAll = await count.textContent();

  await page.getByLabel('Min price').fill('30k');
  await expect(match).not.toHaveText(all);
  expect(Number((await match.textContent())!.replace(/\D/g, ''))).toBeLessThan(Number(all.replace(/\D/g, '')));
  await expect(count).not.toHaveText(countAll!);
  await page.getByRole('combobox', { name: /Sort/ }).selectOption('price_asc');
  // cheapest remaining card must be >= $30K
  await expect(page.getByTestId('card').first()).toContainText(/\$(3\d|[4-9]\d)(\.\d)?K|\$\d(\.\d)?M/);

  await page.getByLabel('Max price').fill('abc');
  await expect(page.getByLabel('Max price')).toHaveAttribute('aria-invalid', 'true');

  await page.getByRole('button', { name: 'Clear filters' }).click();
  await expect(match).toHaveText(all);
  await expect(page.getByLabel('Min price')).toHaveValue('');

  await page.getByText('Land type').click();
  await page.getByLabel('Mare').check();
  await expect(match).not.toHaveText(all);
  await page.getByLabel('Mare').uncheck();
  await expect(match).toHaveText(all);

  await page.getByLabel('Hide off-market plots').check();
  await expect(match).not.toHaveText(all);
  expect(errors).toEqual([]);
});

test('D-6: Buy price never changes with filters, sort, overlay, tier, selection', async ({ page }) => {
  await page.setViewportSize({ width: 1400, height: 800 });
  await page.goto('/?view=fit');
  const cardFor = (id: string) => page.locator(`[data-testid="card"][data-plot="${id}"]`);
  const priceIn = async (id: string) => (await cardFor(id).locator('div >> text=/^\\$/').first().textContent())!;

  await expect(page.getByTestId('card').first()).toBeVisible();
  const top = page.getByTestId('card').first();
  const id = (await top.getAttribute('data-plot'))!;
  const price = await priceIn(id);

  const listingPrice = async () => {
    await cardFor(id).click();
    const t = (await page.getByTestId('listing-price').textContent())!;
    await page.getByRole('button', { name: '← Back to results' }).click();
    await expect(page.getByRole('article', { name: 'Listing' })).toHaveCount(0);
    return t;
  };
  expect(await listingPrice()).toContain(price);

  // Overlay + opacity.
  await page.getByRole('combobox', { name: 'Overlay' }).selectOption('viability');
  await page.getByRole('slider', { name: 'Overlay opacity' }).fill('0.2');
  await expect(cardFor(id)).toBeVisible();
  expect(await priceIn(id)).toBe(price);

  // Filters that keep the plot, plus a land-type round trip.
  // A price filter that really excludes most plots but keeps this one: min = 90% of its displayed price.
  const shown = Number(/\$(\d+(?:\.\d+)?)([KM])/.exec(price)!.slice(1, 2)[0]) * (price.includes('M') ? 1000 : 1);
  await page.getByLabel('Min price').fill(`${Math.floor(shown * 0.9)}k`);
  await expect(page.getByTestId('match-count')).not.toHaveText('64,800 plots match');
  await page.getByText('Land type').click();
  await page.getByLabel('Mare').check();
  await page.getByLabel('Mare').uncheck();
  await page.getByLabel('Hide off-market plots').check();
  await expect(cardFor(id)).toBeVisible();
  expect(await priceIn(id)).toBe(price);

  // Sort round trip.
  const sort = page.getByRole('combobox', { name: /Sort/ });
  await sort.selectOption('viability_desc');
  await sort.selectOption('price_desc');
  await expect(cardFor(id)).toBeVisible();
  expect(await priceIn(id)).toBe(price);
  expect(await listingPrice()).toContain(price);

  // Tier round trip.
  await page.getByRole('button', { name: 'South Pole District' }).click();
  await expect(page.getByTestId('count')).toContainText('results');
  await page.getByRole('button', { name: 'Moon-wide' }).click();
  await expect(cardFor(id)).toBeVisible();
  expect(await priceIn(id)).toBe(price);
  expect(await listingPrice()).toContain(price);
  // TODO(A6): add the Rent tab / move-in / stay / time slider to this test once they exist.
});

test('clicking a dot at the default Moon-wide zoom selects its plot and opens the listing', async ({ page }) => {
  await page.setViewportSize({ width: 1400, height: 800 });
  await page.goto('/?view=fit');
  await page.getByTestId('card').first().waitFor();
  await page.locator('canvas').first().waitFor();
  await page.waitForTimeout(1500);
  const box = (await page.locator('canvas').first().boundingBox())!;
  const s = Math.min(box.width / 360, box.height / 180); // fit scale (px per degree)
  // Plot centres are on half-degree grid points; (-100.5, 20.5) is an on-market plot in the stub-free real data.
  const x = box.x + box.width / 2 - 100.5 * s, y = box.y + box.height / 2 - 20.5 * s;
  await page.mouse.move(x - 6, y - 6);
  await page.mouse.move(x, y, { steps: 4 });
  await page.waitForTimeout(500); // let hover picking settle
  await page.mouse.click(x, y);
  await expect(page.getByTestId('selected')).toBeVisible();
  await expect(page.getByRole('article', { name: 'Listing' })).toBeVisible();
});

test('panning the map does not select a plot', async ({ page }) => {
  await page.setViewportSize({ width: 1400, height: 800 });
  await page.goto('/?view=fit');
  await page.locator('canvas').first().waitFor();
  await page.waitForTimeout(1500);
  const box = (await page.locator('canvas').first().boundingBox())!;
  const x = box.x + box.width / 2, y = box.y + box.height / 2;
  await page.mouse.move(x, y); await page.waitForTimeout(300);
  await page.mouse.down(); await page.mouse.move(x + 60, y + 20, { steps: 6 }); await page.mouse.up();
  await page.waitForTimeout(500);
  await expect(page.getByTestId('selected')).toHaveCount(0);
});

test('each basemap file downloads once; listing shows why, blurb and nearest feature', async ({ page }) => {
  const seen: Record<string, number> = {};
  page.on('request', (r) => { const m = /basemap(_small)?\.jpg$/.exec(r.url()); if (m) seen[m[0]] = (seen[m[0]] ?? 0) + 1; });
  await page.setViewportSize({ width: 1400, height: 800 });
  await page.goto('/?view=fit');
  await page.getByTestId('card').first().click();
  await expect(page.getByTestId('why')).toContainText('Priced');
  await expect(page.getByTestId('blurb')).not.toBeEmpty();
  await expect(page.getByTestId('nearby')).toContainText('Nearest feature:');
  await expect(page.getByTestId('nearby')).toContainText('km');
  await page.waitForTimeout(3000); // let the full basemap finish
  expect(seen['basemap_small.jpg']).toBe(1);
  expect(seen['basemap.jpg']).toBe(1);
});
