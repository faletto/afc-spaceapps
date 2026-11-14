import type { Columns } from '../data/types';
import { ICE_NA } from '../data/types';
import { Term } from '../ui/Term';
import { value } from '../data/loader';

const c = (k: number) => `${(k - 273.15).toFixed(0)} °C`;

/** Facts & features in everyday units (DET-4); tooltips carry the Kelvin / plain-language detail (DET-8). */
export function Facts({ cols, i }: { cols: Columns; i: number }) {
  const land = cols.meta.land_types[cols.col.land_type[i]!] ?? 'unknown';
  const iceRaw = cols.col.ice_km10[i]!;
  const rows: [string, string, string, string][] = [
    ['Sunlight', `${cols.col.sunlit_pct[i]}% of the year`, 'Share of the 2028 hourly steps with the Sun above the horizon.', 'sunlight'],
    ['Longest night', `${cols.col.longest_dark_h[i]} h`, 'Longest continuous stretch without sunlight.', 'longest_night'],
    ['Earth contact', `${cols.col.earth_pct[i]}% of the year`, 'Share of the year Earth is visible above the local horizon.', 'earth_contact'],
    ['Longest blackout', `${cols.col.longest_blackout_h[i]} h`, 'Longest continuous stretch with no line of sight to Earth.', 'longest_blackout'],
    ['Temperature', `${c(cols.col.temp_min_k[i]!)} to ${c(cols.col.temp_max_k[i]!)}`, `${cols.col.temp_min_k[i]} K to ${cols.col.temp_max_k[i]} K`, 'temperature'],
    ['Mean slope', `${value(cols, 'slope_mean_ddeg', i).toFixed(1)}°`, 'Average terrain slope over the plot.', 'slope'],
    ['Land type', land.replace(/_/g, ' '), 'Terrain class of the plot.', 'land_type'],
    ['Ice nearby', iceRaw === ICE_NA ? 'n/a' : `${value(cols, 'ice_km10', i).toFixed(1)} km`, 'Distance to the nearest water-ice signal (polar plots).', 'ice'],
  ];
  return (
    <dl style={{ margin: 0, display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '4px 16px', fontSize: 13 }}>
      {rows.map(([k, v, extra, term]) => (<div key={k} style={{ display: 'contents' }}><dt style={{ opacity: 0.7 }}><Term id={term} extra={term === 'temperature' ? extra : undefined}>{k}</Term></dt><dd style={{ margin: 0 }}>{v}</dd></div>))}
    </dl>
  );
}
