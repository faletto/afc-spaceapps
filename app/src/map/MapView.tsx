import { useEffect, useMemo, useRef, useState } from 'react';
import DeckGL from '@deck.gl/react';
import { OrthographicView } from '@deck.gl/core';
import { BitmapLayer, PolygonLayer, ScatterplotLayer, TextLayer } from '@deck.gl/layers';
import type { Columns, Tier } from '../data/types';
import { dataBase } from '../data/source';
import { useStore } from '../state/store';
import { BAND_COLORS, bandOf, buildMarkers, formatPrice, visibleIds } from './markers';
import { fitZoom, PILL_CAP, PLOT_HALF, PILL_ZOOM_ABOVE_FIT, plotSquare, tierBounds } from './tiers';

/** Dots are < 2 px at the Moon-wide zoom; pick the nearest marker within this many pixels so they stay clickable. */
const PICK_RADIUS_PX = 5;
const VIEW = new OrthographicView({ id: 'map', flipY: false });
interface VS { target: [number, number, number]; zoom: number }

export function MapView({ tier, cols, basemapUrl }: { tier: Tier; cols: Columns; basemapUrl: string | null }) {
  const box = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ w: 0, h: 0 });
  const [vs, setVs] = useState<VS>({ target: [0, 0, 0], zoom: 0 });
  const selection = useStore((s) => s.selection), hover = useStore((s) => s.hover);
  const select = useStore((s) => s.select), setHover = useStore((s) => s.setHover), setViewRect = useStore((s) => s.setViewRect);
  const overlay = useStore((s) => s.overlay), overlayOpacity = useStore((s) => s.overlayOpacity);
  const down = useRef<[number, number] | null>(null);
  const [offTip, setOffTip] = useState<{ x: number; y: number } | null>(null);

  useEffect(() => {
    const el = box.current!;
    const ro = new ResizeObserver(() => setSize({ w: el.clientWidth, h: el.clientHeight }));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const bounds = tierBounds(cols);
  const fit = size.w ? fitZoom(bounds, size.w, size.h) : 0;
  const passing = useStore((s) => s.results?.passing);
  const markers = useMemo(() => buildMarkers(cols, passing), [cols, passing]);
  // deck.gl diffs layer `data` by identity: build the binary attribute objects once per marker set, not once per render,
  // otherwise every hover re-uploads all attributes (and swallows clicks).
  const dotData = useMemo(() => ({
    length: markers.on.ids.length,
    attributes: { getPosition: { value: markers.on.positions, size: 2 }, getFillColor: { value: markers.on.colors!, size: 4, normalized: true } },
  }), [markers]);
  const offData = useMemo(() => ({
    length: markers.off.ids.length, attributes: { getPosition: { value: markers.off.positions, size: 2 } },
  }), [markers]);

  // Re-fit when the tier or container size changes.
  useEffect(() => {
    if (size.w) setVs({ target: [(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2, 0], zoom: fit });
  }, [tier, cols, size.w, size.h]);

  // Publish the visible rect for the results list (debounced, RES-3).
  useEffect(() => {
    if (!size.w) return;
    const t = setTimeout(() => {
      const sc = 2 ** vs.zoom, hw = size.w / 2 / sc, hh = size.h / 2 / sc;
      setViewRect([vs.target[0] - hw, vs.target[1] - hh, vs.target[0] + hw, vs.target[1] + hh]);
    }, 120);
    return () => clearTimeout(t);
  }, [vs, size, setViewRect]);

  // Dot radius follows plot size on screen so dots don't wall off the basemap/overlay; fade them under an overlay.
  const plotPx = 2 ** vs.zoom * 2 * PLOT_HALF[tier];
  const dotR = Math.min(4, Math.max(0.8, plotPx * 0.3));
  const dotOpacity = overlay ? 0.35 : 1;

  const pills = vs.zoom - fit >= PILL_ZOOM_ABOVE_FIT;
  const shown = useMemo(() => {
    if (!pills || !size.w) return [];
    const s = 2 ** vs.zoom, hw = size.w / 2 / s, hh = size.h / 2 / s;
    return visibleIds(markers.on, [vs.target[0] - hw, vs.target[1] - hh, vs.target[0] + hw, vs.target[1] + hh], PILL_CAP);
  }, [pills, vs, size, markers]);

  const outline = (i: number | null) =>
    i == null ? [] : [{ i, poly: plotSquare(cols.col.x[i]!, cols.col.y[i]!, tier) }];

  const layers = [
    basemapUrl ? new BitmapLayer({ id: 'basemap', image: basemapUrl, bounds }) : null,
    overlay && new BitmapLayer({
      id: 'overlay', opacity: overlayOpacity, bounds, image: `${dataBase}${tier}/overlay/${overlay}.png`,
    }),
    // Off market (MAP-5): hollow grey ring — distinct by shape, not only color.
    new ScatterplotLayer({
      id: 'off', data: offData,
      filled: false, stroked: true, getLineColor: [170, 170, 170, 220], lineWidthUnits: 'pixels', getLineWidth: 1.5,
      radiusUnits: 'pixels', getRadius: Math.max(dotR + 0.5, 2.5), opacity: dotOpacity, pickable: true,
      onHover: (info) => { setHover(info.index >= 0 ? markers.off.ids[info.index]! : null); setOffTip(info.index >= 0 ? { x: info.x, y: info.y } : null); },
      onClick: (info) => info.index >= 0 && select(markers.off.ids[info.index]!),
    }),
    new ScatterplotLayer({
      id: 'dots', visible: !pills,
      data: dotData,
      radiusUnits: 'pixels', getRadius: dotR, opacity: dotOpacity, pickable: true,
      onHover: (info) => { setHover(info.index >= 0 ? markers.on.ids[info.index]! : null); if (info.index >= 0) setOffTip(null); },
      onClick: (info) => info.index >= 0 && select(markers.on.ids[info.index]!),
    }),
    new TextLayer<number>({
      id: 'pills', visible: pills, data: shown, pickable: true,
      getPosition: (i) => [cols.col.x[i]!, cols.col.y[i]!], getText: (i) => formatPrice(cols.col.price[i]!),
      getSize: 12, sizeUnits: 'pixels', getColor: [20, 20, 25, 255], fontWeight: 700,
      background: true, getBackgroundColor: (i) => [...BAND_COLORS[bandOf(cols.col.price[i]!, markers.edges)]!, 240] as [number, number, number, number],
      backgroundPadding: [5, 2], getBorderColor: [20, 20, 25, 255], getBorderWidth: 1,
      onHover: (info) => setHover(info.object ?? null),
      onClick: (info) => info.object != null && select(info.object),
    }),
    new PolygonLayer<{ i: number; poly: [number, number][] }>({
      id: 'outline', data: [...outline(hover), ...(selection !== hover ? outline(selection) : [])],
      getPolygon: (d) => d.poly, filled: false, stroked: true, lineWidthUnits: 'pixels',
      getLineWidth: (d) => (d.i === selection ? 3 : 2), getLineColor: (d) => (d.i === selection ? [255, 255, 255, 255] : [120, 190, 255, 255]),
    }),
  ];

  return (
    <div
      ref={box} style={{ position: 'absolute', inset: 0, background: '#0b0d12' }}
      onPointerDownCapture={(e) => { down.current = [e.clientX, e.clientY]; }}
      // deck.gl's own tap needs pointer-down→up within ~250 ms, which slow GPUs miss while picking 64.8k markers.
      // Hover picking is reliable, so a plain click (not a drag) selects the plot under the pointer.
      onClick={(e) => {
        const d = down.current;
        if (hover != null && d && Math.hypot(e.clientX - d[0], e.clientY - d[1]) < 4) select(hover);
      }}
    >
      {size.w > 0 && (
        <DeckGL
          views={VIEW} viewState={vs} pickingRadius={PICK_RADIUS_PX} controller={{ dragRotate: false }} layers={layers}
          onViewStateChange={({ viewState }) => setVs(viewState as unknown as VS)}
          getCursor={({ isHovering }) => (isHovering ? 'pointer' : 'grab')}
        />
      )}
      {offTip && (
        <div role="tooltip" style={{ position: 'absolute', left: offTip.x + 12, top: offTip.y + 12, background: '#222a3a', border: '1px solid #3a4560', borderRadius: 6, padding: '4px 8px', fontSize: 12, pointerEvents: 'none', color: '#eee' }}>
          Off market: not safe to land
        </div>
      )}
    </div>
  );
}
