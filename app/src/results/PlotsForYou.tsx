import { useMemo } from 'react';
import type { Columns, Tier } from '../data/types';
import { badgeLabels } from '../listing/Badges';
import { formatPrice, isOffMarket } from '../map/markers';
import { plotName } from './homeTypes';

/** RES-4: 2–3 featured listings (flag `featured`): the best-viability one, the cheapest ("bargain"), and the next best. */
export function pickFeatured(c: Columns): number[] {
  const bit = c.meta.flags.featured;
  if (bit == null) return [];
  const f: number[] = [];
  for (let i = 0; i < c.rows; i++) if (((c.col.flags[i]! >> bit) & 1) === 1 && !isOffMarket(c, i)) f.push(i);
  if (!f.length) return [];
  const byVia = [...f].sort((a, b) => c.col.viability[b]! - c.col.viability[a]! || a - b);
  const cheapest = [...f].sort((a, b) => c.col.price[a]! - c.col.price[b]! || a - b)[0]!;
  const out = [byVia[0]!];
  if (!out.includes(cheapest)) out.push(cheapest);
  for (const i of byVia) { if (out.length >= 3) break; if (!out.includes(i)) out.push(i); }
  return out;
}

export function PlotsForYou({ cols, tier, onOpen }: { cols: Columns; tier: Tier; onOpen: (i: number) => void }) {
  const ids = useMemo(() => pickFeatured(cols), [cols]);
  if (!ids.length) return null;
  return (
    <section aria-label="Plots for you" style={{ padding: '0 12px 8px' }}>
      <h3 style={{ margin: '0 0 4px', fontSize: 14 }}>Plots for you</h3>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {ids.map((i) => (
          <button key={i} type="button" data-testid="featured" onClick={() => onOpen(i)} style={{ textAlign: 'left', padding: '4px 8px', borderRadius: 6, cursor: 'pointer' }}>
            <strong>{formatPrice(cols.col.price[i]!)}</strong> · {plotName(tier, cols.col.x[i]!, cols.col.y[i]!)}
            <div style={{ fontSize: 11, opacity: 0.7 }}>{badgeLabels(cols, i, 2).join(' · ') || 'Featured'}</div>
          </button>
        ))}
      </div>
    </section>
  );
}
