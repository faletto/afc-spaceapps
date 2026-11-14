import { useEffect, useState } from 'react';
import { loadConfig } from '../data/loader';
import { dataSource } from '../data/source';
import type { HomeCfg } from './homeTypes';
import type { Columns, Tier } from '../data/types';
import { useStore } from '../state/store';
import { compute } from '../worker/client';

/** Runs the filter/sort/rect query in the compute worker whenever its inputs change (latest request wins). */
export function useResultsQuery(tier: Tier, cols: Columns | undefined) {
  const viewRect = useStore((s) => s.viewRect);
  const sort = useStore((s) => s.sort);
  const filters = useStore((s) => s.filters);
  const setResults = useStore((s) => s.setResults);
  const [home, setHome] = useState<HomeCfg | null>(null);
  useEffect(() => { loadConfig(dataSource).then((c) => setHome((c as unknown as { home_types: HomeCfg }).home_types)).catch((e) => console.warn('config not loaded', e)); }, []);
  useEffect(() => {
    if (!cols) return;
    let live = true;
    compute().query(tier, cols, viewRect, sort, filters, home).then((r) => live && setResults(r)).catch((e) => console.error('query failed', e));
    return () => { live = false; };
  }, [tier, cols, viewRect, sort, filters, home, setResults]);
}
