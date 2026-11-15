import { useEffect, useState } from 'react';
import { loadManifest, loadTier } from './data/loader';
import { dataBase as base, dataSource as src } from './data/source';
import { Filters } from './header/Filters';
import { TimeSlider } from './header/TimeSlider';
import { FinePrint } from './listing/FinePrint';
import { OverlayControl } from './map/OverlayControl';
import { loadGlossary } from './ui/glossary';
import { Notice } from './listing/Notice';
import { Listing } from './listing/Listing';
import type { Columns, Tier } from './data/types';
import { useBasemap } from './map/useBasemap';
import { MapView } from './map/MapView';
import { useResultsQuery } from './results/useResults';
import { ResultsList } from './results/ResultsList';
import { useShallow } from 'zustand/react/shallow';
import { useStore } from './state/store';
import { DemoPanel } from './modes/DemoPanel';
import { MODE, PRESENT_ZOOM } from './modes/mode';

export function App() {
  const { tier, setTier, selection, select } = useStore(useShallow((s) => ({ tier: s.tier, setTier: s.setTier, selection: s.selection, select: s.select })));
  const [data, setData] = useState<Partial<Record<Tier, Columns>>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { void loadGlossary(src); }, []);

  useEffect(() => {
    loadManifest(src).then(() => loadTier(src, tier)).then((c) => setData((d) => ({ ...d, [tier]: c }))).catch((e) => setError(String(e)));
  }, [tier]);

  const cols = data[tier];
  useResultsQuery(tier, cols);
  const basemaps = useBasemap(tier, base);
  const results = useStore((s) => s.results);
  return (
    <div style={{ position: 'fixed', inset: 0, display: 'grid', gridTemplateColumns: '1fr minmax(380px, 36%)', gridTemplateRows: 'auto 1fr', color: 'var(--text)', background: 'var(--bg)' }} data-mode={MODE.present ? 'present' : MODE.demo ? 'demo' : undefined}>
      <header className="topbar" style={{ gridColumn: '1 / -1', zoom: MODE.present ? PRESENT_ZOOM : undefined }}>
        <img src={`${import.meta.env.BASE_URL}logo.png`} alt="Lunar Listings" data-testid="logo" />
        <Filters cols={cols} />
      </header>
      <div style={{ position: 'relative' }}>
        {/* Mount the map after the first results so the list paints before deck.gl's (slow on software GL) first render. */}
        {cols && results && <MapView key={tier} tier={tier} cols={cols} basemapUrl={basemaps.full ?? basemaps.small} />}
        {cols && <OverlayControl tier={tier} />}
        {cols && <TimeSlider />}
        {MODE.demo && <DemoPanel data={data} />}
        <div className="panel" style={{ position: 'absolute', top: 12, left: 12, display: 'flex', gap: 8, alignItems: 'center', padding: 6 }}>
          {(['global', 'polar'] as const).map((t) => (
            <button key={t} onClick={() => setTier(t)} aria-pressed={tier === t} style={{ padding: '6px 14px' }}>
              {t === 'global' ? 'Moon-wide' : 'South Pole District'}
            </button>
          ))}
          {!cols && !error && <span>Loading…</span>}
          {error && <span role="alert">{error}</span>}
          {cols && selection != null && !MODE.present && <span data-testid="selected">Selected plot #{selection}</span>}
        </div>
      </div>
      <aside style={{ borderLeft: '1px solid var(--border)', background: 'var(--surface)', minHeight: 0, display: 'flex', flexDirection: 'column', zoom: MODE.present ? PRESENT_ZOOM : undefined }}>
        <div style={{ flex: 1, minHeight: 0 }}>
        {cols && selection != null
          ? <Listing key={selection} cols={cols} tier={tier} i={selection} onBack={() => select(null)} />
          : cols && <ResultsList key={tier} cols={cols} tier={tier} basemapUrl={basemaps.small ?? basemaps.full} />}
        </div>
        <footer style={{ padding: '8px 12px', borderTop: '1px solid var(--border)' }}><FinePrint compact /></footer>
      </aside>
      <Notice />
    </div>
  );
}
