import type { Columns, Tier } from '../data/types';

const SCORES = [
  ['s_safety', 'Landing Score', 'How safe the plot is to land on.'],
  ['s_power', 'Sun Score', 'How much sunlight is available for power.'],
  ['s_comms', 'Signal Score', 'How much of the year the plot can see Earth.'],
  ['s_thermal', 'Comfort Score', 'How mild the temperature swings are.'],
  ['s_landmark', 'Views Score', 'Closeness to famous landmarks.'],
  ['s_ice', 'Ice Score', 'Water ice within reach (polar plots only).'],
] as const;

export function Scores({ cols, i, tier }: { cols: Columns; i: number; tier: Tier }) {
  return (
    <div>
      <div style={{ fontSize: 13, opacity: 0.7 }}>Viability Score</div>
      <div style={{ fontSize: 28, fontWeight: 700 }} data-testid="viability">{cols.col.viability[i]}<span style={{ fontSize: 14, opacity: 0.6 }}> / 100</span></div>
      <ul style={{ listStyle: 'none', padding: 0, margin: '8px 0 0', display: 'grid', gap: 6 }}>
        {SCORES.filter(([k]) => k !== 's_ice' || tier === 'polar').map(([k, label, meaning]) => {
          const v = cols.col[k][i]!;
          return (
            <li key={k} title={meaning} style={{ display: 'grid', gridTemplateColumns: '110px 1fr 32px', alignItems: 'center', gap: 8, fontSize: 13 }}>
              <span>{label}</span>
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
