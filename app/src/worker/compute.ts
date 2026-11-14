import { decodeColumns } from '../data/loader';
import type { Columns, ColsJson, Tier } from '../data/types';
import { queryResults, type Results } from '../results/query';
import type { Filters, Rect, SortKey } from '../state/store';
import type { HomeCfg } from '../results/homeTypes';

export type Req =
  | { type: 'init'; tier: Tier; meta: ColsJson; buffer: ArrayBuffer }
  | { type: 'query'; id: number; tier: Tier; rect: Rect | null; sort: SortKey; filters: Filters; home?: HomeCfg | null };
export type Res = { type: 'result'; id: number } & Results | { type: 'error'; id: number; message: string };

/** Pure message handler (testable without a Worker). Holds decoded columns per tier. */
export function makeHandler() {
  const tiers: Partial<Record<Tier, Columns>> = {};
  return (m: Req): Res | null => {
    if (m.type === 'init') { tiers[m.tier] = decodeColumns(m.meta, m.buffer); return null; }
    const c = tiers[m.tier];
    if (!c) return { type: 'error', id: m.id, message: `tier ${m.tier} not initialised` };
    return { type: 'result', id: m.id, ...queryResults(c, m.rect, m.sort, m.filters, undefined, m.home ?? null, m.tier) };
  };
}
