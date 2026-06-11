import { GeoJsonLayer } from '@deck.gl/layers';
import { colorFor } from '../utils/format';
import { extent, normalizeForHeight } from '../utils/normalizeMetrics';
export function createCensusBlockSurfaceLayer(data:any, metricKey:string, maxHeightM:number, visible:boolean, onHover:any) {
  if (!visible) return null;
  const features=data?.features||[]; const [min,max]=extent(features, metricKey); const cap=Math.min(50, maxHeightM||25);
  return new GeoJsonLayer({id:'census-block-low-surface', data, pickable:true, extruded:true, wireframe:false,
    getElevation:(f:any)=>normalizeForHeight(Number(f.properties?.[metricKey]||0), metricKey, min, max)*cap,
    getFillColor:(f:any)=>colorFor(Number(f.properties?.[metricKey]||0), min, max), getLineColor:[255,255,255,90], lineWidthMinPixels:0.5, onHover} as any);
}
