import { describe, expect, it } from 'vitest';
import { countdown } from './tourModel';

describe('countdown', () => {
  const m = Uint8Array.from([1, 1, 1, 0, 0, 1]);
  it('sets / rises', () => {
    expect(countdown(m, 0, 'Sun', ['sets', 'rises'])).toBe('Sun sets in 3 h');
    expect(countdown(m, 3, 'Sun', ['sets', 'rises'])).toBe('Sun rises in 2 h');
  });
  it('never changes', () => {
    expect(countdown(Uint8Array.from([1, 1]), 0, 'Sun', ['sets', 'rises'])).toMatch(/stays up/);
    expect(countdown(Uint8Array.from([0, 0]), 0, 'Earth', ['sets', 'rises'])).toMatch(/out of sight/);
  });
  it('long waits in days', () => {
    expect(countdown(Uint8Array.from([...new Array(100).fill(0), 1]), 0, 'Sun', ['sets', 'rises'])).toBe('Sun rises in 4 days');
  });
});
