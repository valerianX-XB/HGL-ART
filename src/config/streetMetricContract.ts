export const CANONICAL_STREET_DATASET_PATH = './data/canonical_street_capacity_signal.geojson';
export const CANONICAL_STREET_DATASET_VERSION = 'v5.4.2';

export const STREET_REQUIRED_FIELDS = [
  'street_segment_id',
  'street_name',
  'from_intersection',
  'to_intersection',
  'geometry',
  'hgl_street_opportunity_score',
  'street_under5_capacity_signal',
  'street_preschool_age_demand_signal',
  'residential_capacity_nearby',
  'income_signal',
  'family_anchor_density',
  'school_preschool_anchor_density',
  'competitor_density',
  'ooh_asset_density',
  'transit_access_signal',
  'confidence_level'
] as const;

export const STATIC_STREET_DISPLAY_METRICS = [
  'hgl_street_opportunity_score',
  'street_under5_capacity_signal',
  'street_preschool_age_demand_signal',
  'residential_capacity_nearby',
  'income_signal',
  'family_anchor_density',
  'school_preschool_anchor_density',
  'competitor_density',
  'ooh_asset_density',
  'transit_access_signal'
] as const;

export type StreetMetricKey = typeof STATIC_STREET_DISPLAY_METRICS[number];

export function isStaticStreetMetric(metricKey: string): metricKey is StreetMetricKey {
  return (STATIC_STREET_DISPLAY_METRICS as readonly string[]).includes(metricKey);
}

export function getStreetDomain(domains: any, metricKey: string): [number, number] | undefined {
  const domain = domains?.domains?.find((d: any) => d.metric_key === metricKey);
  const used = domain?.domain_used;
  if (Array.isArray(used) && Number.isFinite(Number(used[0])) && Number.isFinite(Number(used[1])) && Number(used[1]) !== Number(used[0])) {
    return [Number(used[0]), Number(used[1])];
  }
  return undefined;
}
