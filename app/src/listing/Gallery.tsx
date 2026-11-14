import { useState, type ReactNode } from 'react';
import { Tour, type TourProps } from '../tour/Tour';

/** Photos | 3D Tour tabs (DET-5). The tour is polar-only; Moon-wide plots show just the photo tab. */
export function Gallery({ photo, tour }: { photo: ReactNode; tour: TourProps | null }) {
  const [tab, setTab] = useState<'photos' | 'tour'>('photos');
  const btn = (id: 'photos' | 'tour', label: string) => (
    <button type="button" role="tab" aria-selected={tab === id} onClick={() => setTab(id)} style={{ fontWeight: tab === id ? 700 : 400 }}>{label}</button>
  );
  return (
    <section aria-label="Gallery">
      <div role="tablist" style={{ display: 'flex', gap: 6, marginBottom: 6 }}>{btn('photos', 'Photos')}{tour && btn('tour', '3D Tour')}</div>
      {tab === 'tour' && tour ? <Tour {...tour} /> : photo}
    </section>
  );
}
