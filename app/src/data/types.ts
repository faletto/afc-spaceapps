// Mirrors docs/technical-spec.md §5 (contract v0/v1). Do not invent fields: request them in app-log.md.
export type Dtype = 'float32' | 'uint8' | 'uint16';

export interface ColumnMeta { name: string; dtype: Dtype; offset: number; scale?: number }
export interface ColsJson { rows: number; columns: ColumnMeta[] }

export interface Manifest {
  contract_version: number;
  files?: string[];
  [k: string]: unknown;
}

/** Column names shipped in global/cols.bin and polar/cols.bin. */
export const COLUMN_DTYPES = {
  x: 'float32', y: 'float32', lat: 'float32', lon: 'float32', area_km2: 'float32',
  price: 'float32', rent_avg: 'float32', viability: 'uint8',
  s_safety: 'uint8', s_power: 'uint8', s_comms: 'uint8', s_thermal: 'uint8', s_terrain: 'uint8', s_ice: 'uint8',
  sunlit_pct: 'uint8', earth_pct: 'uint8', slope_mean_ddeg: 'uint16',
  longest_dark_h: 'uint16', longest_blackout_h: 'uint16', temp_min_k: 'uint16', temp_max_k: 'uint16',
  ice_km10: 'uint16', land_type: 'uint8', flags: 'uint16',
  bw_lander_h: 'uint16', bw_habitat_h: 'uint16', bw_lander_start: 'uint16', bw_habitat_start: 'uint16',
  tile: 'uint16', row_in_tile: 'uint16',
} as const satisfies Record<string, Dtype>;
// NOTE: the s_* column names are ASSUMED (spec elides "s_safety … s_ice"); confirm with Pipeline Claude.

export type ColumnName = keyof typeof COLUMN_DTYPES;
export type Columns = { rows: number } & { [K in ColumnName]: Float32Array | Uint8Array | Uint16Array };
export const ICE_NA = 65535;
export type Tier = 'global' | 'polar';
