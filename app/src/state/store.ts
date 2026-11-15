import { create } from 'zustand';
import type { OverlayName } from '../data/loader';
import type { Tier } from '../data/types';
import type { HomeType } from '../results/homeTypes';
import type { Results } from '../results/query';

export type SortKey = 'price_asc' | 'price_desc' | 'viability_desc' | 'sun_score_desc' | 'signal_score_desc' | 'best_match';
export const moveInDay = (t: number) => Math.floor(t / 24) + 1;
export type Rect = [number, number, number, number];

/** Filters (FIL-1..3). Prices are USD; null = unbounded. landTypes = indices into cols.meta.land_types ([] = all). */
export interface Filters { priceMin: number | null; priceMax: number | null; landTypes: number[]; hideOff: boolean; homeType: HomeType; minSun: number; minEarth: number }
export const NO_FILTERS: Filters = { priceMin: null, priceMax: null, landTypes: [], hideOff: false, homeType: 'any', minSun: 0, minEarth: 0 };

interface State {
  tab: 'buy' | 'rent';
  tier: Tier;
  /** Plot index within the current tier's columns. */
  selection: number | null;
  hover: number | null;
  sort: SortKey;
  filters: Filters;
  /** Latest worker answer for the current tier (list ids/total + filter mask for the map). */
  results: Results | null;
  overlay: OverlayName | null;
  overlayOpacity: number;
  /** Visible map rect in tier coordinates (null = whole tier). */
  viewRect: Rect | null;
  /** Time slider: hour index into the analysis year (TIME-1). On Rent it is the move-in date (RENT-1). */
  t: number;
  stayDays: number;
  setT: (t: number) => void;
  setStay: (d: number) => void;
  setTab: (t: State['tab']) => void;
  setTier: (t: Tier) => void;
  select: (i: number | null) => void;
  setHover: (i: number | null) => void;
  setSort: (s: SortKey) => void;
  setFilters: (f: Partial<Filters>) => void;
  /** FIL-4/FIL-7: choosing a type makes Best match the sort; going back to Any drops it. */
  setHomeType: (h: HomeType) => void;
  resetFilters: () => void;
  setResults: (r: Results | null) => void;
  setOverlay: (o: OverlayName | null) => void;
  setOverlayOpacity: (o: number) => void;
  setViewRect: (r: Rect | null) => void;
}
export const useStore = create<State>((set) => ({
  tab: 'buy', tier: 'global', selection: null, hover: null, sort: 'price_desc', filters: NO_FILTERS, results: null, overlay: null, overlayOpacity: 0.7, viewRect: null,
  t: 24 * 273, stayDays: 14,
  setT: (t) => set({ t }),
  setStay: (stayDays) => set({ stayDays }),
  // Buy bounds are dollars, Rent bounds are $/month: carrying one over would silently empty the list.
  setTab: (tab) => set((st) => ({ tab, filters: { ...st.filters, priceMin: null, priceMax: null } })),
  setTier: (tier) => set((st) => ({ tier, results: null, selection: null, hover: null, viewRect: null, overlay: tier === 'global' && st.overlay === 'ice' ? null : st.overlay })),
  select: (selection) => set({ selection }),
  setHover: (hover) => set({ hover }),
  setSort: (sort) => set({ sort }),
  setFilters: (f) => set((st) => ({ filters: { ...st.filters, ...f } })),
  setHomeType: (homeType) => set((st) => ({
    filters: { ...st.filters, homeType },
    sort: homeType !== 'any' ? 'best_match' : st.sort === 'best_match' ? 'viability_desc' : st.sort,
  })),
  resetFilters: () => set((st) => ({ filters: NO_FILTERS, sort: st.sort === 'best_match' ? 'viability_desc' : st.sort })),
  setResults: (results) => set({ results }),
  setOverlay: (overlay) => set({ overlay }),
  setOverlayOpacity: (overlayOpacity) => set({ overlayOpacity }),
  setViewRect: (viewRect) => set({ viewRect }),
}));
