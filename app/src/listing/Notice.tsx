/** One-time dismissible notice that the premise is fictional. */
import { useState } from 'react';
import { DISCLAIMER } from './FinePrint';

const KEY = 'lunar-listings:notice-dismissed';

/** One-time dismissible fictional-premise notice on first load (UI-3). */
export function Notice() {
  const [open, setOpen] = useState(() => { try { return !localStorage.getItem(KEY); } catch { return true; } });
  if (!open) return null;
  const close = () => { try { localStorage.setItem(KEY, '1'); } catch { /* ignore */ } setOpen(false); };
  return (
    <div role="note" data-testid="notice" className="panel" style={{ position: 'absolute', left: 16, bottom: 16, right: 16, maxWidth: 540, padding: 14, fontSize: 12, zIndex: 5, display: 'flex', gap: 14, alignItems: 'center', borderColor: 'var(--accent-line)' }}>
      <span><strong style={{ color: 'var(--accent)' }}>Fictional premise, real data.</strong> {DISCLAIMER}</span>
      <button type="button" onClick={close} aria-pressed="true" style={{ alignSelf: 'center', whiteSpace: 'nowrap' }}>Got it</button>
    </div>
  );
}
