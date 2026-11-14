import { useEffect, useState } from 'react';
import type { Tier } from '../data/types';

/**
 * Downloads the tier basemap ONCE and returns a blob: URL shared by the map (deck.gl) and the card thumbnails
 * (CSS). Loading them separately fetches the ~9 MB JPEG twice (different request modes → separate cache entries).
 * Returns null until loaded, so the list and markers are never blocked on it.
 */
export function useBasemap(tier: Tier, base: string): string | null {
  const [url, setUrl] = useState<string | null>(null);
  useEffect(() => {
    let live = true, made: string | null = null;
    setUrl(null);
    fetch(`${base}${tier}/basemap.jpg`).then((r) => (r.ok ? r.blob() : Promise.reject(new Error(`basemap ${r.status}`)))).then((b) => {
      if (!live) return;
      made = URL.createObjectURL(b);
      setUrl(made);
    }).catch((e) => console.warn('basemap not loaded', e));
    return () => { live = false; if (made) URL.revokeObjectURL(made); };
  }, [tier, base]);
  return url;
}
