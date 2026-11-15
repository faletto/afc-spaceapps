import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { loadConfig, loadDetailTile, loadHorizonTile, loadTier, type Source } from '../data/loader';
import { polarXYToLatLon } from '../geo/projections';
import { plotName } from '../results/homeTypes';
import { rentForStay } from '../science/rent';
import { decodeHorizon } from '../science/visibility';
import { plotRent, siteFromColumns, yearRent } from './plotRent';

const root = new URL('../../public/data/', import.meta.url).pathname;
const src: Source = {
  json: async (p) => JSON.parse(readFileSync(root + p, 'utf8')),
  bin: async (p) => { const b = readFileSync(root + p); return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength) as ArrayBuffer; },
};

async function load() {
  const cols = await loadTier(src, 'polar'), cfg = await loadConfig(src);
  let i = 0;
  while (plotName('polar', cols.col.x[i]!, cols.col.y[i]!) !== 'SP-0172-0148') i++;
  const tpa = cols.meta.tiles_per_axis, tile = cols.col.tile[i]!, row = cols.col.row_in_tile[i]!;
  const det = (await loadDetailTile(src, 'polar', tile, tpa))[row]!;
  const hz = (await loadHorizonTile(src, tile, tpa)).subarray(row * 180, row * 180 + 180);
  const { lat, lon } = polarXYToLatLon(det.best_cell_xy![0], det.best_cell_xy![1]);
  const b = (await src.bin('ephemeris.bin')), n = 8784;
  const f = (k: number, c: number) => new Float32Array(b, k * n * 4, c * n);
  const eph = { sun: f(0, 3), earth: f(3, 3), earthDistM: f(6, 1), tsi: f(7, 1) };
  return { cols, cfg, i, eph, site: siteFromColumns(cols, i, 'polar', lat, lon, decodeHorizon(hz)) };
}

describe('plot rent on real data (demo plot SP-0172-0148)', () => {
  it('reproduces the pipeline demo shift; absolute level includes the plot premium', async () => {
    const { cols, cfg, i, eph, site } = await load();
    const a = plotRent(site, eph, cfg, cols, i, 274, 14), b = plotRent(site, eph, cfg, cols, i, 288, 14);
    // Pipeline golden (premium 0): day 274 → $16,758/mo; day 288 → $7,129/mo (−57%). The premium multiplies both, so compare the shift.
    expect(Math.abs(b.perMonth / a.perMonth / (7129 / 16758) - 1)).toBeLessThan(0.05);
    // Absolute: golden × (1 + premium), where premium = exported yearly rent / premium-free yearly rent (here +75%: Apollo + peak of light).
    const yearNoPremium = rentForStay(site, eph, cfg, cfg.computed.scarcity_viability_cutoff, 1, 366).rent_per_month;
    expect(Math.abs(a.perMonth / (16758 * (a.avg / yearNoPremium)) - 1)).toBeLessThan(0.05);
    // This plot's yearly average is dragged down by dark months, so both stays are above it: no Price cut here.
    expect(a.priceCut).toBe(false);
    expect(a.vsAvg).toBeGreaterThan(0);
  });
  it('a 1-year stay equals the exported yearly rent (RENT-5) and Buy price is untouched', async () => {
    const { cols, cfg, i, eph, site } = await load();
    const price = cols.col.price[i]!;
    const y = plotRent(site, eph, cfg, cols, i, 1, 366);
    expect(Math.abs(y.perMonth / y.avg - 1)).toBeLessThan(1e-9);
    expect(cols.col.price[i]).toBe(price);
  });
  it('stays that run past 31 Dec are clipped', async () => {
    const { cols, cfg, i, eph, site } = await load();
    expect(plotRent(site, eph, cfg, cols, i, 360, 90).stayHours).toBe(8784 - 24 * 359);
  });
  it('scrub budget: a stay recompute fits a 15 fps frame (66 ms) with the year reference cached', async () => {
    const { cols, cfg, i, eph, site } = await load();
    const yr = yearRent(site, eph, cfg);
    for (const stay of [14, 30, 90, 366]) {
      plotRent(site, eph, cfg, cols, i, 1, stay, yr); // warm up
      const t0 = performance.now();
      for (let k = 0; k < 5; k++) plotRent(site, eph, cfg, cols, i, 1 + 20 * k, stay, yr);
      const ms = (performance.now() - t0) / 5;
      console.log(`stay ${stay} d: ${ms.toFixed(1)} ms`);
      if (stay <= 90) expect(ms).toBeLessThan(66);
    }
  });
});
