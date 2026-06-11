
import type { MetricConfig } from '../types/data';
export function formatValue(value: any, format?: string): string {
  if (value === null || value === undefined || value === '' || value === Infinity || value === -Infinity) return 'N/A';
  const n = Number(value);
  if (!Number.isFinite(n)) return 'N/A';
  if (format === 'currency') return '$' + n.toLocaleString(undefined, {maximumFractionDigits: 0});
  if (format === 'percent') return n.toFixed(1) + '%';
  if (format === 'score') return n.toFixed(1);
  return n.toLocaleString(undefined, {maximumFractionDigits: 0});
}
export function metricExtent(features: any[], key: string): [number, number] {
  const vals = (features || []).map(f => Number(f.properties?.[key])).filter(Number.isFinite);
  if (!vals.length) return [0, 1];
  vals.sort((a,b)=>a-b);
  const lo = vals[Math.floor((vals.length - 1) * 0.03)];
  const hi = vals[Math.ceil((vals.length - 1) * 0.97)];
  return [Number.isFinite(lo) ? lo : 0, Number.isFinite(hi) && hi !== lo ? hi : (lo || 0) + 1];
}
export function colorFor(value: number, min: number, max: number): [number, number, number, number] {
  const v = Number(value);
  const t = !Number.isFinite(v) || max === min ? 0.15 : Math.max(0, Math.min(1, (v - min) / (max - min)));
  // High-contrast elegant sequential ramp: pale blue -> teal -> amber/orange
  const stops = [
    [232, 241, 250],
    [102, 194, 165],
    [252, 141, 89],
    [190, 65, 55]
  ];
  const x = t * (stops.length - 1);
  const i = Math.min(stops.length - 2, Math.floor(x));
  const f = x - i;
  const c = stops[i].map((a, idx) => Math.round(a + (stops[i+1][idx] - a) * f));
  return [c[0], c[1], c[2], 218];
}
export function getMetric(metrics: MetricConfig[], key: string) { return metrics.find(m => m.key === key) || metrics[0]; }
