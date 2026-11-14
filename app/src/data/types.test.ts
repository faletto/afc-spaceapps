import { describe, expect, it } from 'vitest';
import { COLUMN_DTYPES } from './types';
describe('types', () => { it('lists the 30 spec columns', () => { expect(Object.keys(COLUMN_DTYPES).length).toBe(30); }); });
