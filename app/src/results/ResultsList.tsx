/** Virtualized, two-column results list with the sort control; hover and selection state live in each card, not here. */
import { useEffect, useRef, useState } from 'react';
import { List, type RowComponentProps } from 'react-window';
import type { Columns, Tier } from '../data/types';
import { useShallow } from 'zustand/react/shallow';
import { useStore, type SortKey } from '../state/store';
import { ListingCard } from './ListingCard';
import { PlotsForYou } from './PlotsForYou';
import { RESULT_CAP } from './query';

const SORTS: [SortKey, string][] = [
  ['price_desc', 'Price (high to low)'], ['price_asc', 'Price (low to high)'],
  ['viability_desc', 'Viability'], ['sun_score_desc', 'Sun Score'], ['signal_score_desc', 'Signal Score'],
];
const BEST_MATCH: [SortKey, string] = ['best_match', 'Best match'];
const EMPTY: number[] = [];
const COLS = 2, ROW_H = 220;

interface RowProps {
  ids: number[]; match: number[]; cols: Columns; tier: Tier; basemapUrl: string | null;
  setHover: (i: number | null) => void; select: (i: number | null) => void;
}

function Row({ index, style, ids, match, cols, tier, basemapUrl, setHover, select }: RowComponentProps<RowProps>) {
  return (
    <div style={{ ...style, display: 'grid', gridTemplateColumns: `repeat(${COLS}, 1fr)`, gap: 10, padding: '0 12px', boxSizing: 'border-box' }}>
      {ids.slice(index * COLS, index * COLS + COLS).map((i, k) => (
        <ListingCard
          key={i} cols={cols} tier={tier} i={i} basemapUrl={basemapUrl}
          onHover={setHover} onOpen={select} match={match[index * COLS + k]}
        />
      ))}
    </div>
  );
}

export function ResultsList({ cols, tier, basemapUrl }: { cols: Columns; tier: Tier; basemapUrl: string | null }) {
  const { sort, setSort, setHover, select } = useStore(useShallow((s) => ({ sort: s.sort, setSort: s.setSort, setHover: s.setHover, select: s.select })));
  const results = useStore((s) => s.results);
  const homeType = useStore((s) => s.filters.homeType);
  const quiet = useStore((s) => { const f = s.filters; return f.priceMin == null && f.priceMax == null && !f.landTypes.length && !f.hideOff && f.homeType === 'any' && !f.minSun && !f.minEarth; });
  const ids = results?.ids ?? EMPTY, match = results?.match ?? EMPTY, total = results?.total ?? 0;
  const box = useRef<HTMLDivElement>(null);
  const [h, setH] = useState(400);
  useEffect(() => {
    const ro = new ResizeObserver(() => setH(box.current!.clientHeight));
    ro.observe(box.current!);
    return () => ro.disconnect();
  }, []);
  const rows = Math.ceil(ids.length / COLS);

  return (
    <section aria-label="Lunar real estate" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <header style={{ padding: '16px 12px 10px' }}>
        <h2 style={{ margin: 0, fontSize: 20, fontWeight: 800 }}>Lunar real estate</h2>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 4 }}>
          <span data-testid="count" className="muted">
            {total.toLocaleString()} results{total > RESULT_CAP ? ` · Showing ${RESULT_CAP} of ${total.toLocaleString()}` : ''}
          </span>
          <label>
            Sort:{' '}
            <select value={sort} onChange={(e) => setSort(e.target.value as SortKey)}>
              {(homeType !== 'any' ? [BEST_MATCH, ...SORTS] : SORTS).map(([k, label]) => <option key={k} value={k}>{label}</option>)}
            </select>
          </label>
        </div>
      </header>
      {quiet && <PlotsForYou cols={cols} tier={tier} onOpen={select} />}
      {results && total === 0 && (
        <p data-testid="empty" className="muted" style={{ margin: 0, padding: '0 12px 8px', fontSize: 13 }}>Nothing matches in this part of the map. Zoom out, press “Whole map”, or loosen the filters.</p>
      )}
      <div ref={box} style={{ flex: 1, minHeight: 0 }}>
        <List
          style={{ height: h }} rowComponent={Row} rowCount={rows} rowHeight={ROW_H} overscanCount={2}
          rowProps={{ ids, match, cols, tier, basemapUrl, setHover, select }}
        />
      </div>
    </section>
  );
}
