import { ScatterplotLayer } from '@deck.gl/layers';
function color(status: string): [number,number,number,number] {
  const s = (status || '').toLowerCase();
  if (s.includes('available network')) return [46, 204, 113, 230];
  if (s.includes('potentially')) return [241, 196, 15, 230];
  if (s.includes('candidate')) return [230, 126, 34, 230];
  return [149, 165, 166, 220];
}
export function createOohPointLayer(data: any, topOnly: boolean, visible: boolean, onHover: any) {
  if (!visible) return null;
  const rows = (data?.features || []).filter((f:any) => !topOnly || Number(f.properties?.rank) <= 5);
  return new ScatterplotLayer({ id:'ooh-candidates', data: rows, pickable:true, radiusUnits:'meters', getRadius:(f:any)=>Number(f.properties?.rank)<=5?120:80, getPosition:(f:any)=>f.geometry.coordinates, getFillColor:(f:any)=>color(f.properties?.availability_status), getLineColor:[20,20,20,230], stroked:true, lineWidthMinPixels:1, onHover } as any);
}
