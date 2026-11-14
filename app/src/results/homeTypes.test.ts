import { existsSync, readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { loadTier, type Source } from '../data/loader';
import { NO_FILTERS } from '../state/store';
import { HOME_TYPES, matchPct, plotName, type HomeCfg, type HomeType } from './homeTypes';
import { queryResults } from './query';

const root = new URL('../../public/data/', import.meta.url).pathname;
const src: Source = {
  json: async (p) => JSON.parse(readFileSync(root + p, 'utf8')),
  bin: async (p) => { const b = readFileSync(root + p); return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength) as ArrayBuffer; },
};

describe('plotName', () => {
  it('matches the pipeline ids', () => {
    expect(plotName('global', 0.5, 0.5)).toBe('G-090-180');
    expect(plotName('polar', 120, 18840)).toBe('SP-0140-0160'); // best cell of SP-0140-0160 in polar/detail/8_8.json
  });
});

describe.skipIf(!existsSync(root + 'manifest.json'))('home types on real data', () => {
  const cfg = (JSON.parse(readFileSync(root + 'config.json', 'utf8')) as { home_types: HomeCfg }).home_types;
  it('every type returns ≥ 50 polar plots (calibration rule), never changing prices', async () => {
    const c = await loadTier(src, 'polar');
    const base = queryResults(c, null, 'price_desc', NO_FILTERS, 5);
    for (const [t] of HOME_TYPES.filter(([k]) => k !== 'any')) {
      const r = queryResults(c, null, 'best_match', { ...NO_FILTERS, homeType: t as HomeType }, 200, cfg, 'polar');
      expect(r.total, t).toBeGreaterThanOrEqual(50);
      expect(r.match.length).toBe(r.ids.length);
      for (let k = 1; k < r.match.length; k++) expect(r.match[k]!).toBeLessThanOrEqual(r.match[k - 1]!);
      for (const i of r.ids) expect(matchPct(c, i, t as HomeType, cfg)).toBeLessThanOrEqual(100);
    }
    expect(queryResults(c, null, 'price_desc', NO_FILTERS, 5).ids).toEqual(base.ids); // D-6
  });
  it('ice depot is polar-only', async () => {
    const g = await loadTier(src, 'global');
    expect(queryResults(g, null, 'best_match', { ...NO_FILTERS, homeType: 'ice_depot' }, 200, cfg, 'global').total).toBe(0);
  });
  it('min sunlight filter', async () => {
    const c = await loadTier(src, 'polar');
    const r = queryResults(c, null, 'price_desc', { ...NO_FILTERS, minSun: 80 });
    for (const i of r.ids) expect(c.col.sunlit_pct[i]!).toBeGreaterThanOrEqual(80);
    expect(r.total).toBeLessThan(queryResults(c, null, 'price_desc').total);
  });
});
