import { create } from 'zustand';
import type { Tier } from '../data/types';

interface State {
  tab: 'buy' | 'rent';
  tier: Tier;
  /** Plot index within the current tier's columns. */
  selection: number | null;
  hover: number | null;
  setTab: (t: State['tab']) => void;
  setTier: (t: Tier) => void;
  select: (i: number | null) => void;
  setHover: (i: number | null) => void;
}
export const useStore = create<State>((set) => ({
  tab: 'buy', tier: 'global', selection: null, hover: null,
  setTab: (tab) => set({ tab }),
  setTier: (tier) => set({ tier, selection: null, hover: null }),
  select: (selection) => set({ selection }),
  setHover: (hover) => set({ hover }),
}));
