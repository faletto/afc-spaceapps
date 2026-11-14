import { decodeHorizon, hoursToChange, siteSeries, type Eph, type SciConfig, type Series } from '../science/visibility';

export interface TourModel { lat: number; lon: number; horizon: Float64Array; year: Series }

/** Full-year hourly series for a polar plot's best cell (the horizon in the tile is that cell's). */
export function buildTour(lat: number, lon: number, horizonQ: ArrayLike<number>, eph: Eph, cfg: SciConfig, unitDeg?: number, offsetDeg?: number): TourModel {
  const horizon = decodeHorizon(horizonQ, unitDeg, offsetDeg);
  return { lat, lon, horizon, year: siteSeries(lat, lon, horizon, eph, cfg) };
}

const fmtH = (h: number) => (h >= 48 ? `${Math.round(h / 24)} days` : `${h} h`);

/** Countdown text at hour t for a 0/1 mask (sun: sunlit, earth: earthOk). */
export function countdown(mask: Uint8Array, t: number, noun: 'Sun' | 'Earth', verbs: [string, string]): string {
  const ch = hoursToChange(mask, t);
  const now = mask[t] === 1;
  if (!ch) return now ? `${noun} stays up for the rest of 2028` : `${noun} stays ${noun === 'Sun' ? 'down' : 'out of sight'} for the rest of 2028`;
  return now ? `${noun} ${verbs[0]} in ${fmtH(ch.hours)}` : `${noun} ${verbs[1]} in ${fmtH(ch.hours)}`;
}
export const sunCountdown = (m: TourModel, t: number) => countdown(m.year.sunlit, t, 'Sun', ['sets', 'rises']);
export const earthCountdown = (m: TourModel, t: number) => countdown(m.year.earthOk, t, 'Earth', ['sets', 'rises']);

export const hourLabel = (t: number) => new Date(Date.UTC(2028, 0, 1, t)).toISOString().replace('T', ' ').slice(0, 16) + ' UTC';
