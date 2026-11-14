import type { Columns, Tier } from '../data/types';
import type { Rect, SortKey } from '../state/store';
import type { Req, Res } from './compute';
import type { Results } from '../results/query';

/** Promise wrapper over the compute worker. Each tier's columns are copied in once. */
class ComputeClient {
  private w = new Worker(new URL('./compute.worker.ts', import.meta.url), { type: 'module' });
  private pending = new Map<number, { ok: (r: Results) => void; fail: (e: Error) => void }>();
  private seq = 0;
  private ready = new Set<Tier>();

  constructor() {
    this.w.onmessage = (e: MessageEvent<Res>) => {
      const p = this.pending.get(e.data.id);
      if (!p) return;
      this.pending.delete(e.data.id);
      if (e.data.type === 'error') p.fail(new Error(e.data.message));
      else p.ok({ ids: e.data.ids, total: e.data.total });
    };
  }

  private init(tier: Tier, c: Columns) {
    if (this.ready.has(tier)) return;
    this.ready.add(tier);
    const msg: Req = { type: 'init', tier, meta: c.meta, buffer: c.buffer.slice(0) };
    this.w.postMessage(msg);
  }

  query(tier: Tier, c: Columns, rect: Rect | null, sort: SortKey): Promise<Results> {
    this.init(tier, c);
    const id = ++this.seq;
    return new Promise((ok, fail) => {
      this.pending.set(id, { ok, fail });
      this.w.postMessage({ type: 'query', id, tier, rect, sort } satisfies Req);
    });
  }
}

let client: ComputeClient | null = null;
export const compute = () => (client ??= new ComputeClient());
