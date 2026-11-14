/** Local geometry (spec §3.3). Mirrors pipeline/lunar_listings/geometry.py; golden-vector tested. */
export const R_MOON_M = 1_737_400;
const D2R = Math.PI / 180;
export type Vec3 = readonly [number, number, number];

export interface Frame { u: Vec3; e: Vec3; n: Vec3 }

export function enuFrame(latDeg: number, lonDeg: number): Frame {
  const la = latDeg * D2R, lo = lonDeg * D2R;
  return {
    u: [Math.cos(la) * Math.cos(lo), Math.cos(la) * Math.sin(lo), Math.sin(la)],
    e: [-Math.sin(lo), Math.cos(lo), 0],
    n: [-Math.sin(la) * Math.cos(lo), -Math.sin(la) * Math.sin(lo), Math.cos(la)],
  };
}

const dot = (a: Vec3, x: number, y: number, z: number) => a[0] * x + a[1] * y + a[2] * z;
const clamp1 = (v: number) => Math.min(1, Math.max(-1, v));

/** Elevation and azimuth (deg, 0 = N, 90 = E, in [0,360)) of unit direction (x,y,z). */
export function azEl(x: number, y: number, z: number, f: Frame): { el: number; az: number } {
  const el = Math.asin(clamp1(dot(f.u, x, y, z))) / D2R;
  const az = Math.atan2(dot(f.e, x, y, z), dot(f.n, x, y, z)) / D2R;
  return { el, az: ((az % 360) + 360) % 360 };
}

/** Earth direction with parallax: d = normalize(E·dist − (R+h)·u). */
export function earthAzEl(ex: number, ey: number, ez: number, distM: number, f: Frame, hM = 0, R = R_MOON_M) {
  const dx = ex * distM - (R + hM) * f.u[0], dy = ey * distM - (R + hM) * f.u[1], dz = ez * distM - (R + hM) * f.u[2];
  const nrm = Math.hypot(dx, dy, dz);
  return azEl(dx / nrm, dy / nrm, dz / nrm, f);
}
