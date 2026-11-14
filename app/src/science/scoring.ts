/** Sub-scores, viability and pricing (spec §3.9–3.10). Mirrors pipeline scoring.py / pricing.py (golden tested). */

export interface ScoreConfig {
  power: { area_m2: number; efficiency: number; load_w: number; net_ref_w: number; battery_wh_per_kg: number; battery_ref_kg: number };
  penalty: { blackout: { h50: number; k: number } };
  thermal: { cold_range_k: [number, number]; swing_range_k: [number, number] };
  ice: { max_km: number };
  weights: Record<string, number>;
  price: { base_usd: number; k: number; scarcity_mult: number; rent_ratio: number; range: { global: number; polar: number } };
}

export const norm = (x: number, [lo, hi]: [number, number]) => Math.min(1, Math.max(0, (x - lo) / (hi - lo)));
export const penalty = (h: number, h50: number, k: number) => 1 / (1 + (h / h50) ** k);

export function thermalHazard(tMin: number, tMax: number, cfg: ScoreConfig): number {
  const cold = 1 - norm(tMin, cfg.thermal.cold_range_k);
  const swing = norm(tMax - tMin, cfg.thermal.swing_range_k);
  return (cold + swing) / 2;
}

export function powerScore(energyWhM2Day: number, longestDarkH: number, cfg: ScoreConfig): number {
  const pw = cfg.power;
  const harvest = (energyWhM2Day / 24) * pw.area_m2 * pw.efficiency;
  const net = Math.max(0, harvest - pw.load_w);
  const batteryKg = (pw.load_w * longestDarkH) / pw.battery_wh_per_kg;
  return norm(net, [0, pw.net_ref_w]) / (1 + batteryKg / pw.battery_ref_kg);
}

export interface ScoreInput {
  hazard_score: number; energy_wh_m2_day: number; longest_dark_h: number; earth_frac: number; longest_blackout_h: number;
  temp_min_k: number; temp_max_k: number; landmark_score: number; ice_km?: number | null;
}
export type SubScores = { safety: number; power: number; comms: number; thermal: number; landmark: number; ice: number };

export function subscores(t: ScoreInput, cfg: ScoreConfig, polar = false): SubScores {
  const pen = cfg.penalty.blackout;
  return {
    safety: 1 - t.hazard_score,
    power: powerScore(t.energy_wh_m2_day, t.longest_dark_h, cfg),
    comms: t.earth_frac * penalty(t.longest_blackout_h, pen.h50, pen.k),
    thermal: 1 - thermalHazard(t.temp_min_k, t.temp_max_k, cfg),
    landmark: t.landmark_score,
    ice: polar && t.ice_km != null ? 1 - norm(t.ice_km, [0, cfg.ice.max_km]) : 0,
  };
}

/** 0..100; unsafe plots are capped (Off market). */
export function viability(s: SubScores, landingSafe: boolean, cfg: ScoreConfig, cap = 10): number {
  let num = 0, den = 0;
  for (const k of Object.keys(s) as (keyof SubScores)[]) { const w = cfg.weights[k] ?? 0; num += w * s[k]; den += w; }
  const v = (100 * num) / den;
  return landingSafe ? v : Math.min(v, cap);
}

/** price = BASE·exp(k·v/100)·(1+premium)·(scarcity if v ≥ cutoff). */
export function priceUsd(v: number, cfg: ScoreConfig, premium = 0, cutoff: number | null = null): number {
  const p = cfg.price;
  return p.base_usd * Math.exp((p.k * v) / 100) * (1 + premium) * (cutoff != null && v >= cutoff ? p.scarcity_mult : 1);
}
export const rentPerMonth = (price: number, cfg: ScoreConfig) => cfg.price.rent_ratio * price;
