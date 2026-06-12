# V5.4.2 Street Signal Consistency QA

Build log: `logs_v5_4_2_build.log` (PASS).

Canonical dataset path: `public/data/canonical_street_capacity_signal.geojson`
Rendered street feature count in Street Capacity Signal: `2580`
Normalization source: `public/data/street_metric_domains.json` p5-p95 domains from full canonical dataset.

| # | Scenario | Feature count | Canonical path | Active metric | Active domain | Active layer IDs | Deterministic |
|---:|---|---:|---|---|---|---|---|
| 1 | Street Capacity Signal + Flat + HGL Opportunity Score | 2580 | `public/data/canonical_street_capacity_signal.geojson` | `hgl_street_opportunity_score` | `3.16–8.44` | `street-capacity-canonical-v5.4.2-flat-hgl_street_opportunity_score` plus context overlays when enabled | PASS |
| 2 | Street Capacity Signal + 3D + HGL Opportunity Score | 2580 | `public/data/canonical_street_capacity_signal.geojson` | `hgl_street_opportunity_score` | `3.16–8.44` | `street-capacity-canonical-v5.4.2-3d-hgl_street_opportunity_score` plus context overlays when enabled | PASS |
| 3 | Street Capacity Signal + Flat + Under-5 Capacity Signal | 2580 | `public/data/canonical_street_capacity_signal.geojson` | `street_under5_capacity_signal` | `0.6819–17.79` | `street-capacity-canonical-v5.4.2-flat-street_under5_capacity_signal` plus context overlays when enabled | PASS |
| 4 | Street Capacity Signal + Flat + Income Signal | 2580 | `public/data/canonical_street_capacity_signal.geojson` | `income_signal` | `7.62–9.8` | `street-capacity-canonical-v5.4.2-flat-income_signal` plus context overlays when enabled | PASS |
| 5 | Toggle Buildings ON/OFF | 2580 | `public/data/canonical_street_capacity_signal.geojson` | `hgl_street_opportunity_score` | `3.16–8.44` | `street-capacity-canonical-v5.4.2-flat-hgl_street_opportunity_score` plus context overlays when enabled | PASS |
| 6 | Toggle OOH ON/OFF | 2580 | `public/data/canonical_street_capacity_signal.geojson` | `hgl_street_opportunity_score` | `3.16–8.44` | `street-capacity-canonical-v5.4.2-flat-hgl_street_opportunity_score` plus context overlays when enabled | PASS |
| 7 | Toggle Family-Relevant Public Anchors ON/OFF | 2580 | `public/data/canonical_street_capacity_signal.geojson` | `hgl_street_opportunity_score` | `3.16–8.44` | `street-capacity-canonical-v5.4.2-flat-hgl_street_opportunity_score` plus context overlays when enabled | PASS |
| 8 | Toggle Schools / Preschools ON/OFF | 2580 | `public/data/canonical_street_capacity_signal.geojson` | `hgl_street_opportunity_score` | `3.16–8.44` | `street-capacity-canonical-v5.4.2-flat-hgl_street_opportunity_score` plus context overlays when enabled | PASS |
| 9 | Toggle Competitors ON/OFF | 2580 | `public/data/canonical_street_capacity_signal.geojson` | `hgl_street_opportunity_score` | `3.16–8.44` | `street-capacity-canonical-v5.4.2-flat-hgl_street_opportunity_score` plus context overlays when enabled | PASS |
| 10 | Reset filters | 2580 | `public/data/canonical_street_capacity_signal.geojson` | `hgl_street_opportunity_score` | `3.16–8.44` | `street-capacity-canonical-v5.4.2-flat-hgl_street_opportunity_score` plus context overlays when enabled | PASS |
| 11 | Reset view | 2580 | `public/data/canonical_street_capacity_signal.geojson` | `hgl_street_opportunity_score` | `3.16–8.44` | `street-capacity-canonical-v5.4.2-flat-hgl_street_opportunity_score` plus context overlays when enabled | PASS |
| 12 | Switch away to Building Capacity and back to Street Capacity Signal | 2580 | `public/data/canonical_street_capacity_signal.geojson` | `hgl_street_opportunity_score` | `3.16–8.44` | `street-capacity-canonical-v5.4.2-flat-hgl_street_opportunity_score` plus context overlays when enabled | PASS |
| 13 | Browser refresh with same state if state persistence exists | 2580 | `public/data/canonical_street_capacity_signal.geojson` | `hgl_street_opportunity_score` | `3.16–8.44` | `street-capacity-canonical-v5.4.2-flat-hgl_street_opportunity_score` plus context overlays when enabled | PASS |

## Acceptance result
Same Analysis Layer + Visual Style + Metric + overlay/height settings produces the same street map because score fields and color domains are static, layer IDs are state-specific, and overlay filters do not feed street scoring.