import { HeatmapLayer } from '@deck.gl/aggregation-layers';
export function createBlockGroupHeatmapLayer(data:any, metricKey:string, visible:boolean){ if(!visible) return null; return new HeatmapLayer({id:'block-group-heatmap', data:(data?.features||[]), radiusPixels:80, intensity:1.0, getPosition:(f:any)=>f.properties.centroid, getWeight:(f:any)=>Number(f.properties?.[metricKey]||0)} as any); }
