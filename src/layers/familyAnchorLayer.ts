import { ScatterplotLayer } from '@deck.gl/layers';
const COLORS:Record<string,number[]>={
 'Parks / playgrounds':[34,197,94,210], 'Libraries':[37,99,235,210], 'Child activity':[236,72,153,220], 'Pediatric / health':[14,165,233,215], 'Family retail / grocery':[245,158,11,210], 'Museums / culture':[168,85,247,210], 'Community centers':[20,184,166,210], 'Transit / corridors':[100,116,139,200], 'Birthday / camp / event':[249,115,22,220]
};
export function createFamilyAnchorLayer(data: any, visible: boolean, onHover: any, categoryFilters?: Set<string>) {
  if (!visible) return null;
  const rows = (data?.features || []).filter((f:any)=>!!f.geometry && (!categoryFilters || categoryFilters.has(f.properties?.anchor_category)));
  return new ScatterplotLayer({ id:`family-relevant-public-anchors-${rows.length}`, data: rows, pickable:true, radiusUnits:'pixels', radiusMinPixels:3, radiusMaxPixels:7, getRadius:4, getPosition:(f:any)=>f.geometry.coordinates, getFillColor:(f:any)=>COLORS[f.properties?.anchor_category]||[52,152,219,210], getLineColor:[255,255,255,220], stroked:true, lineWidthMinPixels:0.8, onHover } as any);
}
