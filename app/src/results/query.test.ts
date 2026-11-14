import { describe, expect, it } from 'vitest';
import type { Columns } from '../data/types';
import { NO_FILTERS } from '../state/store';
import { queryResults } from './query';

const mk = (): Columns => ({
  rows: 4,
  buffer: new ArrayBuffer(0),
  meta: { flags: { off_market: 0 }, bounds: [0, 0, 1, 1] } as unknown as Columns['meta'],
  scales: {},
  col: {
    land_type: Uint8Array.from([0, 1, 1, 0]),
    x: Float32Array.from([0, 1, 2, 3]), y: Float32Array.from([0, 0, 0, 0]),
    price: Float32Array.from([30, 10, 20, 40]), flags: Uint16Array.from([0, 0, 1, 0]),
    viability: Uint8Array.from([1, 2, 3, 4]), s_power: Uint8Array.from([4, 3, 2, 1]), s_comms: Uint8Array.from([1, 1, 9, 5]),
  } as unknown as Columns['col'],
});

describe('queryResults', () => {
  it('excludes off-market, sorts, caps', () => {
    expect(queryResults(mk(), null, 'price_desc')).toMatchObject({ ids: [3, 0, 1], total: 3 });
    expect(queryResults(mk(), null, 'price_asc', NO_FILTERS, 2)).toMatchObject({ ids: [1, 0], total: 3 });
    expect(queryResults(mk(), null, 'sun_score_desc').ids).toEqual([0, 1, 3]);
    expect(queryResults(mk(), null, 'signal_score_desc').ids).toEqual([3, 0, 1]);
  });
  it('filters by view rect', () => {
    expect(queryResults(mk(), [-1, -1, 1.5, 1], 'price_asc')).toMatchObject({ ids: [1, 0], total: 2 });
  });
  it('applies price range, land type and hideOff', () => {
    const f = { ...NO_FILTERS };
    expect(queryResults(mk(), null, 'price_asc', { ...f, priceMin: 20 }).ids).toEqual([0, 3]);
    expect(queryResults(mk(), null, 'price_asc', { ...f, priceMax: 20 }).ids).toEqual([1]);
    expect(queryResults(mk(), null, 'price_asc', { ...f, landTypes: [1] }).ids).toEqual([1]);
    const withOff = queryResults(mk(), null, 'price_asc', f).passing;
    expect(Array.from(withOff)).toEqual([1, 1, 1, 1]); // off-market plot 2 still drawn on the map
    expect(Array.from(queryResults(mk(), null, 'price_asc', { ...f, hideOff: true }).passing)).toEqual([1, 1, 0, 1]);
    expect(Array.from(queryResults(mk(), null, 'price_asc', { ...f, priceMin: 25 }).passing)).toEqual([1, 0, 0, 1]); // any price bound hides off-market plots (no price)
  });
  it('never mutates the price column (D-6)', () => {
    const c = mk(), before = Array.from(c.col.price);
    queryResults(c, null, 'price_desc', { ...NO_FILTERS, priceMin: 15, landTypes: [0, 1], hideOff: true });
    expect(Array.from(c.col.price)).toEqual(before);
  });
});
