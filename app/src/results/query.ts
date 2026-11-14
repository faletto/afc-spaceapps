import type { Columns } from '../data/types';
import type { Rect, SortKey } from '../state/store';
import { isOffMarket } from '../map/markers';

export const RESULT_CAP = 200;
export interface Results { ids: number[]; total: number }

/** Plots inside `rect` (or whole tier), sorted, top RESULT_CAP. Off-market plots are excluded (no price). */
export function queryResults(c: Columns, rect: Rect | null, sort: SortKey, cap = RESULT_CAP): Results {
  const { x, y } = c.col;
  const hit: number[] = [];
  for (let i = 0; i < c.rows; i++) {
    if (isOffMarket(c, i)) continue;
    if (rect && (x[i]! < rect[0] || x[i]! > rect[2] || y[i]! < rect[1] || y[i]! > rect[3])) continue;
    hit.push(i);
  }
  const key = sort.startsWith('price') ? c.col.price : sort === 'viability_desc' ? c.col.viability : c.col.sunlit_pct;
  const dir = sort.endsWith('asc') ? 1 : -1;
  hit.sort((a, b) => dir * (key[a]! - key[b]!) || a - b);
  return { ids: hit.slice(0, cap), total: hit.length };
}
