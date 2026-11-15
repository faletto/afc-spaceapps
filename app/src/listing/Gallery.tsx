/** The 3D Tour panel of a listing. Polar plots only. */
import { Tour, type TourProps } from '../tour/Tour';

/** 3D Tour panel (DET-5). Polar-only; Moon-wide plots have no tour, so nothing is shown. There are no Moon photos to show. */
export function Gallery({ tour }: { tour: TourProps | null }) {
  if (!tour) return null;
  return (
    <section aria-label="3D Tour" className="block">
      <h3 className="section-title">3D Tour</h3>
      <Tour {...tour} />
    </section>
  );
}
