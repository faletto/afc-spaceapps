/** Plot detail panel: price, scores, facts, blurb, price rationale and the 3D Tour. Loads the plot's detail tile lazily. */
import { useEffect, useState } from 'react';
import { loadDetailTile, type DetailRecord } from '../data/loader';
import { dataSource } from '../data/source';
import type { Columns, Tier } from '../data/types';
import { formatPrice } from '../map/markers';
import { FactTiles } from './FactTiles';
import { Badges } from './Badges';
import { Facts } from './Facts';
import { FinePrint, InfoIcon } from './FinePrint';
import { Gallery } from './Gallery';
import { Scores } from './Scores';
import { RentBlock } from '../rent/RentBlock';
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
    <article aria-label="Listing" style={{ height: '100%', overflowY: 'auto', padding: 16, boxSizing: 'border-box', display: 'grid', gap: 14, alignContent: 'start' }}>
      <button type="button" onClick={onBack} style={{ justifySelf: 'start' }}>← Back to results</button>
      <header style={{ display: 'grid', gap: 4 }}>
        <Badges cols={cols} i={i} />
        <h2 data-testid="listing-title" style={{ margin: 0, fontSize: 24, fontWeight: 800 }}>{detail?.id ? `Plot ${detail.id}` : detail?.name ?? `Plot #${i}`}</h2>
        <div className="muted" style={{ fontSize: 12 }}>
          {Math.abs(lat).toFixed(2)}°{lat < 0 ? 'S' : 'N'}, {Math.abs(lon).toFixed(2)}°{lon < 0 ? 'W' : 'E'} · {tier === 'polar' ? 'Detailed survey' : 'Moon-wide estimate'}
        </div>
        {detail?.nearest_feature
          ? <div data-testid="nearby" style={{ fontSize: 12, opacity: 0.8 }}>Nearest feature: {detail.nearest_feature}{detail.nearest_km != null ? `, ${detail.nearest_km.toFixed(0)} km` : ''}</div>
          : detail?.nearby?.length ? <div data-testid="nearby" style={{ fontSize: 12, opacity: 0.8 }}>Near {detail.nearby.slice(0, 3).join(', ')}</div> : null}
      </header>
      <section>
        <div data-testid="listing-price" style={{ fontSize: 36, fontWeight: 800, letterSpacing: '-0.03em' }}>
          {off ? 'Off market' : formatPrice(cols.col.price[i]!)} <InfoIcon />
        </div>
        {rentTab && !off && <div className="muted" style={{ fontSize: 12 }}>Buy Moonstimate</div>}
        <FactTiles cols={cols} i={i} />
        <div style={{ marginTop: 4 }}><FinePrint compact /></div>
        {detail?.why && <p data-testid="why" style={{ margin: '8px 0 0', fontSize: 14 }}>{detail.why}</p>}
        {detail?.blurb && <p data-testid="blurb" className="muted" style={{ margin: '6px 0 0', fontStyle: 'italic' }}>{detail.blurb}</p>}
      </section>
      <Gallery
        tour={tier === 'polar' && detail?.best_cell_xy ? { tile: cols.col.tile[i]!, rowInTile: cols.col.row_in_tile[i]!, tilesPerAxis: cols.meta.tiles_per_axis, bestXY: detail?.best_cell_xy, lat, lon } : null}
      />
      {rentTab && !off && <RentBlock data={rentData} cols={cols} i={i} />}
      <Scores cols={cols} i={i} tier={tier} />
      <section className="block"><h3 className="section-title">Facts &amp; features</h3><Facts cols={cols} i={i} detail={detail} /></section>
    </article>
  );
}
