import { GeoJsonLayer } from '@deck.gl/layers';
import { colorFor } from '../utils/format';
import { extent, normalizeForHeight } from '../utils/normalizeMetrics';
export function createBlockGroupSurfaceLayer(data:any, metricKey:string, maxHeightM:number, visible:boolean, onHover:any) {
  if (!visible) return null;
  const features=data?.features||[]; const [min,max]=extent(features, metricKey); const cap=Math.min(70, maxHeightM||35);
  return new GeoJsonLayer({id:'block-group-low-surface', data, pickable:true, extruded:true, wireframe:false,
    getElevation:(f:any)=>normalizeForHeight(Number(f.properties?.[metricKey]||0), metricKey, min, max)*cap,
    getFillColor:(f:any)=>colorFor(Number(f.properties?.[metricKey]||0), min, max), getLineColor:[255,255,255,120], lineWidthMinPixels:0.5, onHover} as any);
}
