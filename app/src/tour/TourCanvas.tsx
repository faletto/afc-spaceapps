import { useEffect, useRef } from 'react';
import { horizonAt } from '../science/visibility';
import type { TourModel } from './tourModel';

const EL_MIN = -3, EL_MAX = 15, W = 960, H = 300, WINDOW_H = 24 * 30;
const xOf = (az: number) => (((az + 180) % 360) / 360) * W; // north in the centre
const yOf = (el: number) => H - ((el - EL_MIN) / (EL_MAX - EL_MIN)) * H;
const vscale = (360 / W / ((EL_MAX - EL_MIN) / H)).toFixed(0);

export function TourCanvas({ model, t }: { model: TourModel; t: number }) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const c = ref.current, g = c?.getContext('2d');
    if (!c || !g) return;
    const s = model.year, hz = model.horizon;
    g.clearRect(0, 0, W, H);
    const sky = g.createLinearGradient(0, 0, 0, H);
    sky.addColorStop(0, '#05070d'); sky.addColorStop(1, '#1a2030');
    g.fillStyle = sky; g.fillRect(0, 0, W, H);
    g.fillStyle = '#8b93a7'; g.font = '12px system-ui';
    for (const [az, l] of [[0, 'N'], [45, 'NE'], [90, 'E'], [135, 'SE'], [180, 'S'], [225, 'SW'], [270, 'W'], [315, 'NW']] as const) {
      g.fillText(l, xOf(az) - 6, 14); g.fillRect(xOf(az), 18, 1, 6);
    }
    const k0 = Math.max(0, t - s.t0), k1 = Math.min(s.n, k0 + WINDOW_H);
    // Hollow = not counted by the series (Sun: <50% of disk visible; Earth: below horizon + margin), same criterion as the stats.
    const dots = (el: Float64Array, az: Float64Array, ok: Uint8Array, col: string) => {
      for (let k = k0; k < k1; k++) {
        const e = el[k]!;
        if (e < EL_MIN || e > EL_MAX) continue;
        const hidden = !ok[k];
        g.beginPath(); g.arc(xOf(az[k]!), yOf(e), 2.2, 0, 7);
        if (hidden) { g.strokeStyle = col; g.globalAlpha = 0.5; g.lineWidth = 1; g.stroke(); } else { g.fillStyle = col; g.globalAlpha = 1; g.fill(); }
      }
      g.globalAlpha = 1;
    };
    dots(s.sunEl, s.sunAz, s.sunlit, '#ffd166');
    dots(s.earthEl, s.earthAz, s.earthOk, '#4cc9f0');
    g.beginPath(); g.moveTo(0, H);
    for (let px = 0; px <= W; px += 2) g.lineTo(px, yOf(horizonAt(hz, (px / W) * 360 - 180)));
    g.lineTo(W, H); g.closePath();
    g.fillStyle = '#2b2f3a'; g.fill(); g.strokeStyle = '#9aa3b8'; g.lineWidth = 1.5; g.stroke();
    const k = t - s.t0;
    const mark = (el: number, az: number, col: string, label: string) => {
      const y = yOf(Math.min(EL_MAX, Math.max(EL_MIN, el)));
      g.beginPath(); g.arc(xOf(az), y, 8, 0, 7); g.fillStyle = col; g.fill(); g.strokeStyle = '#fff'; g.lineWidth = 2; g.stroke();
      g.fillStyle = '#fff'; g.font = 'bold 12px system-ui'; g.fillText(label, xOf(az) + 11, y + 4);
    };
    mark(s.sunEl[k]!, s.sunAz[k]!, '#ffd166', s.sunlit[k] ? 'Sun' : 'Sun (hidden)');
    mark(s.earthEl[k]!, s.earthAz[k]!, '#4cc9f0', s.earthOk[k] ? 'Earth' : 'Earth (no signal)');
  }, [model, t]);
  return (
    <div>
      <canvas ref={ref} width={W} height={H} data-testid="tour-canvas" role="img"
        aria-label="360-degree horizon panorama with Sun and Earth paths" style={{ width: '100%', height: 'auto', borderRadius: 6, display: 'block' }} />
      <div style={{ fontSize: 11, opacity: 0.7, marginTop: 2 }}>Vertical scale ×{vscale} · dots = next 30 days (hollow = Sun mostly hidden or no Earth signal) · north in the centre</div>
    </div>
  );
}
