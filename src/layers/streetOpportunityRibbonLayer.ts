import { PathLayer } from '@deck.gl/layers';
import { colorFor } from '../utils/format';
import { extent, normalizeForHeight } from '../utils/normalizeMetrics';
export function createStreetOpportunityRibbonLayer(data:any, metricKey:string, maxHeightM:number, visible:boolean, onHover:any) {
  if (!visible) return null;
  const features=data?.features||[]; const [min,max]=extent(features, metricKey); const cap=Math.min(20, maxHeightM||8);
  return new PathLayer({ id:'street-opportunity-ribbons', data:features, pickable:true,
    getPath:(f:any)=>f.geometry.coordinates, getWidth:(f:any)=>4 + 12*normalizeForHeight(Number(f.properties?.[metricKey]||0), metricKey, min, max), widthUnits:'meters', rounded:true,
    getColor:(f:any)=>colorFor(Number(f.properties?.[metricKey]||0), min, max), getElevation:(f:any)=>normalizeForHeight(Number(f.properties?.[metricKey]||0), metricKey, min, max)*cap, onHover } as any);
}
