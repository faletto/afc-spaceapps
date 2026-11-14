import { describe, expect, it } from 'vitest';
import type { Columns } from '../data/types';
import { badgeLabels } from '../listing/Badges';
import { NO_FILTERS, useStore } from '../state/store';
import { matchPct, passesHome, type HomeCfg } from './homeTypes';
import { pickFeatured } from './PlotsForYou';
import { queryResults } from './query';

const cfg = {
  lander_pad: { gates: { longest_night_h: 48 }, weights: { power: 0.35, safety: 0.4 } },
  habitat: { gates: { longest_blackout_h: 168 }, weights: { comms: 0.35, thermal: 0.25 } },
  solar_farm: { gates: { safe_area_frac: 0.4, sunlit_frac: 0.6 }, weights: { power: 0.6 } },
  ice_depot: { gates: { ice_km: 2 }, weights: { ice: 0.45, power: 0.25 }, polar_only: true },
} as HomeCfg;

const tiny = (): Columns => ({
  rows: 3, buffer: new ArrayBuffer(0), scales: { ice_km10: 0.1 },
  meta: { flags: { off_market: 0, hot_property: 1, earth_view: 3, featured: 4 }, land_types: ['highlands', 'peak_of_light'], bounds: [0, 0, 1, 1] } as unknown as Columns['meta'],
  col: {
    bw_lander_h: Uint16Array.from([48, 49, 0]), bw_habitat_h: Uint16Array.from([168, 169, 0]), sunlit_pct: Uint8Array.from([60, 59, 100]),
    ice_km10: Uint16Array.from([20, 21, 65535]), s_safety: Uint8Array.from([100, 0, 50]), s_power: Uint8Array.from([0, 0, 50]),
    s_comms: Uint8Array.from([0, 0, 0]), s_thermal: Uint8Array.from([0, 0, 0]), s_landmark: Uint8Array.from([0, 0, 0]), s_ice: Uint8Array.from([0, 0, 0]),
    viability: Uint8Array.from([10, 20, 30]), price: Float32Array.from([30, 10, 20]), land_type: Uint8Array.from([0, 1, 0]),
    flags: Uint16Array.from([(1 << 1) | (1 << 3) | (1 << 4), 1 << 4, 1 << 0]), x: Float32Array.from([0, 1, 2]), y: Float32Array.from([0, 0, 0]),
  } as unknown as Columns['col'],
});

describe('home-type gates and match %', () => {
  const c = tiny();
  it('gates at their boundaries (lander 48 h, habitat 168 h, solar 60 %, ice 2.0 km, n/a)', () => {
    expect([0, 1].map((i) => passesHome(c, i, 'lander_pad', cfg, 'polar'))).toEqual([true, false]);
    expect([0, 1].map((i) => passesHome(c, i, 'habitat', cfg, 'polar'))).toEqual([true, false]);
    expect([0, 1].map((i) => passesHome(c, i, 'solar_farm', cfg, 'polar'))).toEqual([true, false]);
    expect([0, 1, 2].map((i) => passesHome(c, i, 'ice_depot', cfg, 'polar'))).toEqual([true, false, false]);
    expect(passesHome(c, 0, 'ice_depot', cfg, 'global')).toBe(false);
  });
  it('match % is the weighted mean of the listed weights (hand-computed)', () => {
    expect(matchPct(c, 2, 'lander_pad', cfg)).toBeCloseTo(50, 9); // (0.35·50 + 0.4·50) / 0.75
    expect(matchPct(c, 0, 'lander_pad', cfg)).toBeCloseTo(53.3333333, 6); // (0.35·0 + 0.4·100) / 0.75
    expect(matchPct(c, 1, 'any', cfg)).toBe(20);
  });
  it('passing mask ignores the rect and applies the gate; prices are untouched (D-6)', () => {
    const before = Array.from(c.col.price);
    const r = queryResults(c, [10, 10, 11, 11], 'best_match', { ...NO_FILTERS, homeType: 'lander_pad' }, 200, cfg, 'polar');
    expect(Array.from(r.passing)).toEqual([1, 0, 0]);
    expect(r.ids).toEqual([]);
    expect(Array.from(c.col.price)).toEqual(before);
  });
});

describe('badges, featured, store', () => {
  const c = tiny();
  it('badge order, max cap, no price_cut', () => {
    expect(badgeLabels(c, 0)).toEqual(['Hot property', 'Earth view']);
    expect(badgeLabels(c, 0, 1)).toEqual(['Hot property']);
    expect(badgeLabels(c, 1)).toEqual(['Peak of light']);
    expect(badgeLabels(c, 2)).toEqual(['Off market']);
  });
  it('pickFeatured: best viability + cheapest, never off-market', () => {
    const f = pickFeatured(c);
    expect(f[0]).toBe(1); // viability 20 > 10
    expect(f).toContain(0);
    expect(f).not.toContain(2);
  });
  it('setHomeType / resetFilters manage the best_match sort', () => {
    useStore.getState().setSort('price_asc');
    useStore.getState().setHomeType('habitat');
    expect(useStore.getState().sort).toBe('best_match');
    useStore.getState().setHomeType('any');
    expect(useStore.getState().sort).toBe('viability_desc');
    useStore.getState().setSort('price_asc');
    useStore.getState().setHomeType('any');
    expect(useStore.getState().sort).toBe('price_asc');
    useStore.getState().setHomeType('lander_pad');
    useStore.getState().resetFilters();
    expect(useStore.getState().sort).toBe('viability_desc');
  });
});
