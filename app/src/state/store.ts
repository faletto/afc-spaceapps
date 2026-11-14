import { create } from 'zustand';
import type { OverlayName } from '../data/loader';
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
  overlay: OverlayName | null;
  overlayOpacity: number;
  /** Visible map rect in tier coordinates (null = whole tier). */
  viewRect: Rect | null;
  setTab: (t: State['tab']) => void;
  setTier: (t: Tier) => void;
  select: (i: number | null) => void;
  setHover: (i: number | null) => void;
  setSort: (s: SortKey) => void;
  setOverlay: (o: OverlayName | null) => void;
  setOverlayOpacity: (o: number) => void;
  setViewRect: (r: Rect | null) => void;
}
export const useStore = create<State>((set) => ({
  tab: 'buy', tier: 'global', selection: null, hover: null, sort: 'price_desc', overlay: null, overlayOpacity: 0.7, viewRect: null,
  setTab: (tab) => set({ tab }),
  setTier: (tier) => set((st) => ({ tier, selection: null, hover: null, viewRect: null, overlay: tier === 'global' && st.overlay === 'ice' ? null : st.overlay })),
  select: (selection) => set({ selection }),
  setHover: (hover) => set({ hover }),
  setSort: (sort) => set({ sort }),
  setOverlay: (overlay) => set({ overlay }),
  setOverlayOpacity: (overlayOpacity) => set({ overlayOpacity }),
  setViewRect: (viewRect) => set({ viewRect }),
}));
