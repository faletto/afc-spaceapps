export interface GlossaryEntry { label: string; text: string; formula?: string; source?: string }

/**
 * App-side FALLBACK glossary. Spec D-1 wants this text in `config/glossary.json` (Pipeline-owned);
 * requested as R-A3 — swap to the exported file when it lands. Keep ids stable.
 */
export const GLOSSARY: Record<string, GlossaryEntry> = {
  sunlight: { label: 'Sunlight', text: 'Share of the year the Sun is above the plot\'s horizon.', source: 'NASA JPL Horizons ephemeris, 2028' },
  longest_night: { label: 'Longest night', text: 'Longest continuous stretch without sunlight.' },
  earth_contact: { label: 'Earth contact', text: 'Share of the year Earth is high enough above the local horizon for direct radio contact.', source: 'NASA JPL Horizons ephemeris, 2028' },
  longest_blackout: { label: 'Longest blackout', text: 'Longest continuous stretch with no line of sight to Earth.' },
  temperature: { label: 'Temperature', text: 'Modelled surface temperature range over the year. Shown in °C; hover for Kelvin.' },
  slope: { label: 'Mean slope', text: 'Average terrain slope across the plot. Steeper plots are harder to land on and build.', source: 'LRO LOLA elevation' },
  land_type: { label: 'Land type', text: 'Terrain class of the plot (mare, highland, crater floor, rim, ridge, PSR edge).' },
  ice: { label: 'Ice nearby', text: 'Distance to the nearest water-ice signal in permanently shadowed regions (polar plots only).' },
  viability: { label: 'Viability Score', text: 'Combined 0–100 score for how suitable the plot is for living and working.' },
  landing: { label: 'Landing Score', text: 'How safe the plot is to land on.' },
  sun_score: { label: 'Sun Score', text: 'How much sunlight is available for power.' },
  signal: { label: 'Signal Score', text: 'How much of the year the plot can see Earth.' },
  comfort: { label: 'Comfort Score', text: 'How mild the temperature swings are.' },
  views: { label: 'Views Score', text: 'Closeness to famous landmarks.' },
  ice_score: { label: 'Ice Score', text: 'Water ice within reach (polar plots only).' },
};
