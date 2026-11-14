import { readFileSync, existsSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import type { ColsJson } from '../data/types';
import { queryResults } from '../results/query';
import { decodeColumns } from '../data/loader';
import { makeHandler } from './compute';

const root = new URL('../../public/data/global/', import.meta.url).pathname;
describe.skipIf(!existsSync(root + 'cols.bin'))('compute handler', () => {
  const meta = JSON.parse(readFileSync(root + 'cols.json', 'utf8')) as ColsJson;
  const b = readFileSync(root + 'cols.bin');
  const buffer = () => b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength) as ArrayBuffer;

  it('answers queries identically to the direct call', () => {
    const h = makeHandler();
    expect(h({ type: 'init', tier: 'global', meta, buffer: buffer() })).toBeNull();
    const r = h({ type: 'query', id: 7, tier: 'global', rect: null, sort: 'price_asc' });
    const direct = queryResults(decodeColumns(meta, buffer()), null, 'price_asc');
    expect(r).toEqual({ type: 'result', id: 7, ...direct });
    expect(direct.ids.length).toBe(200);
  });
  it('errors on uninitialised tier', () => {
    expect(makeHandler()({ type: 'query', id: 1, tier: 'polar', rect: null, sort: 'price_asc' })).toMatchObject({ type: 'error', id: 1 });
  });
  it('full query over 64.8k rows is fast', () => {
    const c = decodeColumns(meta, buffer());
    const t = performance.now(); queryResults(c, null, 'viability_desc');
    expect(performance.now() - t).toBeLessThan(200);
  });
});
