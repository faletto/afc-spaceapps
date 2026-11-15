import { HOURS_2028 } from '../science/visibility';
import { moveInDay, useStore } from '../state/store';

export const dateLabel = (t: number) => new Date(Date.UTC(2028, 0, 1, t)).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' });
export const STAYS: [number, string][] = [[14, '2 weeks'], [30, '1 month'], [90, '3 months'], [366, '1 year']];

/** TIME-1 slider (hourly over 2028; rent uses the day). On Rent it is the move-in date (RENT-1) and a stay length appears. Never touches Buy prices (D-6). */
export function TimeSlider() {
  const { t, setT, tab, stayDays, setStay } = useStore();
  return (
    <div role="group" aria-label="Time" style={{ position: 'absolute', left: 12, right: 12, bottom: 12, display: 'flex', gap: 12, alignItems: 'center', background: '#161a22e6', border: '1px solid #262c38', borderRadius: 8, padding: '6px 10px', fontSize: 13 }}>
      <span data-testid="time-label" style={{ minWidth: 190 }}>{tab === 'rent' ? 'Move-in' : 'Time'}: {dateLabel(t)}{tab === 'rent' ? '' : ` ${String(t % 24).padStart(2, '0')}:00 UTC`}</span>
      <input type="range" aria-label="Time" min={0} max={HOURS_2028 - 1} step={1} value={t} onChange={(e) => setT(Number(e.target.value))} style={{ flex: 1 }} />
      {tab === 'rent' && (
        <label>
          Stay{' '}
          <select aria-label="Stay length" value={stayDays} onChange={(e) => setStay(Number(e.target.value))}>
            {STAYS.map(([d, l]) => <option key={d} value={d}>{l}</option>)}
          </select>
        </label>
      )}
      <span style={{ opacity: 0.6 }}>day {moveInDay(t)}</span>
    </div>
  );
}
