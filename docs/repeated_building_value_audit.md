# Repeated Building Value Audit v4

## Duplicate counts for residential_units
- 0: 1829
- 1: 830
- 2: 702
- 3: 540
- 4: 470
- 8: 396
- 5: 346
- 6: 311
- 20: 265
- 10: 243

## Duplicate counts for under5_capacity_signal
- 0.0: 1829
- 0.045: 353
- 0.089: 292
- 0.034: 216
- 0.134: 163
- 0.068: 154
- 0.101: 119
- 0.327: 112
- 0.447: 111
- 0.28: 102

## Duplicate counts for hgl_building_opportunity_score
- 0.0: 1829
- 1.83: 292
- 2.17: 198
- 1.43: 166
- 2.91: 138
- 3.45: 113
- 3.26: 110
- 2.42: 94
- 2.97: 94
- 1.77: 90

## Findings
- Non-residential buildings with non-zero residential capacity fields: 0
- Repeated zero values are legitimate for non-residential buildings.
- Repeated one-unit values are expected for one-/two-family or small residential buildings.
- Scores are derived from building-level UnitsRes/capacity and use classification plus local aggregate income/age proxies; ZIP-level values are no longer directly copied as building residents.
- Commercial/office/public/institutional/parking/industrial classes are set to zero residential capacity.
