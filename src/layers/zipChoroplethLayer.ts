import { GeoJsonLayer, ScatterplotLayer } from '@deck.gl/layers';
import { colorFor, metricExtent } from '../utils/format';
export function createZipChoroplethLayer(polyData: any, centroidData: any, metricKey: string, onHover: any) {
  const features = polyData?.features || [];
  const hasPolygons = features.some((f: any) => ['Polygon','MultiPolygon'].includes(f.geometry?.type));
  const source = hasPolygons ? features : centroidData.features;
  const [min, max] = metricExtent(source, metricKey);
  if (hasPolygons) return new GeoJsonLayer({ id:'zip-choropleth', data: polyData, pickable:true, stroked:true, filled:true, getFillColor:(f:any)=>colorFor(Number(f.properties?.[metricKey]||0),min,max), getLineColor:[255,255,255,230], lineWidthMinPixels:1, onHover } as any);
  return new ScatterplotLayer({ id:'zip-centroid-choropleth', data: centroidData.features, pickable:true, radiusUnits:'meters', radiusScale:1, getRadius:650, getPosition:(f:any)=>f.geometry.coordinates, getFillColor:(f:any)=>colorFor(Number(f.properties?.[metricKey]||0),min,max), getLineColor:[255,255,255], stroked:true, lineWidthMinPixels:1, onHover } as any);
}
