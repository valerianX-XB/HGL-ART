import { LAYER_CONFIG, type AnalysisLayer } from '../config/layerMetricCompatibility';
export function getAvailableVisualStyles(layer: AnalysisLayer){ return LAYER_CONFIG[layer].styles; }
export function getDefaultVisualStyle(layer: AnalysisLayer){ return LAYER_CONFIG[layer].defaultStyle; }
