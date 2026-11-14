import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { azEl, earthAzEl, enuFrame } from '../geo/geometry';
import { polarXYToLatLon } from '../geo/projections';
import { bestWindow, decodeHorizon, runsOfFalse, siteSeries, siteStats, type SciConfig } from './visibility';

const data = (p: string) => new URL(`../../public/data/${p}`, import.meta.url);
const golden = JSON.parse(readFileSync(new URL('../../../pipeline/tests/golden/golden_v1.json', import.meta.url), 'utf8'));
const cfg = JSON.parse(readFileSync(data('config.json'), 'utf8')) as SciConfig;
// NOTE: public/data/ephemeris.bin is still the v1 stub (R-A6), so parity builds the real float64 ephemeris from the pipeline CSV.
const rows = readFileSync(new URL('../../../pipeline/data/ephemeris_2028.csv', import.meta.url), 'utf8').trim().split('\n').slice(1).map((l) => l.split(',').slice(1).map(Number) as number[]);
const unit = (lonD: number, latD: number) => { const lo = (lonD * Math.PI) / 180, la = (latD * Math.PI) / 180; return [Math.cos(la) * Math.cos(lo), Math.cos(la) * Math.sin(lo), Math.sin(la)]; };
const eph = {
  sun: Float64Array.from(rows.flatMap((r) => unit(r[2]!, r[3]!))),
  earth: Float64Array.from(rows.flatMap((r) => unit(r[0]!, r[1]!))),
  earthDistM: Float64Array.from(rows, (r) => r[5]! * 1e3),
  tsi: Float64Array.from(rows, (r) => 3.828e26 / (4 * Math.PI * (r[4]! * 1e3) ** 2)),
};
const dAz = (a: number, b: number) => Math.abs(((a - b + 540) % 360) - 180);

describe('geometry parity', () => {
  it('matches golden az/el', () => {
    for (const g of golden.geometry) {
      const fr = enuFrame(g.lat, g.lon), t = g.hour;
      const s = azEl(eph.sun[3 * t]!, eph.sun[3 * t + 1]!, eph.sun[3 * t + 2]!, fr);
      const e = earthAzEl(eph.earth[3 * t]!, eph.earth[3 * t + 1]!, eph.earth[3 * t + 2]!, eph.earthDistM[t]!, fr);
      expect(Math.abs(s.el - g.sun_el)).toBeLessThan(1e-4);
      expect(Math.abs(e.el - g.earth_el)).toBeLessThan(1e-4);
      if (Math.abs(g.sun_el) < 85) expect(dAz(s.az, g.sun_az)).toBeLessThan(1e-3); // near zenith azimuth is ill-conditioned
      if (Math.abs(g.earth_el) < 85) expect(dAz(e.az, g.earth_az)).toBeLessThan(1e-6);
    }
  });
  it('enu frame is orthonormal', () => {
    const { u, e, n } = enuFrame(-89.7, 45);
    const d = (a: readonly number[], b: readonly number[]) => a[0]! * b[0]! + a[1]! * b[1]! + a[2]! * b[2]!;
    expect(d(u, e)).toBeCloseTo(0, 12); expect(d(u, n)).toBeCloseTo(0, 12); expect(d(e, n)).toBeCloseTo(0, 12);
    expect(d(n, n)).toBeCloseTo(1, 12);
  });
  it('polar inverse projection', () => {
    expect(polarXYToLatLon(0, 0).lat).toBeCloseTo(-90, 9);
    const R = 1_737_400, lat = -88, lon = 30, rho = 2 * R * Math.tan(((45 + lat / 2) * Math.PI) / 180);
    const p = polarXYToLatLon(rho * Math.sin((lon * Math.PI) / 180), rho * Math.cos((lon * Math.PI) / 180));
    expect(p.lat).toBeCloseTo(lat, 9); expect(p.lon).toBeCloseTo(lon, 9);
  });
});

describe('visibility parity', () => {
  golden.visibility.forEach((g: Record<string, number[] | number>, idx: number) => {
    it(`site ${idx} (${g.lat}, ${g.lon})`, () => {
      const s = siteSeries(g.lat as number, g.lon as number, g.horizon as number[], eph, cfg);
      const st = siteStats(s, eph, cfg);
      for (const k of ['sunlit_frac', 'earth_frac'] as const) expect(Math.abs(st[k] - (g[k] as number)), k).toBeLessThan(1e-9);
      for (const k of ['mean_earth_el', 'temp_min_k', 'temp_mean_k', 'temp_max_k'] as const) expect(Math.abs(st[k] - (g[k] as number)), k).toBeLessThan(1e-6);
      expect(Math.abs(st.energy_wh_m2_day / (g.energy_wh_m2_day as number) - 1)).toBeLessThan(1e-9);
      for (const k of ['longest_dark_h', 'longest_light_h', 'longest_blackout_h'] as const) expect(Math.abs(st[k] - (g[k] as number)), k).toBe(0);
      (g.monthly_sunlit as number[]).forEach((v, m) => expect(Math.abs(st.monthly_sunlit[m]! - v)).toBeLessThan(1e-9));
      expect(Math.abs(runsOfFalse(s.sunlit).length - (g.dark_runs as number[][]).length)).toBe(0);
      expect(Math.abs(bestWindow(s.sunlit, 14)[0] - (g.best_window_lander as number[])[0]!)).toBe(0);
      expect(Math.abs(bestWindow(s.earthOk, 90)[0] - (g.best_window_habitat as number[])[0]!)).toBe(0);
    });
  });
  // Golden quantisation cases were generated with horizons.quantize's default offset (-3) while the manifest/data use -6 (R-A7).
  it.skip('horizon quantisation golden cases (pending R-A7)', () => {
    const q = golden.horizon_quantisation;
    for (const c of q.cases) {
      const d = decodeHorizon([c.q], q.unit_deg, q.offset_deg)[0]!;
      expect(Math.abs(d - Math.min(34.8, Math.max(-6, c.deg)))).toBeLessThanOrEqual(0.08 + 1e-9);
    }
  });
  it('decodeHorizon uses v*0.16-6', () => {
    expect(decodeHorizon([0, 255])[0]).toBe(-6);
    expect(decodeHorizon([0, 255])[1]).toBeCloseTo(34.8, 9);
  });
});
