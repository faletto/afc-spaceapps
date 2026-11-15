/** Marker data for the map: price bands, off-market flag, typed-array marker sets built in one pass, and view-rect helpers. */
import type { Columns } from '../data/types';

export const FLAG_OFF_MARKET = 0;
export const isOffMarket = (c: Columns, i: number) => ((c.col.flags[i]! >> (c.meta.flags.off_market ?? FLAG_OFF_MARKET)) & 1) === 1;

/** Sequential price-band ramp, navy → baby blue (136, 188, 249) → near-white (cheap → pricey). Not color-only: off-market uses a different shape. */
export const BAND_COLORS: [number, number, number][] = [
  [52, 86, 138], [76, 124, 194], [106, 160, 232], [136, 188, 249], [216, 235, 255],
];

/** Dark or white text, whichever contrasts more with a band colour (WCAG relative luminance). */
export function textColorFor([r, g, b]: [number, number, number]): [number, number, number, number] {
  const lin = (v: number) => { const c = v / 255; return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
  const L = 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
  return (L + 0.05) / 0.05 > 1.05 / (L + 0.05) ? [18, 20, 28, 255] : [255, 255, 255, 255];
}

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
  // Single pass into preallocated typed arrays (no per-plot boxing); shrink with subarray at the end.
  const n = c.rows, { x, y, price } = c.col;
  const allOn = new Uint32Array(n);
  let nAll = 0;
  const offFlags = new Uint8Array(n);
  for (let i = 0; i < n; i++) { if (isOffMarket(c, i)) offFlags[i] = 1; else allOn[nAll++] = i; }
  let edges = edgeCache.get(c);
  if (!edges) edgeCache.set(c, (edges = priceBandEdges(price, allOn.subarray(0, nAll))));
  const onIds = new Uint32Array(n), offIds = new Uint32Array(n);
  const onPos = new Float32Array(2 * n), offPos = new Float32Array(2 * n), colors = new Uint8Array(4 * n);
  let a = 0, b = 0;
  for (let i = 0; i < n; i++) {
    if (passing && !passing[i]) continue;
    if (offFlags[i]) { offIds[b] = i; offPos[2 * b] = x[i]!; offPos[2 * b + 1] = y[i]!; b++; continue; }
    onIds[a] = i; onPos[2 * a] = x[i]!; onPos[2 * a + 1] = y[i]!;
    const [r, g, bl] = BAND_COLORS[bandOf(price[i]!, edges)]!;
    colors[4 * a] = r; colors[4 * a + 1] = g; colors[4 * a + 2] = bl; colors[4 * a + 3] = 235;
    a++;
  }
  return {
    on: { ids: onIds.slice(0, a), positions: onPos.slice(0, 2 * a), colors: colors.slice(0, 4 * a) },
    off: { ids: offIds.slice(0, b), positions: offPos.slice(0, 2 * b) },
    edges,
  };
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

/** A random on-market plot's position (the centre of the default view), or null if there are none. */
export function randomPlotPosition(c: Columns, rnd: () => number = Math.random): [number, number] | null {
  const ids: number[] = [];
  for (let i = 0; i < c.rows; i++) if (!isOffMarket(c, i)) ids.push(i);
  if (!ids.length) return null;
  const i = ids[Math.floor(rnd() * ids.length)]!;
  return [c.col.x[i]!, c.col.y[i]!];
}

/** View centre for a zoom level, kept inside the tier bounds (so a random pick near an edge doesn't show empty space). */
export function clampTarget(target: [number, number], bounds: [number, number, number, number], zoom: number, w: number, h: number): [number, number] {
  const hw = w / 2 / 2 ** zoom, hh = h / 2 / 2 ** zoom;
  const cl = (v: number, lo: number, hi: number) => (lo > hi ? (lo + hi) / 2 : Math.min(hi, Math.max(lo, v)));
  return [cl(target[0], bounds[0] + hw, bounds[2] - hw), cl(target[1], bounds[1] + hh, bounds[3] - hh)];
}
