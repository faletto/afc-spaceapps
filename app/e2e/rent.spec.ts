import { test as base, expect } from '@playwright/test';
import { RENT_ENABLED } from '../src/features';

const test = RENT_ENABLED ? base : base.skip;

const money = (s: string | null) => s!.replace(/[^0-9.KMB]/g, '');

test('Rent tab: move-in changes the rent, never the Buy price; tour follows the slider; history chart', async ({ page }) => {
  await page.setViewportSize({ width: 1400, height: 800 });
  await page.goto('/');
  await page.getByRole('button', { name: 'South Pole District' }).click();
  await page.getByRole('tab', { name: 'Rent' }).click();
  await page.getByTestId('card').first().waitFor();
  await expect(page.getByTestId('card').first()).toContainText('/mo');
  await page.getByTestId('card').first().click();
  const buy = money(await page.getByTestId('listing-price').textContent());

  await expect(page.getByTestId('listing-rent')).toBeVisible();
  const slider = page.getByRole('slider', { name: 'Time' });
  await slider.fill(String(24 * 273));
  await expect(page.getByTestId('time-label')).toContainText('Move-in');
  await expect.poll(async () => money(await page.getByTestId('listing-rent').textContent())).not.toBe('');
  const rents = new Set<string>();
  for (const day of [10, 100, 200, 288, 340]) {
    await slider.fill(String(24 * (day - 1)));
    await expect(page.getByTestId('time-label')).toContainText(/\d{4}/);
    await page.waitForTimeout(1200); // rent is a deferred value; give it time under software GL
    rents.add(money(await page.getByTestId('listing-rent').textContent()));
    expect(money(await page.getByTestId('listing-price').textContent())).toBe(buy); // D-6
  }
  expect(rents.size).toBeGreaterThan(1); // rent responds to the move-in date

  await slider.fill('0');
  await page.getByLabel('Stay length').selectOption({ label: '1 year' });
  await expect(page.getByTestId('rent-total')).toContainText('366-day');

  // 3D Tour follows the same slider (TIME-2).
  await expect(page.getByTestId('tour-sun')).toContainText(/Sun (sets|rises|stays)/);
  const before = await page.getByTestId('tour-sun').textContent();
  await slider.fill(String(24 * 40));
  await expect.poll(async () => page.getByTestId('tour-sun').textContent()).not.toBe(before);

  // Back to Buy: Buy price still unchanged.
  await page.getByRole('tab', { name: 'Buy' }).click();
  await expect(page.getByTestId('rent-block')).toHaveCount(0);
  expect(money(await page.getByTestId('listing-price').textContent())).toBe(buy);
});
