import { useEffect, useState } from 'react';
import type { Tier } from '../data/types';

export interface Basemaps { small: string | null; full: string | null }

async function blobUrl(url: string): Promise<string> {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`);
  return URL.createObjectURL(await r.blob());
}

/**
 * Basemap blob URLs shared by the map (deck.gl) and card thumbnails (CSS), each downloaded ONCE (loading the same
 * file via fetch and via CSS downloads it twice). The small basemap (~0.3–0.7 MB) paints first and feeds the
 * thumbnails; the full-resolution one (~8 MB) arrives in the background and replaces it on the map.
 * Null until loaded, so the list and markers are never blocked. State is keyed by tier, so a stale (revoked)
 * URL from the previous tier is never returned.
 */
export function useBasemap(tier: Tier, base: string): Basemaps {
  const [state, setState] = useState<{ tier: Tier; small: string | null; full: string | null }>({ tier, small: null, full: null });
  useEffect(() => {
    let live = true;
    const made: string[] = [];
    setState({ tier, small: null, full: null });
    const load = (file: 'basemap_small.jpg' | 'basemap.jpg', key: 'small' | 'full') =>
      blobUrl(`${base}${tier}/${file}`).then((u) => {
        if (!live) { URL.revokeObjectURL(u); return; }
        made.push(u);
        setState((s) => (s.tier === tier ? { ...s, [key]: u } : s));
      }).catch((e) => console.warn(`${file} not loaded`, e));
    void load('basemap_small.jpg', 'small');
    void load('basemap.jpg', 'full');
    return () => { live = false; made.forEach((u) => URL.revokeObjectURL(u)); };
  }, [tier, base]);
  return state.tier === tier ? { small: state.small, full: state.full } : { small: null, full: null };
}
