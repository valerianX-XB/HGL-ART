import { GeoJsonLayer } from '@deck.gl/layers';
import { colorFor } from '../utils/format';
import { extent, normalizeForHeight } from '../utils/normalizeMetrics';
export function createZipExtrusionLayer(data:any, metricKey:string, maxHeightM:number, onHover:any) {
  const features = data?.features || [];
  const [min,max] = extent(features, metricKey);
  const capped = Math.min(45, maxHeightM || 25);
  return new GeoJsonLayer({ id:'low-zip-overview-surface', data, pickable:true, extruded:true, wireframe:false,
    getElevation:(f:any)=> normalizeForHeight(Number(f.properties?.[metricKey]||0), metricKey, min, max) * capped,
    getFillColor:(f:any)=> colorFor(Number(f.properties?.[metricKey]||0), min, max),
    getLineColor:[255,255,255,210], lineWidthMinPixels:1, onHover
  } as any);
}
