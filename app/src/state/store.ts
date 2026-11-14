import { create } from 'zustand';
import type { OverlayName } from '../data/loader';
import type { Tier } from '../data/types';
import type { Results } from '../results/query';

export type SortKey = 'price_asc' | 'price_desc' | 'viability_desc' | 'sun_score_desc' | 'signal_score_desc';
export type Rect = [number, number, number, number];

/** Filters (FIL-1..3). Prices are USD; null = unbounded. landTypes = indices into cols.meta.land_types ([] = all). */
export interface Filters { priceMin: number | null; priceMax: number | null; landTypes: number[]; hideOff: boolean }
export const NO_FILTERS: Filters = { priceMin: null, priceMax: null, landTypes: [], hideOff: false };

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
  setTab: (t: State['tab']) => void;
  setTier: (t: Tier) => void;
  select: (i: number | null) => void;
  setHover: (i: number | null) => void;
  setSort: (s: SortKey) => void;
  setFilters: (f: Partial<Filters>) => void;
  resetFilters: () => void;
  setResults: (r: Results | null) => void;
  setOverlay: (o: OverlayName | null) => void;
  setOverlayOpacity: (o: number) => void;
  setViewRect: (r: Rect | null) => void;
}
export const useStore = create<State>((set) => ({
  tab: 'buy', tier: 'global', selection: null, hover: null, sort: 'price_desc', filters: NO_FILTERS, results: null, overlay: null, overlayOpacity: 0.7, viewRect: null,
  setTab: (tab) => set({ tab }),
  setTier: (tier) => set((st) => ({ tier, results: null, selection: null, hover: null, viewRect: null, overlay: tier === 'global' && st.overlay === 'ice' ? null : st.overlay })),
  select: (selection) => set({ selection }),
  setHover: (hover) => set({ hover }),
  setSort: (sort) => set({ sort }),
  setFilters: (f) => set((st) => ({ filters: { ...st.filters, ...f } })),
  resetFilters: () => set({ filters: NO_FILTERS }),
  setResults: (results) => set({ results }),
  setOverlay: (overlay) => set({ overlay }),
  setOverlayOpacity: (overlayOpacity) => set({ overlayOpacity }),
  setViewRect: (viewRect) => set({ viewRect }),
}));
