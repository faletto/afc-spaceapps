import { Term } from '../ui/Term';
import type { Columns, Tier } from '../data/types';

const SCORES = [
  ['s_safety', 'Landing Score', 'landing'],
  ['s_power', 'Sun Score', 'sun_score'],
  ['s_comms', 'Signal Score', 'signal'],
  ['s_thermal', 'Comfort Score', 'comfort'],
  ['s_landmark', 'Views Score', 'views'],
  ['s_ice', 'Ice Score', 'ice_score'],
] as const;

export function Scores({ cols, i, tier }: { cols: Columns; i: number; tier: Tier }) {
  return (
    <div>
      <div style={{ fontSize: 13, opacity: 0.7 }}><Term id="viability">Viability Score</Term></div>
      <div style={{ fontSize: 28, fontWeight: 700 }} data-testid="viability">{cols.col.viability[i]}<span style={{ fontSize: 14, opacity: 0.6 }}> / 100</span></div>
      <ul style={{ listStyle: 'none', padding: 0, margin: '8px 0 0', display: 'grid', gap: 6 }}>
        {SCORES.filter(([k]) => k !== 's_ice' || tier === 'polar').map(([k, label, term]) => {
          const v = cols.col[k][i]!;
          return (
            <li key={k} style={{ display: 'grid', gridTemplateColumns: '110px 1fr 32px', alignItems: 'center', gap: 8, fontSize: 13 }}>
              <span><Term id={term}>{label}</Term></span>
              <span style={{ background: '#262c38', height: 8, borderRadius: 4 }}>
                <span style={{ display: 'block', width: `${v}%`, height: '100%', background: '#78beff', borderRadius: 4 }} />
              </span>
              <span style={{ textAlign: 'right' }}>{v}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
