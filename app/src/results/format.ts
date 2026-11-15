import type { Columns } from '../data/types';

/** The four headline facts, with units and what each one measures (DET-10), for tiles and the compact card line. */
export function factsParts(c: Columns, i: number) {
  const slope = c.col.slope_mean_ddeg[i]! * (c.scales.slope_mean_ddeg ?? 1);
  return {
    sun: `${c.col.sunlit_pct[i]}%`, earth: `${c.col.earth_pct[i]}%`, slope: `${slope.toFixed(0)}°`, area: `${c.col.area_km2[i]!.toFixed(1)} km²`,
  };
}

/** Compact card line: "Sunlit 51% of the year · Earth in view 0% of the year · 3° slope · 784 km²". */
export function factsLine(c: Columns, i: number): string {
  const f = factsParts(c, i);
  return `Sunlit ${f.sun} of the year · Earth in view ${f.earth} of the year · ${f.slope} slope · ${f.area}`;
}
