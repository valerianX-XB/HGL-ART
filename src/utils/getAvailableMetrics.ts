import { LAYER_CONFIG, type AnalysisLayer } from '../config/layerMetricCompatibility';
export function getAvailableMetrics(layer: AnalysisLayer){ return LAYER_CONFIG[layer].metrics; }
export function getDefaultMetric(layer: AnalysisLayer){ return LAYER_CONFIG[layer].defaultMetric; }
