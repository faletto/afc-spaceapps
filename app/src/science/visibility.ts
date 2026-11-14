/** Visibility, statistics and windows (spec §3.6–3.9). Mirrors pipeline/lunar_listings/visibility.py (golden tested). */
import { azEl, earthAzEl, enuFrame, R_MOON_M } from '../geo/geometry';

export const AU_KM = 149_597_870.7;
const RHO_1AU_DEG = 0.2666;
const SIGMA = 5.67e-8;
const L_SUN = 3.828e26;
const D2R = Math.PI / 180;

/** Subset of config.json used here. */
export interface SciConfig {
  power: { panel: string; sunlit_threshold: number };
  comms: { mode: string; margin_deg: number; cutoff_deg: number };
  thermal: { albedo: number; emissivity: number; floor_k: number; psr_floor_k: number };
}
export interface Eph { sun: ArrayLike<number>; earth: ArrayLike<number>; earthDistM: ArrayLike<number>; tsi: ArrayLike<number> }

export const HOURS_2028 = 8784;
export const DEFAULT_QUANT = { unitDeg: 0.16, offsetDeg: -6 };

/** Decode a plot's uint8 horizon (180 az samples) to degrees. */
export function decodeHorizon(q: ArrayLike<number>, unitDeg = DEFAULT_QUANT.unitDeg, offsetDeg = DEFAULT_QUANT.offsetDeg): Float64Array {
  return Float64Array.from(q as ArrayLike<number>, (v) => v * unitDeg + offsetDeg);
}

/** Circular linear interpolation of the horizon at azimuth az (deg). */
export function horizonAt(hz: ArrayLike<number>, az: number): number {
  const naz = hz.length, f = (az / (360 / naz)) % naz;
  const fl = Math.floor(f), i0 = ((fl % naz) + naz) % naz, t = f - fl;
  return hz[i0]! * (1 - t) + hz[(i0 + 1) % naz]! * t;
}

/** Visible fraction of the solar disk (circular segment). */
export function sunDiskFraction(elSun: number, horizon: number, rho: number): number {
  const x = Math.min(1, Math.max(-1, (elSun - horizon) / rho));
  return (Math.acos(-x) + x * Math.sqrt(1 - x * x)) / Math.PI;
}

export function monthOfHour(year: number, t: number): number {
  return new Date(Date.UTC(year, 0, 1, t)).getUTCMonth();
}

export interface Series {
  t0: number; n: number;
  sunEl: Float64Array; sunAz: Float64Array; earthEl: Float64Array; earthAz: Float64Array;
  fSun: Float64Array; sunlit: Uint8Array; earthOk: Uint8Array;
}

/** Hourly series for one site over hours [t0, t1). `hz` = horizon degrees (180 samples) or null for a smooth Moon. */
export function siteSeries(lat: number, lon: number, hz: ArrayLike<number> | null, eph: Eph, cfg: SciConfig, t0 = 0, t1 = eph.tsi.length, R = R_MOON_M): Series {
  const n = t1 - t0, f = enuFrame(lat, lon), margin = cfg.comms.mode === 'terrain_margin';
  const out: Series = { t0, n, sunEl: new Float64Array(n), sunAz: new Float64Array(n), earthEl: new Float64Array(n), earthAz: new Float64Array(n), fSun: new Float64Array(n), sunlit: new Uint8Array(n), earthOk: new Uint8Array(n) };
  for (let k = 0; k < n; k++) {
    const t = t0 + k;
    const s = azEl(eph.sun[3 * t]!, eph.sun[3 * t + 1]!, eph.sun[3 * t + 2]!, f);
    const e = earthAzEl(eph.earth[3 * t]!, eph.earth[3 * t + 1]!, eph.earth[3 * t + 2]!, eph.earthDistM[t]!, f, 0, R);
    const rSunKm = Math.sqrt(L_SUN / (4 * Math.PI * eph.tsi[t]!)) / 1e3;
    const rho = RHO_1AU_DEG / (rSunKm / AU_KM);
    const ms = hz ? horizonAt(hz, s.az) : 0, me = hz ? horizonAt(hz, e.az) : 0;
    const fs = sunDiskFraction(s.el, ms, rho);
    out.sunEl[k] = s.el; out.sunAz[k] = s.az; out.earthEl[k] = e.el; out.earthAz[k] = e.az; out.fSun[k] = fs;
    out.sunlit[k] = fs > cfg.power.sunlit_threshold ? 1 : 0;
    out.earthOk[k] = (margin ? e.el >= me + cfg.comms.margin_deg : e.el >= cfg.comms.cutoff_deg && e.el >= me) ? 1 : 0;
  }
  return out;
}

export function longestRun(mask: ArrayLike<number>, want: 0 | 1): number {
  let best = 0, cur = 0;
  for (let i = 0; i < mask.length; i++) { cur = mask[i] === want ? cur + 1 : 0; if (cur > best) best = cur; }
  return best;
}

/** Maximal runs of 0 as [start, length]. */
export function runsOfFalse(mask: ArrayLike<number>): [number, number][] {
  const out: [number, number][] = [];
  let start = -1;
  for (let i = 0; i < mask.length; i++) {
    if (!mask[i] && start < 0) start = i;
    else if (mask[i] && start >= 0) { out.push([start, i - start]); start = -1; }
  }
  if (start >= 0) out.push([start, mask.length - start]);
  return out;
}

export interface SiteStats {
  sunlit_frac: number; longest_dark_h: number; longest_light_h: number; energy_wh_m2_day: number;
  earth_frac: number; longest_blackout_h: number; mean_earth_el: number;
  temp_min_k: number; temp_mean_k: number; temp_max_k: number;
  monthly_sunlit: number[]; monthly_earth: number[];
}

/** Window statistics over a series (§3.6–3.7). */
export function siteStats(s: Series, eph: Eph, cfg: SciConfig, year = 2028): SiteStats {
  const { n } = s, vertical = cfg.power.panel === 'vertical_tracking', th = cfg.thermal;
  let nSun = 0, nE = 0, energy = 0, eeSum = 0, tSum95 = 0, tSum40 = 0, tMin95 = 1e9, tMin40 = 1e9, tMax95 = 0, tMax40 = 0;
  const ms = new Array<number>(12).fill(0), me = new Array<number>(12).fill(0), cnt = new Array<number>(12).fill(0);
  for (let k = 0; k < n; k++) {
    const tsi = eph.tsi[s.t0 + k]!, es = s.sunEl[k]!, fs = s.fSun[k]!;
    nSun += s.sunlit[k]!; nE += s.earthOk[k]!; eeSum += s.earthEl[k]!;
    energy += tsi * fs * (vertical ? Math.cos(es * D2R) : Math.max(0, Math.sin(es * D2R)));
    const fh = tsi * fs * Math.max(0, Math.sin(es * D2R));
    const teq = Math.max(0, ((1 - th.albedo) * fh) / (th.emissivity * SIGMA)) ** 0.25;
    const t95 = Math.max(teq, th.floor_k), t40 = Math.max(teq, th.psr_floor_k);
    tSum95 += t95; tSum40 += t40;
    tMin95 = Math.min(tMin95, t95); tMax95 = Math.max(tMax95, t95); tMin40 = Math.min(tMin40, t40); tMax40 = Math.max(tMax40, t40);
    const m = monthOfHour(year, s.t0 + k);
    cnt[m]!++; ms[m]! += s.sunlit[k]!; me[m]! += s.earthOk[k]!;
  }
  const psr = nSun === 0;
  return {
    sunlit_frac: nSun / n, longest_dark_h: longestRun(s.sunlit, 0), longest_light_h: longestRun(s.sunlit, 1),
    energy_wh_m2_day: energy / (n / 24), earth_frac: nE / n, longest_blackout_h: longestRun(s.earthOk, 0),
    mean_earth_el: eeSum / n,
    temp_min_k: psr ? tMin40 : tMin95, temp_mean_k: (psr ? tSum40 : tSum95) / n, temp_max_k: psr ? tMax40 : tMax95,
    monthly_sunlit: ms.map((v, k) => (cnt[k] ? v / cnt[k]! : NaN)), monthly_earth: me.map((v, k) => (cnt[k] ? v / cnt[k]! : NaN)),
  };
}

/** Min over daily starts of the longest 0-run inside a stay; returns [hours, start day-of-year (1-based)]. */
export function bestWindow(mask: ArrayLike<number>, stayDays: number): [number, number] {
  const L = stayDays * 24, nt = mask.length, runs = runsOfFalse(mask);
  let best = Infinity, bestS = 0;
  for (let s = 0; s + L <= nt; s += 24) {
    let worst = 0;
    for (const [a, len] of runs) worst = Math.max(worst, Math.min(a + len, s + L) - Math.max(a, s));
    if (worst < best) { best = worst; bestS = s; }
  }
  return [best, bestS / 24 + 1];
}

/** Hours from index k until `mask` next differs from its current value; null if it never changes in the series. */
export function hoursToChange(mask: ArrayLike<number>, k: number): { hours: number; to: 0 | 1 } | null {
  const cur = mask[k];
  for (let j = k + 1; j < mask.length; j++) if (mask[j] !== cur) return { hours: j - k, to: mask[j] as 0 | 1 };
  return null;
}
