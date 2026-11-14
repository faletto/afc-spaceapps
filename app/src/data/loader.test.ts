import { readFileSync, existsSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { EXPECTED_CONTRACT, loadManifest, loadTier, loadEphemeris, loadDetailTile, tileName, value, type Source } from './loader';

const root = new URL('../../public/data/', import.meta.url).pathname;
const src: Source = {
  json: async (p) => JSON.parse(readFileSync(root + p, 'utf8')),
  bin: async (p) => { const b = readFileSync(root + p); return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength) as ArrayBuffer; },
};
const have = existsSync(root + 'manifest.json');

describe.skipIf(!have)('loader on public/data', () => {
  it('manifest matches the contract version the app is built for', async () => { expect((await loadManifest(src)).contract_version).toBe(EXPECTED_CONTRACT); });
  it('decodes both tiers with manifest row counts', async () => {
    const m = await loadManifest(src);
    for (const t of ['global', 'polar'] as const) {
      const c = await loadTier(src, t);
      expect(c.rows).toBe(m.counts[t]);
      expect(c.col.price.length).toBe(c.rows);
      expect(value(c, 'price', 0)).toBeGreaterThan(0);
    }
  });
  it('rows sorted by tile', async () => {
    const t = (await loadTier(src, 'global')).col.tile;
    for (let i = 1; i < t.length; i++) if (t[i]! < t[i - 1]!) throw new Error(`unsorted at ${i}`);
  });
  it('ephemeris + detail tile', async () => {
    const m = await loadManifest(src);
    const e = await loadEphemeris(src, m.steps as number);
    expect(e.sun.length).toBe(8784 * 3);
    const g = await loadTier(src, 'global');
    const d = await loadDetailTile(src, 'global', g.col.tile[0]!, m.tiles_per_axis);
    expect(d.length).toBeGreaterThan(0);
    expect(d[0]!.row).toBe(0);
    expect(tileName(17, 16)).toBe('1_1');
  });
});
