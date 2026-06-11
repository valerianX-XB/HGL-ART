import { ScatterplotLayer } from '@deck.gl/layers';
export function createSchoolPreschoolLayer(data:any, visible:boolean, onHover:any){
 if(!visible) return null;
 const rows=(data?.features||[]).filter((f:any)=>!!f.geometry);
 return new ScatterplotLayer({id:`schools-preschools-${rows.length}`, data:rows, pickable:true, radiusUnits:'pixels', radiusMinPixels:5, radiusMaxPixels:10, getRadius:(f:any)=>f.properties?.site_type==='Kindergarten'||f.properties?.site_type==='Childcare'?7:5, getPosition:(f:any)=>f.geometry.coordinates, getFillColor:[37,99,235,220], getLineColor:[255,255,255,240], stroked:true, lineWidthMinPixels:1, onHover} as any);
}
