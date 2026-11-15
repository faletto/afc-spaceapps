/** URL modes (spec §6.6): ?demo=1 preloaded scenarios, ?present=1 large-type presentation layout. */
export interface Mode { demo: boolean; present: boolean; /** ?view=fit starts on the whole map instead of a random zoomed-in area. */ fit: boolean }
export const parseMode = (search: string): Mode => {
  const q = new URLSearchParams(search);
  return { demo: q.get('demo') === '1', present: q.get('present') === '1', fit: q.get('view') === 'fit' };
};
export const MODE: Mode = parseMode(typeof location === 'undefined' ? '' : location.search);
/** Present mode scales type and markers by this factor (1920×1080 projector layout). */
export const PRESENT_ZOOM = 1.35;
