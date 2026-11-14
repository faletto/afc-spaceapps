import { useEffect, useMemo, useRef, useState } from 'react';
import DeckGL from '@deck.gl/react';
import { OrthographicView } from '@deck.gl/core';
import { BitmapLayer, PolygonLayer, ScatterplotLayer, TextLayer } from '@deck.gl/layers';
import type { Columns, Tier } from '../data/types';
import { dataBase } from '../data/source';
import { useStore } from '../state/store';
import { BAND_COLORS, bandOf, buildMarkers, formatPrice, visibleIds } from './markers';
import { fitZoom, PILL_CAP, PLOT_HALF, PILL_ZOOM_ABOVE_FIT, plotSquare, tierBounds } from './tiers';

const VIEW = new OrthographicView({ id: 'map', flipY: false });
interface VS { target: [number, number, number]; zoom: number }

export function MapView({ tier, cols, basemapUrl }: { tier: Tier; cols: Columns; basemapUrl: string | null }) {
  const box = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ w: 0, h: 0 });
  const [vs, setVs] = useState<VS>({ target: [0, 0, 0], zoom: 0 });
  const { selection, hover, select, setHover, setViewRect, overlay, overlayOpacity } = useStore();

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
      id: 'off', data: { length: markers.off.ids.length, attributes: { getPosition: { value: markers.off.positions, size: 2 } } },
      filled: false, stroked: true, getLineColor: [170, 170, 170, 220], lineWidthUnits: 'pixels', getLineWidth: 1.5,
      radiusUnits: 'pixels', getRadius: Math.max(dotR + 0.5, 2.5), opacity: dotOpacity, pickable: true,
      onHover: (info) => setHover(info.index >= 0 ? markers.off.ids[info.index]! : null),
      onClick: (info) => info.index >= 0 && select(markers.off.ids[info.index]!),
    }),
    new ScatterplotLayer({
      id: 'dots', visible: !pills,
      data: { length: markers.on.ids.length, attributes: { getPosition: { value: markers.on.positions, size: 2 }, getFillColor: { value: markers.on.colors!, size: 4, normalized: true } } },
      radiusUnits: 'pixels', getRadius: dotR, opacity: dotOpacity, pickable: true,
      onHover: (info) => setHover(info.index >= 0 ? markers.on.ids[info.index]! : null),
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
    <div ref={box} style={{ position: 'absolute', inset: 0, background: '#0b0d12' }}>
      {size.w > 0 && (
        <DeckGL
          views={VIEW} viewState={vs} controller={{ dragRotate: false }} layers={layers}
          onViewStateChange={({ viewState }) => setVs(viewState as unknown as VS)}
          getCursor={({ isHovering }) => (isHovering ? 'pointer' : 'grab')}
        />
      )}
    </div>
  );
}
