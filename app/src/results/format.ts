import type { Columns } from '../data/types';

/** Facts line (DET-10): "82% sun · 61% Earth · 4° slope · 1.0 km²". */
export function factsLine(c: Columns, i: number): string {
  const slope = c.col.slope_mean_ddeg[i]! * (c.scales.slope_mean_ddeg ?? 1);
  return `${c.col.sunlit_pct[i]}% sun · ${c.col.earth_pct[i]}% Earth · ${slope.toFixed(0)}° slope · ${c.col.area_km2[i]!.toFixed(1)} km²`;
}
