import { PathLayer } from '@deck.gl/layers';
import { colorFor } from '../utils/format';
import { extent, normalizeForHeight } from '../utils/normalizeMetrics';

export function createStreetOpportunityRibbonLayer(
  data: any,
  metricKey: string,
  maxHeightM: number,
  visible: boolean,
  onHover: any,
  visualStyle: string,
  domain?: [number, number],
  datasetVersion = 'v5.4.2'
) {
  if (!visible) return null;
  const features = data?.features || [];
  const [fallbackMin, fallbackMax] = extent(features, metricKey);
  const min = domain?.[0] ?? fallbackMin;
  const max = domain?.[1] ?? fallbackMax;
  const cap = visualStyle === '3d' ? Math.min(20, maxHeightM || 8) : 0;
  const widthBase = visualStyle === 'flat' ? 7 : 4;
  const widthRange = visualStyle === 'flat' ? 10 : 12;

  return new PathLayer({
    id: `street-capacity-canonical-${datasetVersion}-${visualStyle}-${metricKey}`,
    data: features,
    pickable: true,
    getPath: (f: any) => f.geometry.coordinates,
    getWidth: (f: any) => widthBase + widthRange * normalizeForHeight(Number(f.properties?.[metricKey] ?? 0), metricKey, min, max),
    widthUnits: 'meters',
    rounded: true,
    getColor: (f: any) => colorFor(Number(f.properties?.[metricKey] ?? 0), min, max),
    getElevation: (f: any) => normalizeForHeight(Number(f.properties?.[metricKey] ?? 0), metricKey, min, max) * cap,
    updateTriggers: {
      getWidth: [metricKey, min, max, visualStyle, datasetVersion],
      getColor: [metricKey, min, max, datasetVersion],
      getElevation: [metricKey, min, max, cap, visualStyle, datasetVersion]
    },
    onHover
  } as any);
}
