/** Time slider over the 2028 analysis year (hourly). Drives the 3D Tour; never changes Buy prices (D-6). */
import { HOURS_2028 } from '../science/visibility';
import { useShallow } from 'zustand/react/shallow';
import { moveInDay, useStore } from '../state/store';

export const dateLabel = (t: number) => new Date(Date.UTC(2028, 0, 1, t)).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' });
export const STAYS: [number, string][] = [[14, '2 weeks'], [30, '1 month'], [90, '3 months'], [366, '1 year']];

/** TIME-1 slider (hourly over 2028; rent uses the day). On Rent it is the move-in date (RENT-1) and a stay length appears. Never touches Buy prices (D-6). */
export function TimeSlider() {
  const { t, setT, tab, stayDays, setStay } = useStore(useShallow((s) => ({ t: s.t, setT: s.setT, tab: s.tab, stayDays: s.stayDays, setStay: s.setStay })));
  return (
    <div role="group" aria-label="Time" className="panel" style={{ position: 'absolute', left: 12, right: 12, bottom: 12, display: 'flex', gap: 14, alignItems: 'center', padding: '8px 14px', fontSize: 13 }}>
      <span data-testid="time-label" style={{ minWidth: 190, fontWeight: 600 }}>{tab === 'rent' ? 'Move-in' : 'Time'}: {dateLabel(t)}{tab === 'rent' ? '' : ` ${String(t % 24).padStart(2, '0')}:00 UTC`}</span>
      <input type="range" aria-label="Time" min={0} max={HOURS_2028 - 1} step={1} value={t} onChange={(e) => setT(Number(e.target.value))} style={{ flex: 1 }} />
      {tab === 'rent' && (
        <label>
          Stay{' '}
          <select aria-label="Stay length" value={stayDays} onChange={(e) => setStay(Number(e.target.value))}>
            {STAYS.map(([d, l]) => <option key={d} value={d}>{l}</option>)}
          </select>
        </label>
      )}
      <span className="muted">day {moveInDay(t)}</span>
    </div>
  );
}
