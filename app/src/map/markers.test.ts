import { describe, expect, it } from 'vitest';
import { bandOf, formatPrice, priceBandEdges, visibleIds } from './markers';

describe('markers', () => {
  it('formats prices', () => {
    expect(formatPrice(4200)).toBe('$4.2K'); expect(formatPrice(25000)).toBe('$25K');
    expect(formatPrice(4.2e6)).toBe('$4.2M'); expect(formatPrice(900)).toBe('$900');
  });
  it('bands by quantile', () => {
    const p = Float32Array.from({ length: 100 }, (_, i) => i);
    const e = priceBandEdges(p, Uint32Array.from(p.keys()));
    expect(e.length).toBe(4); expect(bandOf(0, e)).toBe(0); expect(bandOf(99, e)).toBe(4);
  });
  it('culls to view rect and cap', () => {
    const set = { ids: Uint32Array.from([7, 8, 9]), positions: Float32Array.from([0, 0, 5, 5, 1, 1]) };
    expect(visibleIds(set, [-1, -1, 2, 2], 10)).toEqual([7, 9]);
    expect(visibleIds(set, [-1, -1, 9, 9], 1)).toEqual([7]);
  });
});
