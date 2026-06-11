export type AnalysisLayer = 'building' | 'street' | 'blockGroup' | 'censusBlock' | 'zip' | 'ooh' | 'combined';
export type VisualStyle = '3d' | 'heatmap' | 'flat' | 'mixed' | 'inventory';
export type MetricKey = string;

export interface MetricConfig {
  key: string;
  label_en: string;
  label_zh: string;
  format: string;
  description: string;
}

export interface MapState {
  analysisLayer: AnalysisLayer;
  visualStyle: VisualStyle;
  metricKey: string;
  overlays: {
    buildings: boolean;
    ooh: boolean;
    anchors: boolean;
    schools: boolean;
    parks: boolean;
    competitors: boolean;
    zip: boolean;
    hglLocation: boolean;
  };
  oohTypeFilters: Set<string>;
  oohStatusFilters: Set<string>;
  familyAnchorCategoryFilters: Set<string>;
  heightSettings: Record<string, number>;
  selectedFeatureId?: string | null;
  hoveredFeatureId?: string | null;
  dataVersion: number;
}
