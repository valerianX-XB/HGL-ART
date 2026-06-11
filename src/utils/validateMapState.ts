import { LAYER_CONFIG, type AnalysisLayer, type VisualStyle } from '../config/layerMetricCompatibility';
export function validateMapState<T extends {analysisLayer: AnalysisLayer; visualStyle: VisualStyle; metricKey: string}>(state: T): T {
  const cfg = LAYER_CONFIG[state.analysisLayer];
  const metricKey = cfg.metrics.includes(state.metricKey) ? state.metricKey : cfg.defaultMetric;
  const visualStyle = cfg.styles.includes(state.visualStyle) ? state.visualStyle : cfg.defaultStyle;
  return {...state, metricKey, visualStyle};
}
