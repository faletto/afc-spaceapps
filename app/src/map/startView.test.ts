import { describe, expect, it } from 'vitest';
import type { Columns } from '../data/types';
import { parseMode } from '../modes/mode';
import { clampTarget, randomPlotPosition, textColorFor } from './markers';

const cols = (flags: number[]): Columns => ({
  rows: flags.length, buffer: new ArrayBuffer(0), scales: {},
  meta: { flags: { off_market: 0 } } as unknown as Columns['meta'],
  col: { flags: Uint16Array.from(flags), x: Float32Array.from(flags.map((_, i) => i * 10)), y: Float32Array.from(flags.map((_, i) => i)) } as unknown as Columns['col'],
});

describe('start view', () => {
  it('random plot is always an on-market plot, and null when there is none', () => {
    const c = cols([1, 0, 1, 0, 1]); // plots 1 and 3 are on the market
    for (const r of [0, 0.3, 0.5, 0.99]) expect([10, 30]).toContain(randomPlotPosition(c, () => r)![0]);
    expect(randomPlotPosition(cols([1, 1]))).toBeNull();
  });
  it('clamps the view centre so no empty space shows past the bounds', () => {
    const b: [number, number, number, number] = [-180, -90, 180, 90];
    // zoom 3 at 800×400 px → view is 100° × 50° wide
    expect(clampTarget([179, 89], b, 3, 800, 400)).toEqual([130, 65]);
    expect(clampTarget([-179, -89], b, 3, 800, 400)).toEqual([-130, -65]);
    expect(clampTarget([10, 5], b, 3, 800, 400)).toEqual([10, 5]);
    // a view bigger than the map centres on it
    expect(clampTarget([170, 80], b, -3, 800, 400)).toEqual([0, 0]);
  });
  it('?view=fit keeps the whole map; default is a zoomed-in area', () => {
    expect(parseMode('').fit).toBe(false);
    expect(parseMode('?view=fit').fit).toBe(true);
  });
  it('pill text colour has enough contrast on every price band', () => {
    const lum = ([r, g, b]: number[]) => { const f = (v: number) => { const c = v / 255; return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(r!) + 0.7152 * f(g!) + 0.0722 * f(b!); };
    for (const band of [[94, 196, 160], [140, 210, 110], [240, 210, 80], [244, 140, 60], [220, 70, 80]] as [number, number, number][]) {
      const t = textColorFor(band), a = lum(band), b = lum(t);
      expect((Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05)).toBeGreaterThan(3.5);
    }
  });
});
