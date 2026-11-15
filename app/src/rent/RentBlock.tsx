import { useDeferredValue, useMemo } from 'react';
import type { Columns } from '../data/types';
import { dateLabel, STAYS } from '../header/TimeSlider';
import { formatPrice } from '../map/markers';
import { moveInDay, useStore } from '../state/store';
import { plotRent } from './plotRent';
import type { PlotRentData } from './usePlotRentData';

/** RENT-2/3 + Price cut badge: Rent Moonstimate for the chosen move-in and stay, with the reason it differs from the yearly average. */
export function RentBlock({ data, cols, i }: { data: PlotRentData | null | false; cols: Columns; i: number }) {
  const t = useDeferredValue(useStore((s) => s.t)), stayDays = useDeferredValue(useStore((s) => s.stayDays));
  const day = moveInDay(t);
  const r = useMemo(() => (data ? plotRent(data.site, data.eph, data.cfg, cols, i, day, stayDays, data.year) : null), [data, cols, i, day, stayDays]);
  const stayLabel = STAYS.find(([d]) => d === stayDays)?.[1] ?? `${stayDays} days`;
  if (data === false) return <section aria-label="Rent"><div role="alert">Rent estimate unavailable: no horizon data for this plot.</div></section>;
  if (!r) return <section aria-label="Rent"><div style={{ opacity: 0.7 }}>Calculating rent…</div></section>;
  const pct = Math.round(Math.abs(r.vsAvg) * 100);
  const clipped = r.stayHours < stayDays * 24;
  return (
    <section aria-label="Rent" data-testid="rent-block" className="block" style={{ display: 'grid', gap: 6, borderColor: 'var(--accent-line)' }}>
      <div className="section-title" style={{ margin: 0 }}>Rent Moonstimate · move in {dateLabel(t)} · {stayLabel}</div>
      <div style={{ display: 'flex', gap: 8, alignItems: 'baseline', flexWrap: 'wrap' }}>
        <span data-testid="listing-rent" style={{ fontSize: 30, fontWeight: 800, color: 'var(--accent)', letterSpacing: '-0.02em' }}>{formatPrice(r.perMonth)}<span style={{ fontSize: 14 }}>/mo</span></span>
        {r.priceCut && <span data-testid="price-cut" className="chip">Price cut</span>}
      </div>
      <div data-testid="rent-total" style={{ fontSize: 14 }}>{formatPrice(r.total)} for the {Math.round(r.stayHours / 24)}-day stay{clipped ? ' (cut off at 31 Dec)' : ''}</div>
      <div data-testid="rent-change" style={{ fontSize: 13, color: r.vsAvg < 0 ? 'var(--good)' : 'var(--warn)' }}>
        {pct < 3 ? 'About the 1-year average rent.' : `Rent ${r.vsAvg < 0 ? '↓' : '↑'} ${pct}% vs the 1-year average (${formatPrice(r.avg)}/mo)${r.reason ? `: ${r.reason}` : ''}.`}
      </div>
      <div style={{ fontSize: 12, opacity: 0.7 }}>Longest night {Math.round(r.stats.longest_dark_h)} h · longest blackout {Math.round(r.stats.longest_blackout_h)} h · Earth contact {Math.round(r.stats.earth_frac * 100)}% in this window. The Buy price above does not change.</div>
    </section>
  );
}
