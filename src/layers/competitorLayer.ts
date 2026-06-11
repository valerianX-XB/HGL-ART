import { ScatterplotLayer } from '@deck.gl/layers';
export function createCompetitorLayer(data:any, visible:boolean, onHover:any){
 if(!visible) return null;
 const rows=(data?.features||[]).filter((f:any)=>!!f.geometry);
 return new ScatterplotLayer({id:`competitors-${rows.length}`, data:rows, pickable:true, radiusUnits:'pixels', radiusMinPixels:6, radiusMaxPixels:11, getRadius:8, getPosition:(f:any)=>f.geometry.coordinates, getFillColor:[220,38,38,220], getLineColor:[255,255,255,245], stroked:true, lineWidthMinPixels:1.3, onHover} as any);
}
