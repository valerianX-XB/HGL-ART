# V5.4.2 Street Layer Dependency Audit

## Deterministic rendering contract
Street Capacity Signal now loads only `public/data/canonical_street_capacity_signal.geojson` in normal mode. The layer is created once from the canonical dataset and static metric fields. Overlay toggles only add/remove context layers. They do not mutate street feature properties, recompute street scores, or change the normalization domain.

## Source/code checks
| Check | Result |
|---|---|
| Canonical street dataset loaded in App | PASS |
| Street heatmap no longer uses OOH heatmap as fallback | PASS |
| Metric domain passed to street layer | PASS |
| Street layer ID includes dataset version, visual style, metric | PASS |
| Deck update triggers include metric/domain/style/version | PASS |

## Street layer dependencies
Every active street layer depends on:
- `analysisLayer` via `layer`
- `visualStyle` via `style` and layer ID
- `metricKey` via `metric` and layer ID
- canonical dataset object `streets` loaded from `CANONICAL_STREET_DATASET_PATH`
- canonical dataset version `v5.4.2` in layer ID/update triggers
- street height setting `height.streetSurfaceMaxM` for 3D style
- stored domain from `street_metric_domains.json`
- hover callback only for interaction

Excluded from street scoring: OOH type/status filters, family-anchor filters, and all overlay visibility toggles. Those controls may change rendered overlay marker counts but not Street Capacity Signal values.

## Active street layer ID pattern
`street-capacity-canonical-v5.4.2-{visualStyle}-{metricKey}`

## Fallback policy
No ZIP, block-group, micro-market-grid, OOH-derived, or generated in-memory street fallback is used for default Street Capacity Signal display.