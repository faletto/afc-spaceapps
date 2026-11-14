import { useState } from 'react';
import { DISCLAIMER } from './FinePrint';

const KEY = 'lunar-listings:notice-dismissed';

/** One-time dismissible fictional-premise notice on first load (UI-3). */
export function Notice() {
  const [open, setOpen] = useState(() => { try { return !localStorage.getItem(KEY); } catch { return true; } });
  if (!open) return null;
  const close = () => { try { localStorage.setItem(KEY, '1'); } catch { /* ignore */ } setOpen(false); };
  return (
    <div role="note" data-testid="notice" style={{ position: 'absolute', left: 12, bottom: 12, right: 12, maxWidth: 520, background: '#1d2433', border: '1px solid #3a4560', borderRadius: 8, padding: 12, fontSize: 12, zIndex: 5, display: 'flex', gap: 12 }}>
      <span><strong>Fictional premise, real data.</strong> {DISCLAIMER}</span>
      <button type="button" onClick={close} style={{ alignSelf: 'start' }}>Got it</button>
    </div>
  );
}
