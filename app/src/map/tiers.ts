import type { Columns, Tier } from '../data/types';

/** Half-width of a plot in map units. ASSUMED: global 1° cells; polar 960 m plots (spec D-5). */
export const PLOT_HALF: Record<Tier, number> = { global: 0.5, polar: 480 };
/** MAP-2: dots become price pills only when a plot is at least this many screen pixels wide, so each tag has room and the
 * map is never a wall of prices. With an overlay on, pills need much more zoom so the overlay colours stay visible. */
export const PILL_MIN_PLOT_PX = 110;
export const PILL_MIN_PLOT_PX_OVERLAY = 220;
/** Never draw more pills than this at once. */
export const PILL_CAP = 250;
/** Pills shown for a plot this many pixels wide (see above). */
export const pillsVisible = (plotPx: number, overlayOn: boolean) => plotPx >= (overlayOn ? PILL_MIN_PLOT_PX_OVERLAY : PILL_MIN_PLOT_PX);
/** First view: zoom this many levels in from "fit" (about 40 plots across on Moon-wide) so the map isn't a wall of markers. */
export const START_ZOOM_ABOVE_FIT = 5;

export const tierBounds = (c: Columns): [number, number, number, number] => c.meta.bounds;
export const fitZoom = (b: [number, number, number, number], w: number, h: number) =>
  Math.log2(Math.min(w / (b[2] - b[0]), h / (b[3] - b[1])));

export function plotSquare(x: number, y: number, tier: Tier): [number, number][] {
  const h = PLOT_HALF[tier];
  return [[x - h, y - h], [x + h, y - h], [x + h, y + h], [x - h, y + h]];
}
