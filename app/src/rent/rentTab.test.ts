import { describe, expect, it } from 'vitest';
import type { Columns } from '../data/types';
import { NO_FILTERS, useStore } from '../state/store';
import { priceCol, queryResults } from '../results/query';
import { MONTH_START_DAY, siteFromColumns } from './plotRent';

const tiny = (): Columns => ({
  rows: 3, buffer: new ArrayBuffer(0), scales: { ice_km10: 0.1 },
  meta: { flags: { off_market: 0 }, land_types: ['highlands'], bounds: [0, 0, 1, 1] } as unknown as Columns['meta'],
  col: {
    price: Float32Array.from([1_000_000, 2_000_000, 3_000_000]), rent_avg: Float32Array.from([30, 10, 20]), viability: Uint8Array.from([1, 2, 3]),
    flags: new Uint16Array(3), land_type: new Uint8Array(3), x: Float32Array.from([10.5, 20.5, 30.5]), y: Float32Array.from([-5.5, 0.5, 5.5]),
    s_safety: Uint8Array.from([80, 80, 80]), s_landmark: Uint8Array.from([50, 0, 0]), ice_km10: Uint16Array.from([65535, 65535, 65535]),
    s_power: new Uint8Array(3), s_comms: new Uint8Array(3),
  } as unknown as Columns['col'],
});

describe('Rent tab data', () => {
  it('price filter and sort use rent_avg on Rent, price on Buy', () => {
    const c = tiny();
    expect(priceCol(c, 'rent')).toBe(c.col.rent_avg);
    expect(queryResults(c, null, 'price_desc', NO_FILTERS, 200, null, 'global', 'buy').ids).toEqual([2, 1, 0]);
    expect(queryResults(c, null, 'price_desc', NO_FILTERS, 200, null, 'global', 'rent').ids).toEqual([0, 2, 1]);
    const f = { ...NO_FILTERS, priceMax: 25 };
    expect(queryResults(c, null, 'price_asc', f, 200, null, 'global', 'rent').ids).toEqual([1, 2]);
    expect(queryResults(c, null, 'price_asc', f, 200, null, 'global', 'buy').total).toBe(0);
  });
  it('switching tabs clears price bounds (different units) but keeps other filters', () => {
    useStore.getState().setFilters({ priceMax: 5_000_000, hideOff: true });
    useStore.getState().setTab('rent');
    const f = useStore.getState().filters;
    expect(f.priceMax).toBeNull();
    expect(f.hideOff).toBe(true);
    useStore.getState().resetFilters(); useStore.getState().setTab('buy');
  });
  it('Moon-wide sites use the plot centre and a smooth horizon', () => {
    const s = siteFromColumns(tiny(), 0, 'global', -5.5, 10.5, null);
    expect(s).toMatchObject({ lat: -5.5, lon: 10.5, horizon_deg: null, ice_km: null, landing_safe: true });
    expect(s.hazard_score).toBeCloseTo(0.2, 9);
    expect(s.landmark_score).toBeCloseTo(0.5, 9);
  });
  it('month start days are real 2028 calendar days', () => {
    MONTH_START_DAY.forEach((d, m) => {
      const date = new Date(Date.UTC(2028, 0, 1 + d - 1));
      expect([date.getUTCMonth(), date.getUTCDate()]).toEqual([m, 1]);
    });
  });
});
