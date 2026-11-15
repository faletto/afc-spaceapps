import type { Columns } from '../data/types';
import { factsParts } from '../results/format';
import { Term } from '../ui/Term';

/** Headline facts as labelled tiles: a number plus what it measures, so "51%" is never ambiguous. */
export function FactTiles({ cols, i }: { cols: Columns; i: number }) {
  const f = factsParts(cols, i);
  const tiles: [string, React.ReactNode][] = [
    [f.sun, <><Term id="sunlight">of the year in sunlight</Term></>],
    [f.earth, <><Term id="earth_contact">of the year Earth is in view</Term></>],
    [f.slope, <><Term id="slope">average ground slope</Term></>],
    [f.area, 'plot area'],
  ];
  return (
    <div data-testid="facts" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(110px, 1fr))', gap: 8, marginTop: 8 }}>
      {tiles.map(([v, label], k) => (
        <div key={k} className="block" style={{ padding: '8px 10px' }}>
          <div style={{ fontSize: 20, fontWeight: 800, letterSpacing: '-0.02em', color: 'var(--accent)' }}>{v}</div>
          <div className="muted" style={{ fontSize: 12, lineHeight: 1.3 }}>{label}</div>
        </div>
      ))}
    </div>
  );
}
