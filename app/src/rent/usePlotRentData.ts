import { useEffect, useState } from 'react';
import { loadConfig, loadEphemeris, loadHorizonTile, type AppConfig, type DetailRecord } from '../data/loader';
import { dataSource } from '../data/source';
import type { Columns, Tier } from '../data/types';
import { polarXYToLatLon } from '../geo/projections';
import type { RentSite } from '../science/rent';
import { decodeHorizon, HOURS_2028, type Eph } from '../science/visibility';
import { siteFromColumns, yearRent } from './plotRent';
import type { RentResult } from '../science/rent';

export interface PlotRentData { site: RentSite; eph: Eph; cfg: AppConfig; year: RentResult }

/**
 * Everything the client needs to price a stay for one plot: config, ephemeris, the plot's best cell + horizon
 * (polar: from the detail record and horizon tile; Moon-wide: plot centre, smooth Moon) and the full-year reference.
 * false if the plot has no horizon data, null while loading, and for polar plots until `detail` (best cell) has arrived.
 */
export function usePlotRentData(cols: Columns, tier: Tier, i: number, detail: DetailRecord | null): PlotRentData | null | false {
  const [data, setData] = useState<PlotRentData | null | false>(null);
  const bx = detail?.best_cell_xy?.[0], by = detail?.best_cell_xy?.[1];
  useEffect(() => {
    if (tier === 'polar' && (bx == null || by == null)) return;
    let live = true;
    setData(null);
    const tile = cols.col.tile[i]!, row = cols.col.row_in_tile[i]!, tpa = cols.meta.tiles_per_axis;
    Promise.all([loadConfig(dataSource), loadEphemeris(dataSource, HOURS_2028), tier === 'polar' ? loadHorizonTile(dataSource, tile, tpa) : Promise.resolve(null)])
      .then(([cfg, eph, hzTile]) => {
        if (!live) return;
        let lat = cols.col.y[i]!, lon = cols.col.x[i]!, hz: ArrayLike<number> | null = null;
        if (tier === 'polar') {
          const q = hzTile!.subarray(row * 180, row * 180 + 180);
          if (q.length < 180) { setData(false); return; }
          ({ lat, lon } = polarXYToLatLon(bx!, by!));
          hz = decodeHorizon(q);
        }
        const site = siteFromColumns(cols, i, tier, lat, lon, hz);
        setData({ site, eph, cfg, year: yearRent(site, eph, cfg) });
      })
      .catch((e) => console.warn('rent data not loaded', e));
    return () => { live = false; };
  }, [cols, tier, i, bx, by]);
  return data;
}
