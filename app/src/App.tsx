import { useEffect, useState } from 'react';
import { loadManifest, loadTier } from './data/loader';
import { dataBase as base, dataSource as src } from './data/source';
import { FinePrint } from './listing/FinePrint';
import { OverlayControl } from './map/OverlayControl';
import { Notice } from './listing/Notice';
import { Listing } from './listing/Listing';
import type { Columns, Tier } from './data/types';
import { MapView } from './map/MapView';
import { ResultsList } from './results/ResultsList';
import { useStore } from './state/store';

export function App() {
  const { tier, setTier, selection, select } = useStore();
  const [data, setData] = useState<Partial<Record<Tier, Columns>>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadManifest(src).then(() => loadTier(src, tier)).then((c) => setData((d) => ({ ...d, [tier]: c }))).catch((e) => setError(String(e)));
  }, [tier]);

  const cols = data[tier];
  const basemapUrl = `${base}${tier}/basemap.jpg`;
  return (
    <div style={{ position: 'fixed', inset: 0, display: 'grid', gridTemplateColumns: '1fr minmax(380px, 36%)', color: '#eee', background: '#0b0d12', font: '14px system-ui' }}>
      <div style={{ position: 'relative' }}>
        {cols && <MapView key={tier} tier={tier} cols={cols} basemapUrl={basemapUrl} />}
        {cols && <OverlayControl tier={tier} />}
        <div style={{ position: 'absolute', top: 12, left: 12, display: 'flex', gap: 8, alignItems: 'center' }}>
          {(['global', 'polar'] as const).map((t) => (
            <button key={t} onClick={() => setTier(t)} aria-pressed={tier === t} style={{ padding: '6px 12px', fontWeight: tier === t ? 700 : 400 }}>
              {t === 'global' ? 'Moon-wide' : 'South Pole District'}
            </button>
          ))}
          {!cols && !error && <span>Loading…</span>}
          {error && <span role="alert">{error}</span>}
          {cols && selection != null && <span data-testid="selected">Selected plot #{selection}</span>}
        </div>
      </div>
      <aside style={{ borderLeft: '1px solid #262c38', minHeight: 0, display: 'flex', flexDirection: 'column' }}>
        <div style={{ flex: 1, minHeight: 0 }}>
        {cols && selection != null
          ? <Listing key={selection} cols={cols} tier={tier} i={selection} onBack={() => select(null)} />
          : cols && <ResultsList key={tier} cols={cols} tier={tier} basemapUrl={basemapUrl} />}
        </div>
        <footer style={{ padding: '8px 12px', borderTop: '1px solid #262c38' }}><FinePrint compact /></footer>
      </aside>
      <Notice />
    </div>
  );
}
