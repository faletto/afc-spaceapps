/** Rent Moonstimate for a stay (RENT-2). Mirrors pricing.rent_for_stay (golden_rent_v1.json). */
import { priceUsd, rentPerMonth, subscores, viability, type ScoreConfig } from './scoring';
import { siteSeries, siteStats, type Eph, type SciConfig } from './visibility';

export interface RentSite {
  lat: number; lon: number; horizon_deg: ArrayLike<number> | null;
  hazard_score: number; landmark_score: number; landing_safe: boolean; premium: number; ice_km: number | null;
}
export interface RentResult { viability_stay: number; price_stay: number; rent_per_month: number; stay_hours: number; total_stay: number; stats: ReturnType<typeof siteStats> }

/** Hours [a, b) of a stay starting on `moveInDay` (1 = Jan 1), clipped to the analysis year. */
export function stayWindow(moveInDay: number, stayDays: number, nHours: number): [number, number] {
  const a = 24 * (moveInDay - 1), b = Math.min(nHours, a + 24 * stayDays);
  if (!(a >= 0 && a < b)) throw new Error('move-in outside the analysis year');
  return [a, b];
}

export function rentForStay(site: RentSite, eph: Eph, cfg: SciConfig & ScoreConfig, cutoff: number, moveInDay: number, stayDays: number): RentResult {
  const [a, b] = stayWindow(moveInDay, stayDays, eph.tsi.length);
  const polar = site.ice_km != null;
  // Q-P8: polar sites (those with an ice distance) use the polar night floor; Moon-wide keeps floor_k.
  const stats = siteStats(siteSeries(site.lat, site.lon, site.horizon_deg, eph, cfg, a, b), eph, cfg, 2028, polar ? cfg.thermal.polar_floor_k : undefined);
  const sub = subscores({ ...stats, hazard_score: site.hazard_score, landmark_score: site.landmark_score, ice_km: site.ice_km, energy_wh_m2_day: stats.energy_wh_m2_day, earth_frac: stats.earth_frac }, cfg, polar);
  const v = viability(sub, site.landing_safe, cfg);
  const price = priceUsd(v, cfg, site.premium, cutoff);
  const rent = rentPerMonth(price, cfg);
  const hours = b - a;
  return { viability_stay: v, price_stay: price, rent_per_month: rent, stay_hours: hours, total_stay: (rent * hours) / 24 / (365.25 / 12), stats };
}
