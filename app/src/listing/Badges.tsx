import type { Columns } from '../data/types';

/** DET-11 in display priority. `price_cut` is Rent-tab only (A6); `featured` is not a badge. */
const ORDER: [string, string][] = [['hot_property', 'Hot property'], ['earth_view', 'Earth view'], ['peak_of_light', 'Peak of light'], ['off_market', 'Off market']];

export function badgeLabels(cols: Columns, i: number, max = 99): string[] {
  const f = cols.col.flags[i]!;
  const land = cols.meta.land_types[cols.col.land_type[i]!];
  return ORDER.filter(([k]) => (k === 'peak_of_light' ? land === 'peak_of_light' : k in cols.meta.flags && (f >> cols.meta.flags[k]!) & 1))
    .map(([, l]) => l).slice(0, max);
}

export function Badges({ cols, i, max }: { cols: Columns; i: number; max?: number }) {
  const on = badgeLabels(cols, i, max);
  if (!on.length) return null;
  return <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>{on.map((l) => (
    <span key={l} style={{ background: '#2b3a55', borderRadius: 4, padding: '2px 8px', fontSize: 12, fontWeight: 600 }}>{l}</span>))}</div>;
}
