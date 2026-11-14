import type { Columns } from '../data/types';

const LABELS: Record<string, string> = { hot_property: 'Hot property', price_cut: 'Price cut', earth_view: 'Earth view', featured: 'Featured', off_market: 'Off market' };

export function Badges({ cols, i }: { cols: Columns; i: number }) {
  const f = cols.col.flags[i]!;
  const on = Object.entries(cols.meta.flags).filter(([k, bit]) => k in LABELS && (f >> bit) & 1).map(([k]) => LABELS[k]!);
  if (!on.length) return null;
  return <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>{on.map((l) => (
    <span key={l} style={{ background: '#2b3a55', borderRadius: 4, padding: '2px 8px', fontSize: 12, fontWeight: 600 }}>{l}</span>))}</div>;
}
