import { HeatmapLayer } from '@deck.gl/aggregation-layers';
export function createOohHeatmapLayer(data:any, visible:boolean){ if(!visible) return null; return new HeatmapLayer({id:'ooh-asset-heatmap', data:(data?.features||[]), radiusPixels:60, intensity:1.2, getPosition:(f:any)=>f.geometry.coordinates, getWeight:(f:any)=>Number(f.properties?.hgl_relevance_score||1)} as any); }
