import type { ColArray, ColsJson, Columns, ColumnName, Manifest, Tier } from './types';
import { COLUMN_DTYPES } from './types';

export const EXPECTED_CONTRACT = 1;

/** Injectable I/O so tests can run in Node and the app can run in the browser. */
export interface Source { json<T>(path: string): Promise<T>; bin(path: string): Promise<ArrayBuffer> }

export function httpSource(base = import.meta.env.BASE_URL + 'data/'): Source {
  const get = async (p: string) => {
    const r = await fetch(base + p);
    if (!r.ok) throw new Error(`load ${p}: HTTP ${r.status}`);
    return r;
  };
  return { json: async <T>(p: string) => (await get(p)).json() as Promise<T>, bin: async (p) => (await get(p)).arrayBuffer() };
}

export async function loadManifest(src: Source): Promise<Manifest> {
  const m = await src.json<Manifest>('manifest.json');
  if (m.contract_version !== EXPECTED_CONTRACT) {
    console.warn(`Data contract v${m.contract_version} != built-for v${EXPECTED_CONTRACT}`);
  }
  return m;
}

const CTORS = { float32: Float32Array, uint8: Uint8Array, uint16: Uint16Array } as const;

/** Decode cols.bin into zero-copy typed-array views, one per column. */
export function decodeColumns(meta: ColsJson, buf: ArrayBuffer): Columns {
  const col = {} as Record<string, ColArray>;
  const scales: Record<string, number> = {};
  for (const c of meta.columns) {
    const C = CTORS[c.dtype];
    col[c.name] = new C(buf, c.offset, meta.rows);
    scales[c.name] = c.scale;
  }
  for (const name of Object.keys(COLUMN_DTYPES)) {
    if (!(name in col)) throw new Error(`cols.json missing column "${name}"`);
  }
  return { rows: meta.rows, meta, scales, col: col as Columns['col'] };
}

const cache = new Map<string, Promise<unknown>>();
const memo = <T>(key: string, f: () => Promise<T>): Promise<T> => {
  if (!cache.has(key)) cache.set(key, f().catch((e) => { cache.delete(key); throw e; }));
  return cache.get(key) as Promise<T>;
};
export const clearCache = () => cache.clear();

export function loadTier(src: Source, tier: Tier): Promise<Columns> {
  return memo(`cols:${tier}`, async () => {
    const [meta, buf] = await Promise.all([
      src.json<ColsJson>(`${tier}/cols.json`), src.bin(`${tier}/cols.bin`),
    ]);
    return decodeColumns(meta, buf);
  });
}

export interface Ephemeris { sun: Float32Array; earth: Float32Array; earthDistM: Float32Array; tsi: Float32Array }
export function loadEphemeris(src: Source, steps: number): Promise<Ephemeris> {
  return memo('eph', async () => {
    const b = await src.bin('ephemeris.bin');
    const f = (i: number, n: number) => new Float32Array(b, i * steps * 4, n * steps);
    return { sun: f(0, 3), earth: f(3, 3), earthDistM: f(6, 1), tsi: f(7, 1) };
  });
}

export interface DetailRecord { row: number; name: string; blurb: string; sunlit_monthly: number[]; [k: string]: unknown }
export const tileName = (tile: number, tilesPerAxis: number) => `${tile % tilesPerAxis}_${Math.floor(tile / tilesPerAxis)}`;

/** Lazy per-tile detail; tiles with no file (empty polar corners) resolve to []. */
export function loadDetailTile(src: Source, tier: Tier, tile: number, tilesPerAxis: number): Promise<DetailRecord[]> {
  return memo(`detail:${tier}:${tile}`, () =>
    src.json<DetailRecord[]>(`${tier}/detail/${tileName(tile, tilesPerAxis)}.json`).catch(() => []));
}

/** Horizon tile: elevation_deg = v * unit_deg + offset_deg, 180 azimuth samples per plot. */
export function loadHorizonTile(src: Source, tile: number, tilesPerAxis: number): Promise<Uint8Array> {
  return memo(`hor:${tile}`, async () =>
    new Uint8Array(await src.bin(`polar/horizon/${tileName(tile, tilesPerAxis)}.bin`).catch(() => new ArrayBuffer(0))));
}

/** Plot index → ordinal value in real units. */
export const value = (c: Columns, name: ColumnName, i: number) => c.col[name][i]! * (c.scales[name] ?? 1);
