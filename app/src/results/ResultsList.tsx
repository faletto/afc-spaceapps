import { useEffect, useRef, useState } from 'react';
import { List, type RowComponentProps } from 'react-window';
import type { Columns, Tier } from '../data/types';
import { useStore, type SortKey } from '../state/store';
import { ListingCard } from './ListingCard';
import { RESULT_CAP } from './query';

const SORTS: [SortKey, string][] = [
  ['price_desc', 'Price (high to low)'], ['price_asc', 'Price (low to high)'],
  ['viability_desc', 'Viability'], ['sun_score_desc', 'Sun Score'], ['signal_score_desc', 'Signal Score'],
];
const EMPTY: number[] = [];
const COLS = 2, ROW_H = 200;

interface RowProps {
  ids: number[]; cols: Columns; tier: Tier; basemapUrl: string | null;
  hover: number | null; selection: number | null;
  setHover: (i: number | null) => void; select: (i: number | null) => void;
}

function Row({ index, style, ids, cols, tier, basemapUrl, hover, selection, setHover, select }: RowComponentProps<RowProps>) {
  return (
    <div style={{ ...style, display: 'grid', gridTemplateColumns: `repeat(${COLS}, 1fr)`, gap: 10, padding: '0 12px', boxSizing: 'border-box' }}>
      {ids.slice(index * COLS, index * COLS + COLS).map((i) => (
        <ListingCard
          key={i} cols={cols} tier={tier} i={i} basemapUrl={basemapUrl}
          highlighted={hover === i} selected={selection === i} onHover={setHover} onOpen={select}
        />
      ))}
    </div>
  );
}

export function ResultsList({ cols, tier, basemapUrl }: { cols: Columns; tier: Tier; basemapUrl: string | null }) {
  const { sort, setSort, hover, selection, setHover, select } = useStore();
  const results = useStore((s) => s.results);
  const ids = results?.ids ?? EMPTY, total = results?.total ?? 0;
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
      <header style={{ padding: '12px 12px 8px' }}>
        <h2 style={{ margin: 0, fontSize: 18 }}>Lunar real estate</h2>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 4 }}>
          <span data-testid="count">
            {total.toLocaleString()} results{total > RESULT_CAP ? ` · Showing ${RESULT_CAP} of ${total.toLocaleString()}` : ''}
          </span>
          <label>
            Sort:{' '}
            <select value={sort} onChange={(e) => setSort(e.target.value as SortKey)}>
              {SORTS.map(([k, label]) => <option key={k} value={k}>{label}</option>)}
            </select>
          </label>
        </div>
      </header>
      <div ref={box} style={{ flex: 1, minHeight: 0 }}>
        <List
          style={{ height: h }} rowComponent={Row} rowCount={rows} rowHeight={ROW_H} overscanCount={2}
          rowProps={{ ids, cols, tier, basemapUrl, hover, selection, setHover, select }}
        />
      </div>
    </section>
  );
}
