import { useId, useState, type ReactNode } from 'react';
import { GLOSSARY } from './glossary';

/** Glossary tooltip: keyboard-focusable, opens on hover/focus, Escape closes (spec §6.7, DET-8). */
export function Term({ id, children, extra }: { id: string; children: ReactNode; extra?: string }) {
  const [open, setOpen] = useState(false);
  const tipId = useId();
  const g = GLOSSARY[id];
  if (!g) return <>{children}</>;
  return (
    <span style={{ position: 'relative' }}>
      <span
        tabIndex={0} aria-describedby={open ? tipId : undefined} data-term={id}
        onMouseEnter={() => setOpen(true)} onMouseLeave={() => setOpen(false)}
        onFocus={() => setOpen(true)} onBlur={() => setOpen(false)}
        onKeyDown={(e) => e.key === 'Escape' && open && (e.stopPropagation(), setOpen(false))}
        style={{ borderBottom: '1px dotted currentColor', cursor: 'help' }}
      >{children}</span>
      {open && (
        <span role="tooltip" id={tipId} style={{
          position: 'absolute', left: 0, top: '100%', zIndex: 20, width: 240, marginTop: 4, padding: 8, borderRadius: 6,
          background: '#222a3a', border: '1px solid #3a4560', fontSize: 12, lineHeight: 1.4, fontWeight: 400, color: '#eee',
        }}>
          {g.text}{extra ? ` ${extra}` : ''}
          {g.formula && <><br /><code>{g.formula}</code></>}
          {g.source && <><br /><em>Source: {g.source}</em></>}
        </span>
      )}
    </span>
  );
}
