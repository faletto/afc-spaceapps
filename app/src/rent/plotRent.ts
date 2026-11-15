import type { AppConfig } from '../data/loader';
import type { Columns, Tier } from '../data/types';
import { ICE_NA } from '../data/types';
import { isOffMarket } from '../map/markers';
import { rentForStay, type RentResult, type RentSite } from '../science/rent';
import { subscores, type SubScores } from '../science/scoring';
import type { Eph } from '../science/visibility';

/**
 * Site inputs for a plot from the shipped columns. Safety/landmark are quantised to 0–100 in cols.bin, which is fine
 * because rent is computed as a DELTA from the plot's exported yearly rent (below), so the quantisation cancels.
 * `lat/lon/horizon` are the best cell's (polar: from detail.best_cell_xy + horizon tile) or the plot centre (Moon-wide).
 */
export function siteFromColumns(cols: Columns, i: number, tier: Tier, lat: number, lon: number, horizon: ArrayLike<number> | null): RentSite {
  const ice = cols.col.ice_km10[i]!;
  return {
    lat, lon, horizon_deg: horizon,
    hazard_score: 1 - cols.col.s_safety[i]! / 100, landmark_score: cols.col.s_landmark[i]! / 100,
    landing_safe: !isOffMarket(cols, i), premium: 0,
    ice_km: tier === 'polar' && ice !== ICE_NA ? ice * (cols.scales.ice_km10 ?? 1) : null,
  };
}

export interface PlotRent {
  /** Rent Moonstimate for the stay, $/month, and for the whole stay. */
  perMonth: number; total: number; stayHours: number;
  /** Yearly-average rent from the pipeline (the 1-year-stay rent, RENT-5). */
  avg: number; vsAvg: number;
  /** Why the rent differs from the average (RENT-3), or null if within ±3%. */
  reason: string | null;
  priceCut: boolean;
  sub: SubScores; subYear: SubScores; stats: { longest_dark_h: number; longest_blackout_h: number; earth_frac: number };
}

/** Full-year reference (compute once per plot and share). */
export const yearRent = (site: RentSite, eph: Eph, cfg: AppConfig) => rentForStay(site, eph, cfg, cfg.computed.scarcity_viability_cutoff, 1, 366);

const REASONS: Record<'power' | 'comms' | 'thermal', [string, string]> = {
  power: ['the Sun is up more of your stay', 'a long night falls in your stay'],
  comms: ['Earth is in view more of your stay', 'a comms blackout falls in your stay'],
  thermal: ['milder temperatures during your stay', 'harsher temperatures during your stay'],
};

/**
 * Rent for a stay = exported yearly rent × the price change implied by viability(stay) − viability(year), both computed
 * with the same (quantised) inputs through the golden-tested `rentForStay`. ASSUMED: the scarcity multiplier on the
 * yearly price is read from the exported viability (rounded) vs the cutoff; wrong only within ±0.5 of the cutoff.
 */
export function plotRent(site: RentSite, eph: Eph, cfg: AppConfig, cols: Columns, i: number, moveInDay: number, stayDays: number,
  yr: RentResult = yearRent(site, eph, cfg)): PlotRent {
  const cutoff = cfg.computed.scarcity_viability_cutoff;
  const st = rentForStay(site, eph, cfg, cutoff, moveInDay, stayDays);
  const avg = cols.col.rent_avg[i]!, vCol = cols.col.viability[i]!;
  const scar = (v: number) => (v >= cutoff ? cfg.price.scarcity_mult : 1);
  const perMonth = avg * Math.exp((cfg.price.k * (st.viability_stay - yr.viability_stay)) / 100) * (scar(st.viability_stay) / scar(vCol));
  const polar = site.ice_km != null;
  const mk = (s: typeof st) => subscores({ ...s.stats, hazard_score: site.hazard_score, landmark_score: site.landmark_score, ice_km: site.ice_km }, cfg, polar);
  const sub = mk(st), subYear = mk(yr);
  // Biggest weighted sub-score change among those that vary over time.
  let best: 'power' | 'comms' | 'thermal' | null = null, bd = 0;
  for (const k of ['power', 'comms', 'thermal'] as const) {
    const d = (cfg.weights[k] ?? 0) * (sub[k] - subYear[k]);
    if (Math.abs(d) > Math.abs(bd)) { bd = d; best = k; }
  }
  const vsAvg = perMonth / avg - 1;
  return {
    perMonth, total: (perMonth * st.stay_hours) / 24 / (365.25 / 12), stayHours: st.stay_hours, avg, vsAvg,
    reason: best && Math.abs(vsAvg) >= 0.03 ? REASONS[best][bd >= 0 ? 0 : 1] : null,
    priceCut: perMonth <= 0.9 * avg, sub, subYear,
    stats: { longest_dark_h: st.stats.longest_dark_h, longest_blackout_h: st.stats.longest_blackout_h, earth_frac: st.stats.earth_frac },
  };
}

/** DET-7: rent for a 30-day stay starting on the 1st of each month. */
export const MONTH_START_DAY = [1, 32, 61, 92, 122, 153, 183, 214, 245, 275, 306, 336]; // 2028 is a leap year
export function rentHistory(site: RentSite, eph: Eph, cfg: AppConfig, cols: Columns, i: number): number[] {
  const yr = yearRent(site, eph, cfg);
  return MONTH_START_DAY.map((d) => plotRent(site, eph, cfg, cols, i, d, 30, yr).perMonth);
}
