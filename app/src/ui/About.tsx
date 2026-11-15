import { useEffect, useRef, useState } from 'react';
import { DISCLAIMER } from '../listing/FinePrint';
import { useGlossary } from './glossary';

type View = 'about' | 'formulas' | 'validation';
const VIEWS: [View, string][] = [['about', 'About'], ['formulas', 'Formulas'], ['validation', 'Validation']];

/** PRS-5 / DET-8: what the product is, which NASA data it uses, every formula with its source, and how the numbers were checked. */
export function AboutButton() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button type="button" onClick={() => setOpen(true)} aria-haspopup="dialog">About</button>
      {open && <AboutDialog onClose={() => setOpen(false)} />}
    </>
  );
}

function AboutDialog({ onClose }: { onClose: () => void }) {
  const [view, setView] = useState<View>('about');
  const entries = useGlossary((s) => s.entries);
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    ref.current?.focus();
    const k = (e: KeyboardEvent) => { if (e.key === 'Escape') { e.stopPropagation(); onClose(); } };
    window.addEventListener('keydown', k, true);
    return () => window.removeEventListener('keydown', k, true);
  }, [onClose]);
  return (
    <div role="dialog" aria-modal="true" aria-label="About Lunar Listings" ref={ref} tabIndex={-1} data-testid="about"
      style={{ position: 'fixed', inset: 0, zIndex: 20, background: '#000a', display: 'grid', placeItems: 'center' }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div style={{ background: '#161a22', border: '1px solid #3a4560', borderRadius: 10, padding: 16, width: 'min(720px, 92vw)', maxHeight: '86vh', overflowY: 'auto', display: 'grid', gap: 10 }}>
        <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
          <div role="tablist" style={{ display: 'flex', gap: 6 }}>
            {VIEWS.map(([k, l]) => <button key={k} type="button" role="tab" aria-selected={view === k} onClick={() => setView(k)} style={{ fontWeight: view === k ? 700 : 400 }}>{l}</button>)}
          </div>
          <button type="button" onClick={onClose} style={{ marginLeft: 'auto' }}>Close</button>
        </div>
        {view === 'about' && (
          <div style={{ display: 'grid', gap: 8, fontSize: 14 }}>
            <p style={{ margin: 0 }}><strong>Lunar Listings</strong> is a Zillow-style listings site for the Moon: every plot has a Moonstimate (price), a Rent Moonstimate for a chosen stay, named scores and a 3D Tour. The premise is fictional; the numbers come from real NASA data.</p>
            <p style={{ margin: 0, fontSize: 12, opacity: 0.8 }}>{DISCLAIMER}</p>
            <h3 style={{ margin: '4px 0 0', fontSize: 14 }}>NASA datasets and how they are used</h3>
            <ul style={{ margin: 0, paddingLeft: 18, display: 'grid', gap: 4 }}>
              <li><strong>LRO LOLA elevation</strong> (NASA GSFC PGDA): terrain, slopes, roughness and the horizon around every South Pole plot, and the hillshade basemaps.</li>
              <li><strong>JPL Horizons</strong>: hourly Sun and Earth positions for 2028, giving sunlight and Earth contact.</li>
              <li><strong>LOLA illumination maps</strong> (Mazarico et al.): independent check of the polar sunlight results.</li>
              <li><strong>LRO Diviner</strong>: temperature cross-check.</li>
              <li><strong>IAU gazetteer and Apollo/Artemis sites</strong>: landmarks, nearest feature and landmark premiums.</li>
            </ul>
          </div>
        )}
        {view === 'formulas' && (
          <dl data-testid="formulas" style={{ margin: 0, display: 'grid', gap: 10, fontSize: 13 }}>
            {Object.entries(entries).map(([id, e]) => (
              <div key={id}>
                <dt style={{ fontWeight: 700 }}>{e.label}</dt>
                <dd style={{ margin: '2px 0 0' }}>{e.text}
                  {e.formula && <div style={{ fontFamily: 'ui-monospace, monospace', fontSize: 12, opacity: 0.85 }}>{e.formula}</div>}
                  {e.source && <div style={{ fontSize: 12, opacity: 0.7 }}>Source: {e.source}</div>}
                </dd>
              </div>
            ))}
          </dl>
        )}
        {view === 'validation' && (
          <div style={{ display: 'grid', gap: 8, fontSize: 14 }}>
            <p style={{ margin: 0 }}><strong>Ephemeris vs JPL Horizons (EPH-3): pass.</strong> Our Sun and Earth elevations were compared with direct Horizons topocentric queries at 7 sites × 4 dates × 48 h, from the near side to the South Pole. The largest elevation error was about 0.006°, against a limit of 0.1° at the pole.</p>
            <p style={{ margin: 0 }}><strong>South Pole lighting vs LOLA maps.</strong> Sunlight and Earth-contact fractions at every plot's best cell were cross-checked against LOLA-derived illumination averaged over each 240 m cell.</p>
            <p style={{ margin: 0 }}><strong>In this app.</strong> The browser recomputes Sun, Earth, statistics, scores and rent with the same formulas as the pipeline, and is tested against the pipeline's reference values (exact to rounding on geometry, statistics, run lengths, scoring, price and 224 rent cases).</p>
            <p style={{ margin: 0, fontSize: 12, opacity: 0.7 }}>Full report: docs/validation.md in the project repository.</p>
          </div>
        )}
      </div>
    </div>
  );
}
