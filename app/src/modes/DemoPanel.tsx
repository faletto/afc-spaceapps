import { useEffect, useState } from 'react';
import type { Columns, Tier } from '../data/types';
import { useStore } from '../state/store';
import { SCENARIOS, shiftMoveIn } from './scenarios';

/** ?demo=1: one-click buttons for the live-demo script. Switches tier first, then runs once that tier's data is loaded. */
export function DemoPanel({ data }: { data: Partial<Record<Tier, Columns>> }) {
  const tier = useStore((s) => s.tier), setTier = useStore((s) => s.setTier), tab = useStore((s) => s.tab);
  const [pending, setPending] = useState<string | null>(null);
  useEffect(() => {
    if (!pending) return;
    const sc = SCENARIOS.find((x) => x.id === pending)!;
    const c = data[sc.tier];
    if (tier !== sc.tier || !c) return;
    setPending(null);
    void sc.run(c);
  }, [pending, tier, data]);
  return (
    <div role="group" aria-label="Demo scenarios" data-testid="demo-panel" style={{ position: 'absolute', top: 12, right: 12, zIndex: 6, display: 'flex', gap: 6, flexWrap: 'wrap', justifyContent: 'flex-end', maxWidth: '55%' }}>
      {SCENARIOS.map((sc) => (
        <button key={sc.id} type="button" data-testid={`demo-${sc.id}`} onClick={() => { if (tier !== sc.tier) setTier(sc.tier); setPending(sc.id); }}>{sc.label}</button>
      ))}
      <button type="button" data-testid="demo-shift" disabled={tab !== 'rent'} onClick={shiftMoveIn}>Shift move-in +2 weeks</button>
    </div>
  );
}
