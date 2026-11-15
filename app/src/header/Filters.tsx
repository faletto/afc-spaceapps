import { useState } from 'react';
import type { Columns } from '../data/types';
import { HOME_TYPES, type HomeType } from '../results/homeTypes';
import { useStore } from '../state/store';
import { parsePrice } from './parsePrice';

const titleCase = (s: string) => s.replace(/_/g, ' ').replace(/^\w/, (c) => c.toUpperCase());

function PriceInput({ label, value, onCommit }: { label: string; value: number | null; onCommit: (v: number | null) => void }) {
  const [text, setText] = useState(value == null ? '' : String(value));
  const [bad, setBad] = useState(false);
  // Reset (value → null) clears the box.
  if (value == null && text !== '' && !bad && parsePrice(text) !== null) setText('');
  return (
    <label>
      {label}{' '}
      <input
        aria-label={label} aria-invalid={bad} inputMode="decimal" placeholder="any" value={text} size={8}
        onChange={(e) => { setText(e.target.value); const v = parsePrice(e.target.value); setBad(v === undefined); if (v !== undefined) onCommit(v); }}
        style={bad ? { outline: '2px solid #e55' } : undefined}
      />
    </label>
  );
}

/** Filter bar (FIL-1 price, FIL-2 land type, FIL-3 hide off-market). Home type / More come in A5. */
export function Filters({ cols }: { cols: Columns | undefined }) {
  const { filters, setFilters, setHomeType, resetFilters, tab, setTab } = useStore();
  const tier = useStore((s) => s.tier);
  const results = useStore((s) => s.results);
  const active = filters.priceMin != null || filters.priceMax != null || filters.landTypes.length > 0 || filters.hideOff
    || filters.homeType !== 'any' || filters.minSun > 0 || filters.minEarth > 0;
  const landTypes = cols?.meta.land_types ?? [];
  const toggleLand = (i: number) =>
    setFilters({ landTypes: filters.landTypes.includes(i) ? filters.landTypes.filter((x) => x !== i) : [...filters.landTypes, i].sort() });
  return (
    <div role="search" aria-label="Filters" style={{ display: 'flex', gap: 16, alignItems: 'center', padding: '8px 12px', borderBottom: '1px solid #262c38', flexWrap: 'wrap', fontSize: 13 }}>
      <span role="tablist" aria-label="Buy or Rent" style={{ display: 'flex', gap: 4 }}>
        {(['buy', 'rent'] as const).map((k) => (
          <button key={k} type="button" role="tab" aria-selected={tab === k} onClick={() => setTab(k)} style={{ fontWeight: tab === k ? 700 : 400 }}>{k === 'buy' ? 'Buy' : 'Rent'}</button>
        ))}
      </span>
      <span style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        Price <PriceInput label="Min price" value={filters.priceMin} onCommit={(v) => setFilters({ priceMin: v })} />
        – <PriceInput label="Max price" value={filters.priceMax} onCommit={(v) => setFilters({ priceMax: v })} />
      </span>
      <label>
        Home type{' '}
        <select aria-label="Home type" value={filters.homeType} onChange={(e) => setHomeType(e.target.value as HomeType)}>
          {HOME_TYPES.map(([k, l]) => <option key={k} value={k}>{l}</option>)}
        </select>
      </label>
      {filters.homeType === 'ice_depot' && tier === 'global' && <span role="status" style={{ opacity: 0.75 }}>Ice depots exist only in the South Pole District.</span>}
      <details style={{ position: 'relative' }}>
        <summary>Land type{filters.landTypes.length ? ` (${filters.landTypes.length})` : ''}</summary>
        <div style={{ position: 'absolute', zIndex: 10, background: '#1d2433', border: '1px solid #3a4560', borderRadius: 6, padding: 8, display: 'grid', gap: 4, minWidth: 160 }}>
          {landTypes.map((t, i) => (
            <label key={t}><input type="checkbox" checked={filters.landTypes.includes(i)} onChange={() => toggleLand(i)} /> {titleCase(t)}</label>
          ))}
        </div>
      </details>
      <details style={{ position: 'relative' }}>
        <summary>More{filters.minSun > 0 || filters.minEarth > 0 ? ' (on)' : ''}</summary>
        <div style={{ position: 'absolute', zIndex: 10, background: '#1d2433', border: '1px solid #3a4560', borderRadius: 6, padding: 8, display: 'grid', gap: 8, minWidth: 220 }}>
          <label>Min sunlight: {filters.minSun}%<br /><input type="range" aria-label="Minimum sunlight" min={0} max={100} step={5} value={filters.minSun} onChange={(e) => setFilters({ minSun: Number(e.target.value) })} /></label>
          <label>Min Earth contact: {filters.minEarth}%<br /><input type="range" aria-label="Minimum Earth contact" min={0} max={100} step={5} value={filters.minEarth} onChange={(e) => setFilters({ minEarth: Number(e.target.value) })} /></label>
        </div>
      </details>
      <label><input type="checkbox" checked={filters.hideOff} onChange={(e) => setFilters({ hideOff: e.target.checked })} /> Hide off-market plots</label>
      {active && <button type="button" onClick={() => { resetFilters(); }}>Clear filters</button>}
      {results && <span data-testid="match-count" style={{ marginLeft: 'auto', opacity: 0.75 }}>{countPassing(results.passing).toLocaleString()} plots match</span>}
    </div>
  );
}

function countPassing(mask: Uint8Array) { let n = 0; for (let i = 0; i < mask.length; i++) n += mask[i]!; return n; }
