import type { Columns } from '../data/types';

export const FLAG_OFF_MARKET = 0;
export const isOffMarket = (c: Columns, i: number) => ((c.col.flags[i]! >> (c.meta.flags.off_market ?? FLAG_OFF_MARKET)) & 1) === 1;

/** Sequential price-band ramp (cheap → pricey). Not color-only: off-market uses a different shape. */
export const BAND_COLORS: [number, number, number][] = [
  [94, 196, 160], [140, 210, 110], [240, 210, 80], [244, 140, 60], [220, 70, 80],
];

/** Price band edges = quantiles of on-market prices (data-independent of absolute scale). */
export function priceBandEdges(prices: ArrayLike<number>, onMarket: Uint32Array, bands = BAND_COLORS.length): number[] {
  const v = Float32Array.from(onMarket, (i) => prices[i]!).sort();
  const edges: number[] = [];
  for (let b = 1; b < bands; b++) edges.push(v[Math.floor((b * v.length) / bands)] ?? 0);
  return edges;
}
export const bandOf = (p: number, edges: number[]) => { let b = 0; while (b < edges.length && p >= edges[b]!) b++; return b; };

const UNITS = [[1e3, 'K'], [1e6, 'M'], [1e9, 'B']] as const;
export function formatPrice(p: number): string {
  if (p < 1e3) return `$${Math.round(p)}`;
  for (const [k, [div, unit]] of UNITS.entries()) {
    const v = p / div;
    const text = v >= 10 ? String(Math.round(v)) : (Math.round(v * 10) / 10).toFixed(1);
    // Roll over to the next unit when rounding reaches 1000 (999,950 → $1.0M, not $1000K).
    if (Number(text) < 1000 || k === UNITS.length - 1) return `$${text}${unit}`;
  }
  return `$${p}`; // unreachable
}

export interface MarkerSet {
  /** Plot index for each marker (picking index → plot index). */
  ids: Uint32Array;
  positions: Float32Array; // interleaved x,y
  colors?: Uint8Array;     // interleaved RGBA
}
export interface TierMarkers { on: MarkerSet; off: MarkerSet; edges: number[] }

const edgeCache = new WeakMap<Columns, number[]>();

/** `passing` (1 = shown) comes from the filter worker; price bands stay fixed by the unfiltered prices so colors don't shift. */
export function buildMarkers(c: Columns, passing?: Uint8Array): TierMarkers {
  const on: number[] = [], off: number[] = [], allOn: number[] = [];
  for (let i = 0; i < c.rows; i++) {
    const offm = isOffMarket(c, i);
    if (!offm) allOn.push(i);
    if (passing && !passing[i]) continue;
    (offm ? off : on).push(i);
  }
  const onIds = Uint32Array.from(on), offIds = Uint32Array.from(off);
  const price = c.col.price;
  let edges = edgeCache.get(c);
  if (!edges) edgeCache.set(c, (edges = priceBandEdges(price, Uint32Array.from(allOn))));
  const pos = (ids: Uint32Array) => {
    const p = new Float32Array(ids.length * 2);
    ids.forEach((i, k) => { p[2 * k] = c.col.x[i]!; p[2 * k + 1] = c.col.y[i]!; });
    return p;
  };
  const colors = new Uint8Array(onIds.length * 4);
  onIds.forEach((i, k) => { const [r, g, b] = BAND_COLORS[bandOf(price[i]!, edges)]!; colors.set([r, g, b, 235], 4 * k); });
  return { on: { ids: onIds, positions: pos(onIds), colors }, off: { ids: offIds, positions: pos(offIds) }, edges };
}

/** On-market markers inside the view rect, capped (pill layer budget). */
export function visibleIds(set: MarkerSet, rect: [number, number, number, number], cap: number): number[] {
  const [x0, y0, x1, y1] = rect, out: number[] = [];
  const p = set.positions;
  for (let k = 0; k < set.ids.length && out.length < cap; k++) {
    const x = p[2 * k]!, y = p[2 * k + 1]!;
    if (x >= x0 && x <= x1 && y >= y0 && y <= y1) out.push(set.ids[k]!);
  }
  return out;
}
