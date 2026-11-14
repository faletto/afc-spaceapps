import type { Columns, Tier } from '../data/types';

/** Half-width of a plot in map units. ASSUMED: global 1° cells; polar 960 m plots (spec D-5). */
export const PLOT_HALF: Record<Tier, number> = { global: 0.5, polar: 480 };
/** Zoom levels above "fit" at which dots become price pills (MAP-2). */
export const PILL_ZOOM_ABOVE_FIT = 3;
export const PILL_CAP = 1500;

export const tierBounds = (c: Columns): [number, number, number, number] => c.meta.bounds;
export const fitZoom = (b: [number, number, number, number], w: number, h: number) =>
  Math.log2(Math.min(w / (b[2] - b[0]), h / (b[3] - b[1])));

export function plotSquare(x: number, y: number, tier: Tier): [number, number][] {
  const h = PLOT_HALF[tier];
  return [[x - h, y - h], [x + h, y - h], [x + h, y + h], [x - h, y + h]];
}
