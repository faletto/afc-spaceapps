import { useMemo } from 'react';
import type { Columns } from '../data/types';
import { formatPrice } from '../map/markers';
import { MONTH_START_DAY, plotRent } from './plotRent';
import type { PlotRentData } from './usePlotRentData';

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

/** DET-7: Rent Moonstimate for a 30-day stay starting on the 1st of each month. */
export function RentHistory({ data, cols, i }: { data: PlotRentData; cols: Columns; i: number }) {
  const vals = useMemo(() => MONTH_START_DAY.map((d) => plotRent(data.site, data.eph, data.cfg, cols, i, d, 30, data.year).perMonth), [data, cols, i]);
  const max = Math.max(...vals), W = 300, H = 90, bw = W / 12;
  return (
    <section aria-label="Rent history">
      <h3 style={{ margin: '0 0 6px', fontSize: 14 }}>Rent history <span style={{ fontWeight: 400, opacity: 0.7, fontSize: 12 }}>(30-day stay starting each month)</span></h3>
      <svg data-testid="rent-history" viewBox={`0 0 ${W} ${H + 16}`} style={{ width: '100%', maxWidth: 420 }} role="img" aria-label="Rent per month by move-in month">
        {vals.map((v, k) => {
          const h = max > 0 ? (v / max) * H : 0;
          return (
            <g key={k}>
              <rect x={k * bw + 2} y={H - h} width={bw - 4} height={h} fill="#78beff"><title>{`${MONTHS[k]}: ${formatPrice(v)}/mo`}</title></rect>
              <text x={k * bw + bw / 2} y={H + 12} fontSize="8" textAnchor="middle" fill="#9aa3b8">{MONTHS[k]![0]}</text>
            </g>
          );
        })}
      </svg>
      <div style={{ fontSize: 11, opacity: 0.7 }}>Peak {formatPrice(max)}/mo · low {formatPrice(Math.min(...vals))}/mo</div>
    </section>
  );
}
