import { loadDetailTile } from '../data/loader';
import { dataSource } from '../data/source';
import type { Columns, Tier } from '../data/types';
import { isOffMarket } from '../map/markers';
import { plotName } from '../results/homeTypes';
import { pickFeatured } from '../results/PlotsForYou';
import { useStore } from '../state/store';

/** PRS-2: one-click scenarios from the demo script. Each returns the tier it needs; `run` is called once that tier's columns are loaded. */
export interface Scenario { id: string; label: string; tier: Tier; run: (c: Columns) => Promise<void> | void }

const DAY = 24;

/** Cheapest on-market far-side plot (the "bargain" with 0% Earth contact). */
export function farSideBargain(c: Columns): number | null {
  const far = c.meta.land_types.indexOf('far_side');
  let best: number | null = null;
  for (let i = 0; i < c.rows; i++) {
    if (c.col.land_type[i] !== far || isOffMarket(c, i)) continue;
    if (best == null || c.col.price[i]! < c.col.price[best]!) best = i;
  }
  return best;
}

/** A featured plot next to Shackleton if the detail tiles say so, else the best featured plot. */
export async function shackletonRim(c: Columns): Promise<number | null> {
  const feat = pickFeatured(c);
  const all: number[] = [];
  const bit = c.meta.flags.featured;
  if (bit != null) for (let i = 0; i < c.rows; i++) if ((c.col.flags[i]! >> bit) & 1 && !isOffMarket(c, i)) all.push(i);
  for (const i of all.sort((a, b) => c.col.viability[b]! - c.col.viability[a]!).slice(0, 12)) {
    const rec = (await loadDetailTile(dataSource, 'polar', c.col.tile[i]!, c.meta.tiles_per_axis))[c.col.row_in_tile[i]!];
    if (rec?.nearest_feature?.startsWith('Shackleton')) return i;
  }
  console.warn('demo: no featured plot next to Shackleton found; using the best featured plot');
  return feat[0] ?? null;
}

export function plotIndexByName(c: Columns, tier: Tier, name: string): number | null {
  for (let i = 0; i < c.rows; i++) if (plotName(tier, c.col.x[i]!, c.col.y[i]!) === name) return i;
  return null;
}

export const RENT_DEMO_PLOT = 'SP-0172-0148';
export const RENT_DEMO_DAY = 274; // 30 Sep 2028

const s = () => useStore.getState();

export const SCENARIOS: Scenario[] = [
  { id: 'far-side', label: 'Far-side bargain', tier: 'global', run: (c) => {
    const i = farSideBargain(c);
    s().resetFilters(); s().setTab('buy'); s().setSort('price_asc'); s().setOverlay(null);
    if (i != null) s().select(i);
  } },
  { id: 'earth-overlay', label: 'Earth contact overlay', tier: 'global', run: () => { s().select(null); s().setOverlay('earth'); } },
  { id: 'sunlight-pole', label: 'Sunlight at the pole', tier: 'polar', run: () => { s().select(null); s().setOverlay('sunlit'); } },
  { id: 'shackleton', label: 'Shackleton rim + 3D Tour', tier: 'polar', run: async (c) => {
    const i = await shackletonRim(c);
    s().resetFilters(); s().setTab('buy'); s().setOverlay(null);
    if (i != null) { s().select(i); }
  } },
  { id: 'rent', label: 'Rent: move in 30 Sep', tier: 'polar', run: (c) => {
    const i = plotIndexByName(c, 'polar', RENT_DEMO_PLOT);
    s().resetFilters(); s().setOverlay(null); s().setTab('rent'); s().setStay(14); s().setT(DAY * (RENT_DEMO_DAY - 1));
    if (i != null) s().select(i);
  } },
];

/** The rent-shift step: two weeks later (rent changes; the Buy price does not). */
export const shiftMoveIn = () => s().setT(Math.min(8783, s().t + 14 * DAY));
