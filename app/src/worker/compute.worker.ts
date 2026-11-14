import { makeHandler, type Req } from './compute';

const handle = makeHandler();
self.onmessage = (e: MessageEvent<Req>) => {
  const out = handle(e.data);
  if (out) postMessage(out);
};
