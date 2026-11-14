/** "20000", "20k", "1.5M", "$2,500" → USD; "" → null; unparseable → undefined. */
export function parsePrice(text: string): number | null | undefined {
  const t = text.trim().replace(/[$,\s]/g, '').toLowerCase();
  if (!t) return null;
  const m = /^(\d+(?:\.\d+)?)([kmb]?)$/.exec(t);
  if (!m) return undefined;
  return Number(m[1]) * ({ '': 1, k: 1e3, m: 1e6, b: 1e9 } as const)[m[2] as '' | 'k' | 'm' | 'b'];
}
