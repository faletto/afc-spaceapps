import { useEffect, useState } from 'react';
import { httpSource, loadManifest, loadTier } from './data/loader';
import type { Columns, Tier } from './data/types';
import { MapView } from './map/MapView';
import { ResultsList } from './results/ResultsList';
import { useStore } from './state/store';

const src = httpSource();
const base = import.meta.env.BASE_URL + 'data/';

export function App() {
  const { tier, setTier, selection } = useStore();
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
      <aside style={{ borderLeft: '1px solid #262c38', minHeight: 0 }}>
        {cols && <ResultsList key={tier} cols={cols} tier={tier} basemapUrl={basemapUrl} />}
      </aside>
    </div>
  );
}
