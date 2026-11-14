import { memo } from 'react';
import type { Columns, Tier } from '../data/types';
import { formatPrice } from '../map/markers';
import { factsLine } from './format';

/** Thumbnail = basemap crop centred on the plot; zoom = how many cards-widths of basemap. */
export const THUMB = { aspect: 2.4, zoom: 14 };

interface Props {
  cols: Columns; tier: Tier; i: number; basemapUrl: string;
  highlighted: boolean; selected: boolean;
  onHover: (i: number | null) => void; onOpen: (i: number) => void;
}

export const ListingCard = memo(function ListingCard({ cols, tier, i, basemapUrl, highlighted, selected, onHover, onOpen }: Props) {
  const [b0, b1, b2, b3] = cols.meta.bounds;
  const u = (cols.col.x[i]! - b0) / (b2 - b0), v = 1 - (cols.col.y[i]! - b1) / (b3 - b1);
  const aspect = (b2 - b0) / (b3 - b1);
  const Z = THUMB.zoom, r = 1 / THUMB.aspect;          // thumb height = r * width
  const imgH = Z / aspect;                              // image height in thumb widths
  const px = (u * Z - 0.5) / (Z - 1) * 100, py = (v * imgH - r / 2) / (imgH - r) * 100;
  return (
    <button
      type="button" data-testid="card" data-plot={i}
      onMouseEnter={() => onHover(i)} onMouseLeave={() => onHover(null)} onFocus={() => onHover(i)} onBlur={() => onHover(null)}
      onClick={() => onOpen(i)}
      style={{
        display: 'block', width: '100%', textAlign: 'left', padding: 0, cursor: 'pointer', color: 'inherit', background: '#161a22',
        border: `2px solid ${selected ? '#fff' : highlighted ? '#78beff' : '#262c38'}`, borderRadius: 8, overflow: 'hidden',
      }}
    >
      <div
        aria-hidden
        style={{
          aspectRatio: String(THUMB.aspect), backgroundImage: `url(${basemapUrl})`, backgroundRepeat: 'no-repeat',
          backgroundSize: `${Z * 100}% auto`, backgroundPosition: `${px}% ${py}%`,
        }}
      />
      <div style={{ padding: '6px 8px' }}>
        <div style={{ fontSize: 18, fontWeight: 700 }}>{formatPrice(cols.col.price[i]!)}</div>
        <div style={{ fontSize: 12, opacity: 0.85 }}>{factsLine(cols, i)}</div>
        <div style={{ fontSize: 11, opacity: 0.6 }}>
          Plot #{i} · {tier === 'polar' ? 'South Pole District' : 'Moon-wide'}
        </div>
      </div>
    </button>
  );
});
