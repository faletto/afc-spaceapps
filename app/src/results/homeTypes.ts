import type { Columns, Tier } from '../data/types';
import { ICE_NA } from '../data/types';

export type HomeType = 'any' | 'lander_pad' | 'habitat' | 'solar_farm' | 'ice_depot';
export const HOME_TYPES: [HomeType, string][] = [
  ['any', 'Any'], ['lander_pad', 'Lander pad'], ['habitat', 'Habitat'], ['solar_farm', 'Solar farm'], ['ice_depot', 'Ice depot'],
];

/** `home_types` block of config.json (weights are per sub-score name: safety, power, comms, thermal, landmark, ice). */
export interface HomeCfg {
  lander_pad: { gates: { longest_night_h: number }; weights: Record<string, number> };
  habitat: { gates: { longest_blackout_h: number }; weights: Record<string, number> };
  solar_farm: { gates: { safe_area_frac: number; sunlit_frac: number }; weights: Record<string, number> };
  ice_depot: { gates: { ice_km: number }; weights: Record<string, number>; polar_only?: boolean };
}

const SCORE_COL = { safety: 's_safety', power: 's_power', comms: 's_comms', thermal: 's_thermal', landmark: 's_landmark', ice: 's_ice' } as const;

/** Gate check (FIL-4a). Lander/Habitat gates use the precomputed best-window columns (bw_*). */
export function passesHome(c: Columns, i: number, type: HomeType, cfg: HomeCfg, tier: Tier): boolean {
  switch (type) {
    case 'any': return true;
    case 'lander_pad': return c.col.bw_lander_h[i]! <= cfg.lander_pad.gates.longest_night_h;
    case 'habitat': return c.col.bw_habitat_h[i]! <= cfg.habitat.gates.longest_blackout_h;
    case 'solar_farm':
      // ASSUMED: the safe-area gate (safe_area_frac ≥ 0.4) is not a column yet (R-A8); the sunlit gate is applied alone.
      return c.col.sunlit_pct[i]! / 100 >= cfg.solar_farm.gates.sunlit_frac;
    case 'ice_depot': {
      if (tier !== 'polar') return false; // polar_only
      const raw = c.col.ice_km10[i]!;
      return raw !== ICE_NA && raw * (c.scales.ice_km10 ?? 1) <= cfg.ice_depot.gates.ice_km;
    }
  }
}

/** match = 100 · Σ w·s / Σ w over the type's listed weights (any → viability). Never changes a price (D-6). */
export function matchPct(c: Columns, i: number, type: HomeType, cfg: HomeCfg): number {
  if (type === 'any') return c.col.viability[i]!;
  const w = cfg[type].weights;
  let num = 0, den = 0;
  for (const [k, wt] of Object.entries(w)) {
    const col = SCORE_COL[k as keyof typeof SCORE_COL];
    if (!col || !wt) continue;
    num += wt * c.col[col][i]!; den += wt;
  }
  return den ? num / den : 0;
}

/** Plot name from position: Moon-wide G-<lat idx:3>-<lon idx:3> (1° plots); polar SP-<row:4>-<col:4> (960 m plots, row 0 at +y). */
export function plotName(tier: Tier, x: number, y: number): string {
  const p = (n: number, w: number) => String(n).padStart(w, '0');
  if (tier === 'global') return `G-${p(Math.floor(y + 90), 3)}-${p(Math.floor(x + 180), 3)}`;
  return `SP-${p(Math.min(319, Math.floor((153600 - y) / 960)), 4)}-${p(Math.min(319, Math.floor((x + 153600) / 960)), 4)}`;
}
