export function transformMetric(value: number, metricKey: string): number {
  const v = Math.max(0, Number(value) || 0);
  if (['population','households','under5','under5_official_bg','under5_official_tract','official_population','official_households','estimated_under5','estimated_households','residential_units','residential_capacity_units','estimated_household_capacity','under5_capacity_signal','modeled_under5_capacity_signal','preschool_age_capacity_signal'].includes(metricKey)) return Math.sqrt(v);
  if (['median_household_income','mean_household_income','estimated_income_signal'].includes(metricKey)) return Math.log1p(v);
  if (metricKey.includes('pct') || metricKey.includes('language') || metricKey.includes('share')) return Math.min(100, v) / 100;
  if (metricKey.includes('score') || metricKey.includes('signal') || metricKey.includes('density') || metricKey.includes('proximity') || metricKey.includes('confidence')) return Math.min(10, v) / 10;
  return v;
}
export function normalizeForHeight(value: number, metricKey: string, minRaw: number, maxRaw: number): number {
  if (metricKey.includes('pct') || metricKey.includes('share')) return Math.max(0, Math.min(1, (Number(value)||0) / 100));
  if (metricKey.includes('score') || metricKey.includes('signal') || metricKey.includes('density') || metricKey.includes('proximity') || metricKey.includes('confidence')) return Math.max(0, Math.min(1, (Number(value)||0) / 10));
  const min = transformMetric(minRaw, metricKey);
  const max = transformMetric(maxRaw, metricKey);
  const val = transformMetric(value, metricKey);
  if (!Number.isFinite(val) || max === min) return 0.35;
  return Math.max(0, Math.min(1, (val - min) / (max - min)));
}
export function extent(features: any[], key: string): [number, number] {
  const vals = features.map(f => Number(f.properties?.[key])).filter(Number.isFinite).sort((a,b)=>a-b);
  if(!vals.length) return [0,1];
  const lo=vals[Math.floor((vals.length-1)*0.05)];
  const hi=vals[Math.ceil((vals.length-1)*0.95)];
  return [Number.isFinite(lo)?lo:0, Number.isFinite(hi)&&hi!==lo?hi:(lo||0)+1];
}
export function normalize01(value:number, min:number, max:number){ return max===min ? 0.5 : Math.max(0, Math.min(1, (value-min)/(max-min))); }
