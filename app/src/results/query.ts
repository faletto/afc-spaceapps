import type { Columns, Tier } from '../data/types';
import type { Filters, Rect, SortKey } from '../state/store';
import { NO_FILTERS } from '../state/store';
import { isOffMarket } from '../map/markers';
import { matchPct, passesHome, type HomeCfg } from './homeTypes';

export const RESULT_CAP = 200;
export interface Results {
  ids: number[];
  total: number;
  /** 1 = plot passes the filters (ignores the map rect). Drives which markers the map draws. */
  passing: Uint8Array;
  /** Match % per id (parallel to `ids`) when a Home type is chosen; otherwise empty. */
  match: number[];
}

/** Does plot i pass the filters? Off-market plots have no price, so any price bound hides them (they can't be "in range"). */
export function passes(c: Columns, i: number, f: Filters, home?: HomeCfg | null, tier: Tier = 'global'): boolean {
  const off = isOffMarket(c, i);
  if (f.minSun > 0 && c.col.sunlit_pct[i]! < f.minSun) return false;
  if (f.minEarth > 0 && c.col.earth_pct[i]! < f.minEarth) return false;
  if (f.homeType !== 'any') {
    if (off || !home || !passesHome(c, i, f.homeType, home, tier)) return false;
  }
  if (off && f.hideOff) return false;
  if (f.landTypes.length && !f.landTypes.includes(c.col.land_type[i]!)) return false;
  if (f.priceMin != null || f.priceMax != null) {
    if (off) return false;
    const p = c.col.price[i]!;
    if (f.priceMin != null && p < f.priceMin) return false;
    if (f.priceMax != null && p > f.priceMax) return false;
  }
  return true;
}

/** Filtered plots inside `rect` (or the whole tier), sorted, top RESULT_CAP. The list shows on-market plots only. */
export function queryResults(c: Columns, rect: Rect | null, sort: SortKey, filters: Filters = NO_FILTERS, cap = RESULT_CAP, home: HomeCfg | null = null, tier: Tier = 'global'): Results {
  const { x, y } = c.col;
  const passing = new Uint8Array(c.rows);
  const hit: number[] = [];
  for (let i = 0; i < c.rows; i++) {
    if (!passes(c, i, filters, home, tier)) continue;
    passing[i] = 1;
    if (isOffMarket(c, i)) continue;
    if (rect && (x[i]! < rect[0] || x[i]! > rect[2] || y[i]! < rect[1] || y[i]! > rect[3])) continue;
    hit.push(i);
  }
  const matchOf = (i: number) => (home ? matchPct(c, i, filters.homeType, home) : c.col.viability[i]!);
  const key = sort === 'best_match' ? null : sort.startsWith('price') ? c.col.price : sort === 'viability_desc' ? c.col.viability
    : sort === 'sun_score_desc' ? c.col.s_power : c.col.s_comms;
  const dir = sort.endsWith('asc') ? 1 : -1;
  if (key) hit.sort((a, b) => dir * (key[a]! - key[b]!) || a - b);
  else { const m = new Map(hit.map((i) => [i, matchOf(i)])); hit.sort((a, b) => m.get(b)! - m.get(a)! || a - b); }
  const ids = hit.slice(0, cap);
  return { ids, total: hit.length, passing, match: filters.homeType !== 'any' && home ? ids.map(matchOf) : [] };
}
