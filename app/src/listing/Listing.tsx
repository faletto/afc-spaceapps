import { useEffect, useState } from 'react';
import { loadDetailTile, type DetailRecord } from '../data/loader';
import { dataSource } from '../data/source';
import type { Columns, Tier } from '../data/types';
import { formatPrice } from '../map/markers';
import { factsLine } from '../results/format';
import { Badges } from './Badges';
import { Facts } from './Facts';
import { FinePrint, InfoIcon } from './FinePrint';
import { Gallery } from './Gallery';
import { Scores } from './Scores';
import { RentBlock } from '../rent/RentBlock';
import { RentHistory } from '../rent/RentHistory';
import { usePlotRentData } from '../rent/usePlotRentData';
import { useStore } from '../state/store';

export function Listing({ cols, tier, i, onBack }: { cols: Columns; tier: Tier; i: number; onBack: () => void }) {
  const [detail, setDetail] = useState<DetailRecord | null>(null);
  useEffect(() => {
    let live = true;
    setDetail(null);
    const tile = cols.col.tile[i]!, row = cols.col.row_in_tile[i]!;
    loadDetailTile(dataSource, tier, tile, cols.meta.tiles_per_axis).then((rs) => { if (live) setDetail(rs[row] ?? null); }).catch((e) => console.warn('detail not loaded', e));
    return () => { live = false; };
  }, [cols, tier, i]);

  useEffect(() => {
    const k = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement | null;
      if (e.key === 'Escape' && !(t && ['INPUT', 'SELECT', 'TEXTAREA'].includes(t.tagName))) onBack();
    };
    window.addEventListener('keydown', k);
    return () => window.removeEventListener('keydown', k);
  }, [onBack]);

  const rentTab = useStore((s) => s.tab === 'rent');
  const rentData = usePlotRentData(cols, tier, i, detail);
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
        {detail?.nearest_feature
          ? <div data-testid="nearby" style={{ fontSize: 12, opacity: 0.8 }}>Nearest feature: {detail.nearest_feature}{detail.nearest_km != null ? `, ${detail.nearest_km.toFixed(0)} km` : ''}</div>
          : detail?.nearby?.length ? <div data-testid="nearby" style={{ fontSize: 12, opacity: 0.8 }}>Near {detail.nearby.slice(0, 3).join(', ')}</div> : null}
      </header>
      <section>
        <div data-testid="listing-price" style={{ fontSize: 32, fontWeight: 800 }}>
          {off ? 'Off market' : formatPrice(cols.col.price[i]!)} <InfoIcon />
        </div>
        {rentTab && !off && <div style={{ fontSize: 12, opacity: 0.7 }}>Buy Moonstimate</div>}
        <div style={{ fontSize: 14 }}>{factsLine(cols, i)}</div>
        <div style={{ marginTop: 4 }}><FinePrint compact /></div>
        {detail?.why && <p data-testid="why" style={{ margin: '8px 0 0', fontSize: 14 }}>{detail.why}</p>}
        {detail?.blurb && <p data-testid="blurb" style={{ margin: '6px 0 0', fontStyle: 'italic', opacity: 0.85 }}>{detail.blurb}</p>}
      </section>
      <Gallery
        photo={<div style={{ padding: 16, borderRadius: 6, background: '#1a2030', color: '#9aa3b8', fontSize: 13 }}>No photos from the Moon yet. {tier === 'polar' ? 'Try the 3D Tour.' : ''}</div>}
        tour={tier === 'polar' && detail?.best_cell_xy ? { tile: cols.col.tile[i]!, rowInTile: cols.col.row_in_tile[i]!, tilesPerAxis: cols.meta.tiles_per_axis, bestXY: detail?.best_cell_xy, lat, lon } : null}
      />
      {rentTab && !off && <RentBlock data={rentData} cols={cols} i={i} />}
      <Scores cols={cols} i={i} tier={tier} />
      {rentData && !off && <RentHistory data={rentData} cols={cols} i={i} />}
      <section><h3 style={{ margin: '0 0 6px', fontSize: 14 }}>Facts &amp; features</h3><Facts cols={cols} i={i} detail={detail} /></section>
    </article>
  );
}
