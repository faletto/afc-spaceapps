import { describe, expect, it } from 'vitest';
import { parsePrice } from './parsePrice';
describe('parsePrice', () => {
  it('parses plain, suffixed and formatted values', () => {
    expect(parsePrice('20000')).toBe(20000); expect(parsePrice('20k')).toBe(20000); expect(parsePrice('1.5M')).toBe(1.5e6);
    expect(parsePrice('$2,500')).toBe(2500); expect(parsePrice('')).toBeNull(); expect(parsePrice('  ')).toBeNull();
  });
  it('rejects junk', () => { expect(parsePrice('abc')).toBeUndefined(); expect(parsePrice('-5')).toBeUndefined(); });
});
