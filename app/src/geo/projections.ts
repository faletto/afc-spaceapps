/** South polar stereographic (contract: x = ρ sin(lon), y = ρ cos(lon), ρ = 2R·tan(45° + lat/2)). */
const R = 1_737_400;
export function polarXYToLatLon(x: number, y: number): { lat: number; lon: number } {
  const rho = Math.hypot(x, y);
  const lat = (2 * Math.atan(rho / (2 * R))) * (180 / Math.PI) - 90;
  const lon = rho === 0 ? 0 : Math.atan2(x, y) * (180 / Math.PI);
  return { lat, lon };
}
