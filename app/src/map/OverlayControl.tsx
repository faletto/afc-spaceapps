import { useEffect, useState } from 'react';
import { loadLegend, OVERLAY_NAMES } from '../data/loader';
import { dataSource } from '../data/source';
import type { OverlayLegend, Tier } from '../data/types';
import { useStore } from '../state/store';
import { OVERLAY_INFO } from './overlayMeta';

export const rampGradient = (ramp: OverlayLegend['ramp']) =>
  `linear-gradient(to right, ${ramp.map(([t, c]) => `${c} ${Math.round(t * 100)}%`).join(', ')})`;

function Legend({ tier }: { tier: Tier }) {
  const overlay = useStore((s) => s.overlay);
  const [legend, setLegend] = useState<OverlayLegend | null>(null);
  useEffect(() => {
    let live = true;
    setLegend(null);
    if (overlay) loadLegend(dataSource, tier, overlay).then((l) => live && setLegend(l)).catch(() => undefined);
    return () => { live = false; };
  }, [overlay, tier]);
  if (!overlay || !legend) return null;
  return (
    <div data-testid="legend" style={{ marginTop: 8, width: 240 }}>
      <div style={{ fontWeight: 600 }}>{OVERLAY_INFO[overlay].label} <span style={{ opacity: 0.7 }}>({legend.unit})</span></div>
      <div role="img" aria-label={`Color ramp from ${legend.min} to ${legend.max} ${legend.unit}`}
        style={{ height: 10, borderRadius: 3, margin: '4px 0', background: rampGradient(legend.ramp) }} />
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11 }}><span>{legend.min}</span><span>{legend.max}</span></div>
      <div style={{ fontSize: 11, opacity: 0.8, marginTop: 4 }}>{OVERLAY_INFO[overlay].blurb}</div>
    </div>
  );
}

export function OverlayControl({ tier }: { tier: Tier }) {
  const { overlay, setOverlay, overlayOpacity, setOverlayOpacity } = useStore();
  return (
    <div style={{ position: 'absolute', left: 12, top: 56, background: 'rgba(11,13,18,0.85)', padding: 8, borderRadius: 8, fontSize: 13 }}>
      <label>
        Overlay:{' '}
        <select aria-label="Overlay" value={overlay ?? ''} onChange={(e) => setOverlay((e.target.value || null) as typeof overlay)}>
          <option value="">None</option>
          {OVERLAY_NAMES.filter((n) => !OVERLAY_INFO[n].polarOnly || tier === 'polar').map((n) => (
            <option key={n} value={n}>{OVERLAY_INFO[n].label}</option>))}
        </select>
      </label>
      {overlay && (
        <label style={{ display: 'block', marginTop: 6 }}>
          Opacity{' '}
          <input type="range" aria-label="Overlay opacity" min={0} max={1} step={0.05} value={overlayOpacity}
            onChange={(e) => setOverlayOpacity(Number(e.target.value))} />
        </label>
      )}
      <Legend tier={tier} />
    </div>
  );
}
