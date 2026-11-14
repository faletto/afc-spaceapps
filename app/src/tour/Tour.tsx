import { useEffect, useMemo, useState } from 'react';
import { loadConfig, loadEphemeris, loadHorizonTile } from '../data/loader';
import { dataSource } from '../data/source';
import { polarXYToLatLon } from '../geo/projections';
import { HOURS_2028 } from '../science/visibility';
import { TourCanvas } from './TourCanvas';
import { buildTour, earthCountdown, hourLabel, sunCountdown, type TourModel } from './tourModel';

export interface TourProps { tile: number; rowInTile: number; tilesPerAxis: number; bestXY?: [number, number]; lat: number; lon: number }

/** DET-5: 3D Tour panorama for a polar plot. Own time control until the global slider (A6) lands. */
export function Tour({ tile, rowInTile, tilesPerAxis, bestXY, lat, lon }: TourProps) {
  const [model, setModel] = useState<TourModel | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [t, setT] = useState(24 * 273); // ~30 Sep
  useEffect(() => {
    let live = true;
    setModel(null); setErr(null);
    Promise.all([loadHorizonTile(dataSource, tile, tilesPerAxis), loadEphemeris(dataSource, HOURS_2028), loadConfig(dataSource)]).then(([hz, eph, cfg]) => {
      if (!live) return;
      const q = hz.subarray(rowInTile * 180, rowInTile * 180 + 180);
      if (q.length < 180) { setErr('No horizon data for this plot.'); return; }
      const p = bestXY ? polarXYToLatLon(bestXY[0], bestXY[1]) : { lat, lon };
      setModel(buildTour(p.lat, p.lon, q, eph, cfg));
    }).catch((e) => { if (live) setErr(String(e)); });
    return () => { live = false; };
  }, [tile, rowInTile, tilesPerAxis, bestXY, lat, lon]);

  const texts = useMemo(() => (model ? [sunCountdown(model, t), earthCountdown(model, t)] : null), [model, t]);
  if (err) return <p role="alert">3D Tour unavailable: {err}</p>;
  if (!model || !texts) return <p>Loading 3D Tour…</p>;
  return (
    <div data-testid="tour" style={{ display: 'grid', gap: 6 }}>
      <TourCanvas model={model} t={t} />
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', fontSize: 14 }}>
        <strong data-testid="tour-sun">☀ {texts[0]}</strong>
        <strong data-testid="tour-earth">🌍 {texts[1]}</strong>
      </div>
      <label style={{ fontSize: 12, display: 'grid', gap: 2 }}>
        Time: {hourLabel(t)}
        <input type="range" min={0} max={HOURS_2028 - 1} step={6} value={t} onChange={(e) => setT(Number(e.target.value))} aria-label="Tour time" />
      </label>
    </div>
  );
}
