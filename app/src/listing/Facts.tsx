/** Facts and features list for a listing, in everyday units. Column rows are instant; detail-tile rows fill in on load. */
import type { DetailRecord } from '../data/loader';
import { value } from '../data/loader';
import type { Columns } from '../data/types';
import { ICE_NA } from '../data/types';
import { Term } from '../ui/Term';

const c = (k: number) => `${(k - 273.15).toFixed(0)} °C`;
const titleCase = (s: string) => s.replace(/_/g, ' ').replace(/^\w/, (x) => x.toUpperCase());

/** Facts & features in everyday units (DET-4). Column-derived rows are instant; `detail` rows fill in when the tile loads. */
export function Facts({ cols, i, detail }: { cols: Columns; i: number; detail: DetailRecord | null }) {
  const land = cols.meta.land_types[cols.col.land_type[i]!] ?? 'unknown';
  const iceRaw = cols.col.ice_km10[i]!;
  const rows: [string, string, string, string?][] = [
    ['Sunlight', `${cols.col.sunlit_pct[i]}% of the year`, '', 'sunlight'],
    ['Longest night', `${cols.col.longest_dark_h[i]} h`, '', 'longest_night'],
    ['Earth contact', `${cols.col.earth_pct[i]}% of the year`, '', 'earth_contact'],
    ['Longest blackout', `${cols.col.longest_blackout_h[i]} h`, '', 'longest_blackout'],
    ['Temperature', `${c(cols.col.temp_min_k[i]!)} to ${c(cols.col.temp_max_k[i]!)}`, `${cols.col.temp_min_k[i]} K to ${cols.col.temp_max_k[i]} K.`, 'temperature'],
    ['Mean slope', `${value(cols, 'slope_mean_ddeg', i).toFixed(1)}°`, '', 'slope'],
    ['Land type', titleCase(land), '', 'land_type'],
    ['Ice nearby', iceRaw === ICE_NA ? 'n/a' : `${value(cols, 'ice_km10', i).toFixed(1)} km`, '', 'ice'],
  ];
  if (detail) {
    if (detail.temp_mean_k != null) rows.splice(5, 0, ['Mean temperature', c(detail.temp_mean_k), `${detail.temp_mean_k} K.`, 'temperature']);
    if (detail.slope_p90_deg != null) rows.push(['Slope (90th pct)', `${detail.slope_p90_deg.toFixed(1)}°`, '', 'slope']);
    if (detail.safe_area_frac != null) rows.push(['Buildable area', `${Math.round(detail.safe_area_frac * 100)}%`, 'Share of the plot gentle enough to build on.', undefined]);
    if (detail.landing_safe != null) rows.push(['Landing', detail.landing_safe ? 'Safe to land' : 'Not safe to land', '', undefined]);
    if (detail.energy_wh_m2_day != null) rows.push(['Solar energy', `${(detail.energy_wh_m2_day / 1000).toFixed(1)} kWh/m²/day`, 'Mean incident solar energy per day over the year.', undefined]);
    if (detail.longest_light_h != null) rows.push(['Longest daylight', `${detail.longest_light_h} h`, '', undefined]);
  }
  return (
    <dl style={{ margin: 0, display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '4px 16px', fontSize: 13 }}>
      {rows.map(([k, v, extra, term]) => (
        <div key={k} style={{ display: 'contents' }} title={term ? undefined : extra || undefined}>
          <dt style={{ opacity: 0.7 }}>{term ? <Term id={term} extra={extra || undefined}>{k}</Term> : k}</dt>
          <dd style={{ margin: 0 }}>{v}</dd>
        </div>
      ))}
    </dl>
  );
}
