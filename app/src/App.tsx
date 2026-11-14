import DeckGL from '@deck.gl/react';
import { OrthographicView } from '@deck.gl/core';
import { ScatterplotLayer } from '@deck.gl/layers';

// A0 placeholder: proves the deck.gl canvas renders. Replaced by MapView in A1.
const layers = [new ScatterplotLayer({ id: 'demo', data: [{ p: [0, 0] as [number, number] }], getPosition: (d: { p: [number, number] }) => d.p, getRadius: 40, getFillColor: [200, 200, 220] })];

export function App() {
  return (
    <div style={{ position: 'fixed', inset: 0, background: '#0b0d12' }}>
      <DeckGL views={new OrthographicView({})} initialViewState={{ target: [0, 0, 0], zoom: 0 }} controller layers={layers} />
    </div>
  );
}
