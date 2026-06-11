import { HeatmapLayer } from '@deck.gl/aggregation-layers';
export function createHeatmapLayer(data: any, metricKey: string) {
  const features = data?.features || [];
  return new HeatmapLayer({
    id: 'zip-heatmap', data: features, pickable: false, radiusPixels: 90, intensity: 1.2, threshold: 0.03,
    getPosition: (f: any) => f.geometry.coordinates,
    getWeight: (f: any) => Number(f.properties?.[metricKey] || 0)
  } as any);
}
