/** Overlay menu labels and one-line explanations; units and ranges come from each overlay's legend JSON. */
import type { OverlayName } from '../data/loader';

/** Menu labels + one-line explanations (requirements §5.5). Legend JSON from the pipeline supplies unit/range/ramp. */
export const OVERLAY_INFO: Record<OverlayName, { label: string; blurb: string; polarOnly?: boolean }> = {
  sunlit: { label: 'Sunlight', blurb: 'Share of the year the Sun is above the horizon.' },
  earth: { label: 'Earth contact', blurb: 'Share of the year Earth is visible for radio contact.' },
  temperature: { label: 'Temperature', blurb: 'Surface temperature over the year.' },
  safety: { label: 'Terrain hazards', blurb: 'Slope and roughness; brighter means riskier to land.' },
  viability: { label: 'Viability', blurb: 'Combined 0–100 score for living on the plot.' },
  ice: { label: 'Ice access', blurb: 'Distance to water ice in permanently shadowed regions.', polarOnly: true },
};
