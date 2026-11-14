import { create } from 'zustand';
import type { Tier } from '../data/types';

export type SortKey = 'price_asc' | 'price_desc' | 'viability_desc' | 'sunlit_desc';
export type Rect = [number, number, number, number];

interface State {
  tab: 'buy' | 'rent';
  tier: Tier;
  /** Plot index within the current tier's columns. */
  selection: number | null;
  hover: number | null;
  sort: SortKey;
  /** Visible map rect in tier coordinates (null = whole tier). */
  viewRect: Rect | null;
  setTab: (t: State['tab']) => void;
  setTier: (t: Tier) => void;
  select: (i: number | null) => void;
  setHover: (i: number | null) => void;
  setSort: (s: SortKey) => void;
  setViewRect: (r: Rect | null) => void;
}
export const useStore = create<State>((set) => ({
  tab: 'buy', tier: 'global', selection: null, hover: null, sort: 'price_desc', viewRect: null,
  setTab: (tab) => set({ tab }),
  setTier: (tier) => set({ tier, selection: null, hover: null, viewRect: null }),
  select: (selection) => set({ selection }),
  setHover: (hover) => set({ hover }),
  setSort: (sort) => set({ sort }),
  setViewRect: (viewRect) => set({ viewRect }),
}));
