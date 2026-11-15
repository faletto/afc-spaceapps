import { memo } from 'react';
import type { Columns, Tier } from '../data/types';
import { formatPrice } from '../map/markers';
import { useStore } from '../state/store';
import { Badges } from '../listing/Badges';
import { factsLine } from './format';
import { plotName } from './homeTypes';

/** Thumbnail = basemap crop centred on the plot; zoom = how many card-widths of basemap (small basemap is ~2048 px wide, so keep this modest). */
export const THUMB = { aspect: 2.4, zoom: 10 };

interface Props {
  cols: Columns; tier: Tier; i: number; basemapUrl: string | null;
  onHover: (i: number | null) => void; onOpen: (i: number) => void;
  /** Home-type match % (FIL-4); undefined when no type is chosen. */
  match?: number;
}

export const ListingCard = memo(function ListingCard({ cols, tier, i, basemapUrl, onHover, onOpen, match }: Props) {
  const rent = useStore((s) => s.tab === 'rent');
  // Per-card subscriptions: a hover re-renders only the two cards whose flag flips, not the whole list.
  const highlighted = useStore((s) => s.hover === i), selected = useStore((s) => s.selection === i);
  const [b0, b1, b2, b3] = cols.meta.bounds;
  const u = (cols.col.x[i]! - b0) / (b2 - b0), v = 1 - (cols.col.y[i]! - b1) / (b3 - b1);
  const aspect = (b2 - b0) / (b3 - b1);
  const Z = THUMB.zoom, r = 1 / THUMB.aspect;          // thumb height = r * width
  const imgH = Z / aspect;                              // image height in thumb widths
  const px = (u * Z - 0.5) / (Z - 1) * 100, py = (v * imgH - r / 2) / (imgH - r) * 100;
  return (
    <button
      type="button" className="card" data-testid="card" data-plot={i} data-selected={selected} data-highlighted={highlighted}
      onMouseEnter={() => onHover(i)} onMouseLeave={() => onHover(null)} onFocus={() => onHover(i)} onBlur={() => onHover(null)}
      onClick={() => onOpen(i)}
>
      <div
        aria-hidden
        style={{
          aspectRatio: String(THUMB.aspect), backgroundImage: basemapUrl ? `url(${basemapUrl})` : undefined, backgroundColor: 'var(--surface-2)', backgroundRepeat: 'no-repeat',
          backgroundSize: `${Z * 100}% auto`, backgroundPosition: `${px}% ${py}%`,
        }}
      />
      <div style={{ padding: '8px 10px 10px', display: 'grid', gap: 2 }}>
        <div style={{ fontSize: 19, fontWeight: 800, letterSpacing: '-0.02em' }}>
          {rent ? `${formatPrice(cols.col.rent_avg[i]!)}/mo` : formatPrice(cols.col.price[i]!)}
          {rent && <span className="muted" style={{ marginLeft: 6, fontSize: 11, fontWeight: 400 }}>avg</span>}
          {match != null && <span data-testid="match" className="chip" style={{ marginLeft: 8, fontSize: 11 }}>{Math.round(match)}% match</span>}
        </div>
        <div style={{ fontSize: 12, color: 'var(--text)', opacity: 0.88 }}>{factsLine(cols, i)}</div>
        <div className="muted" style={{ fontSize: 11 }}>
          {plotName(tier, cols.col.x[i]!, cols.col.y[i]!)} · {tier === 'polar' ? 'South Pole District' : 'Moon-wide'}
        </div>
        <Badges cols={cols} i={i} max={2} />
      </div>
    </button>
  );
});
