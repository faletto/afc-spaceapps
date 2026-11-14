import { create } from 'zustand';
import type { Tier } from '../data/types';

interface State {
  tab: 'buy' | 'rent';
  tier: Tier;
  selection: number | null;
  setTab: (t: State['tab']) => void;
  setTier: (t: Tier) => void;
  select: (i: number | null) => void;
}
export const useStore = create<State>((set) => ({
  tab: 'buy', tier: 'global', selection: null,
  setTab: (tab) => set({ tab }), setTier: (tier) => set({ tier }), select: (selection) => set({ selection }),
}));
