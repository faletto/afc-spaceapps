import { describe, expect, it } from 'vitest';
import type { Columns } from '../data/types';
import { queryResults } from './query';

const mk = (): Columns => ({
  rows: 4,
  meta: { flags: { off_market: 0 }, bounds: [0, 0, 1, 1] } as unknown as Columns['meta'],
  scales: {},
  col: {
    x: Float32Array.from([0, 1, 2, 3]), y: Float32Array.from([0, 0, 0, 0]),
    price: Float32Array.from([30, 10, 20, 40]), flags: Uint16Array.from([0, 0, 1, 0]),
    viability: Uint8Array.from([1, 2, 3, 4]), sunlit_pct: Uint8Array.from([4, 3, 2, 1]),
  } as unknown as Columns['col'],
});

describe('queryResults', () => {
  it('excludes off-market, sorts, caps', () => {
    expect(queryResults(mk(), null, 'price_desc')).toEqual({ ids: [3, 0, 1], total: 3 });
    expect(queryResults(mk(), null, 'price_asc', 2)).toEqual({ ids: [1, 0], total: 3 });
    expect(queryResults(mk(), null, 'sunlit_desc').ids).toEqual([0, 1, 3]);
  });
  it('filters by view rect', () => {
    expect(queryResults(mk(), [-1, -1, 1.5, 1], 'price_asc')).toEqual({ ids: [1, 0], total: 2 });
  });
});
