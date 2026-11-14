import { useEffect, useState } from 'react';
import { loadDetailTile, type DetailRecord } from '../data/loader';
import { dataSource } from '../data/source';
import type { Columns, Tier } from '../data/types';
import { formatPrice } from '../map/markers';
import { factsLine } from '../results/format';
import { Badges } from './Badges';
import { Facts } from './Facts';
import { FinePrint, InfoIcon } from './FinePrint';
import { Scores } from './Scores';

export function Listing({ cols, tier, i, onBack }: { cols: Columns; tier: Tier; i: number; onBack: () => void }) {
  const [detail, setDetail] = useState<DetailRecord | null>(null);
  useEffect(() => {
    let live = true;
    setDetail(null);
    const tile = cols.col.tile[i]!, row = cols.col.row_in_tile[i]!;
    loadDetailTile(dataSource, tier, tile, cols.meta.tiles_per_axis).then((rs) => { if (live) setDetail(rs[row] ?? null); });
    return () => { live = false; };
  }, [cols, tier, i]);

  useEffect(() => {
    const k = (e: KeyboardEvent) => e.key === 'Escape' && onBack();
    window.addEventListener('keydown', k);
    return () => window.removeEventListener('keydown', k);
  }, [onBack]);

  const lat = cols.col.lat[i]!, lon = cols.col.lon[i]!;
  const off = ((cols.col.flags[i]! >> (cols.meta.flags.off_market ?? 0)) & 1) === 1;
  return (
    <article aria-label="Listing" style={{ height: '100%', overflowY: 'auto', padding: 12, boxSizing: 'border-box', display: 'grid', gap: 14, alignContent: 'start' }}>
      <button type="button" onClick={onBack} style={{ justifySelf: 'start' }}>← Back to results</button>
      <header style={{ display: 'grid', gap: 4 }}>
        <Badges cols={cols} i={i} />
        <h2 data-testid="listing-title" style={{ margin: 0, fontSize: 22 }}>{detail?.id ? `Plot ${detail.id}` : detail?.name ?? `Plot #${i}`}</h2>
        <div style={{ fontSize: 12, opacity: 0.7 }}>
          {Math.abs(lat).toFixed(2)}°{lat < 0 ? 'S' : 'N'}, {Math.abs(lon).toFixed(2)}°{lon < 0 ? 'W' : 'E'} · {tier === 'polar' ? 'Detailed survey' : 'Moon-wide estimate'}
        </div>
        {detail?.nearby?.length ? <div data-testid="nearby" style={{ fontSize: 12, opacity: 0.8 }}>Near {detail.nearby.slice(0, 3).join(', ')}</div> : null}
      </header>
      <section>
        <div data-testid="listing-price" style={{ fontSize: 32, fontWeight: 800 }}>
          {off ? 'Off market' : formatPrice(cols.col.price[i]!)} <InfoIcon />
        </div>
        <div style={{ fontSize: 14 }}>{factsLine(cols, i)}</div>
        <div style={{ marginTop: 4 }}><FinePrint compact /></div>
        {/* TODO(R-A2): one-line "why" (DET-2) and blurb (DET-6, P5) are not in contract v2 yet. */}
        {detail?.blurb && <p style={{ margin: '8px 0 0', fontStyle: 'italic', opacity: 0.85 }}>{detail.blurb}</p>}
      </section>
      <Scores cols={cols} i={i} tier={tier} />
      <section><h3 style={{ margin: '0 0 6px', fontSize: 14 }}>Facts &amp; features</h3><Facts cols={cols} i={i} detail={detail} /></section>
    </article>
  );
}
