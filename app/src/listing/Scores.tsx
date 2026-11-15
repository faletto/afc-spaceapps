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
    <div className="block">
      <div className="section-title"><Term id="viability">Viability Score</Term></div>
      <div style={{ fontSize: 34, fontWeight: 800, color: 'var(--accent)', letterSpacing: '-0.02em' }} data-testid="viability">{cols.col.viability[i]}<span className="muted" style={{ fontSize: 14, fontWeight: 400 }}> / 100</span></div>
      <ul style={{ listStyle: 'none', padding: 0, margin: '8px 0 0', display: 'grid', gap: 6 }}>
        {SCORES.filter(([k]) => k !== 's_ice' || tier === 'polar').map(([k, label, term]) => {
          const v = cols.col[k][i]!;
          return (
            <li key={k} style={{ display: 'grid', gridTemplateColumns: '110px 1fr 32px', alignItems: 'center', gap: 8, fontSize: 13 }}>
              <span><Term id={term}>{label}</Term></span>
              <span style={{ background: 'var(--border)', height: 8, borderRadius: 4, overflow: 'hidden' }}>
                <span style={{ display: 'block', width: `${v}%`, height: '100%', background: 'linear-gradient(90deg, #3d6fb4, var(--accent))', borderRadius: 4 }} />
              </span>
              <span style={{ textAlign: 'right' }}>{v}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
