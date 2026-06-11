import { HeatmapLayer } from '@deck.gl/aggregation-layers';
export function createFamilyAnchorHeatmapLayer(data:any, visible:boolean){ if(!visible) return null; return new HeatmapLayer({id:'family-anchor-heatmap', data:(data?.features||[]).filter((f:any)=>f.geometry), radiusPixels:55, intensity:1.1, getPosition:(f:any)=>f.geometry.coordinates, getWeight:1} as any); }
