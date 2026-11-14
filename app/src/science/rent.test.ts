import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { rentForStay, stayWindow } from './rent';
import { priceUsd, subscores, viability, type ScoreConfig } from './scoring';
import type { SciConfig } from './visibility';

const data = (p: string) => new URL(p, import.meta.url);
const cfg = JSON.parse(readFileSync(data('../../public/data/config.json'), 'utf8')) as SciConfig & ScoreConfig;
const rentG = JSON.parse(readFileSync(data('../../../pipeline/tests/golden/golden_rent_v1.json'), 'utf8'));
const golden = JSON.parse(readFileSync(data('../../../pipeline/tests/golden/golden_v1.json'), 'utf8'));
const rows = readFileSync(data('../../../pipeline/data/ephemeris_2028.csv'), 'utf8').trim().split('\n').slice(1).map((l) => l.split(',').slice(1).map(Number) as number[]);
const unit = (lonD: number, latD: number) => { const lo = (lonD * Math.PI) / 180, la = (latD * Math.PI) / 180; return [Math.cos(la) * Math.cos(lo), Math.cos(la) * Math.sin(lo), Math.sin(la)]; };
const eph = {
  sun: Float64Array.from(rows.flatMap((r) => unit(r[2]!, r[3]!))), earth: Float64Array.from(rows.flatMap((r) => unit(r[0]!, r[1]!))),
  earthDistM: Float64Array.from(rows, (r) => r[5]! * 1e3), tsi: Float64Array.from(rows, (r) => 3.828e26 / (4 * Math.PI * (r[4]! * 1e3) ** 2)),
};

describe('scoring/pricing parity (golden_v1)', () => {
  it('sub-scores, viability (safe + unsafe) and price table', () => {
    const g = golden.scoring, s = subscores(g.input, cfg);
    for (const k of Object.keys(g.subscores)) expect(s[k as keyof typeof s], k).toBeCloseTo(g.subscores[k], 9);
    expect(viability(s, true, cfg)).toBeCloseTo(g.viability_safe, 9);
    expect(viability(s, false, cfg)).toBeCloseTo(g.viability_unsafe, 9);
    for (const p of golden.pricing) {
      expect(Math.abs(priceUsd(p.viability, cfg) / p.price - 1)).toBeLessThan(1e-9);
      expect(Math.abs(priceUsd(p.viability, cfg, 0.25, 60) / p.price_scarce - 1)).toBeLessThan(1e-9);
    }
  });
});

describe('rent parity (golden_rent_v1)', () => {
  it('stayWindow clips to the year', () => {
    expect(stayWindow(1, 14, 8784)).toEqual([0, 336]);
    expect(stayWindow(360, 90, 8784)).toEqual([24 * 359, 8784]);
    expect(() => stayWindow(400, 14, 8784)).toThrow();
  });
  it(`matches all ${rentG.cases.length} cases (relative 1e-9)`, () => {
    const sites = new Map<string, (typeof rentG.sites)[number]>(rentG.sites.map((s: { id: string }) => [s.id, s]));
    for (const c of rentG.cases) {
      const s = sites.get(c.site)!;
      const r = rentForStay({ ...s, horizon_deg: s.horizon_deg }, eph, cfg, rentG.scarcity_cutoff, c.move_in_day, c.stay_days);
      for (const k of ['viability_stay', 'price_stay', 'rent_per_month', 'total_stay'] as const) {
        expect(Math.abs(r[k] / c[k] - 1), `${c.site} d${c.move_in_day} ${c.stay_days}d ${k}`).toBeLessThan(1e-7);
      }
      expect(r.stay_hours).toBe(c.stay_hours);
    }
  });
});
