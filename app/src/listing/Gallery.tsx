import { Tour, type TourProps } from '../tour/Tour';

/** 3D Tour panel (DET-5). Polar-only; Moon-wide plots have no tour, so nothing is shown. There are no Moon photos to show. */
export function Gallery({ tour }: { tour: TourProps | null }) {
  if (!tour) return null;
  return (
    <section aria-label="3D Tour">
      <h3 style={{ margin: '0 0 6px', fontSize: 14 }}>3D Tour</h3>
      <Tour {...tour} />
    </section>
  );
}
