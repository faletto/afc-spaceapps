import type { ReactNode } from 'react';
import { useStore } from '../state/store';
import { Tour, type TourProps } from '../tour/Tour';

/** Photos | 3D Tour tabs (DET-5). The tour is polar-only; Moon-wide plots show just the photo tab. */
export function Gallery({ photo, tour }: { photo: ReactNode; tour: TourProps | null }) {
  const tab = useStore((s) => s.galleryTab), setTab = useStore((s) => s.setGalleryTab);
  const btn = (id: 'photos' | 'tour', label: string) => (
    <button type="button" role="tab" aria-selected={tab === id} onClick={() => setTab(id)}> {label}</button>
  );
  return (
    <section aria-label="Gallery" className="block">
      <div role="tablist" style={{ marginBottom: 10 }}>{btn('photos', 'Photos')}{tour && btn('tour', '3D Tour')}</div>
      {tab === 'tour' && tour ? <Tour {...tour} /> : photo}
    </section>
  );
}
