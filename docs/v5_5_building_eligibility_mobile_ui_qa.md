# V5.5 Building Eligibility + Mobile UI QA

## Building eligibility checks
- Building features tested: `7066`
- Family-eligible scored buildings: `3903`
- Neutral / excluded context buildings: `3163`
- Eligible buildings with nonzero family capacity: `3903`
- Excluded buildings with nonzero under-5/family capacity after patch: `0`

| # | Requirement | Result | Evidence |
|---:|---|---|---|
| 1 | Schools/universities do not contribute to Under-5 Capacity Signal | PASS | Education/university classes and school POI matches receive `under5_capacity_signal=0`. |
| 2 | Hospitals / medical institutions do not contribute | PASS | Medical/institution classes receive `medical_institution`, capacity 0. |
| 3 | Hotels / transient lodging do not contribute | PASS | Hotel/transient classes and keywords receive `hotel_or_transient_lodging`, capacity 0. |
| 4 | Student housing / dormitories do not contribute | PASS | University/student/dorm keywords override UnitsRes and set capacity 0. |
| 5 | Office / commercial-only buildings do not contribute | PASS | Office/commercial building classes and area signals set family eligibility false. |
| 6 | Non-eligible buildings still appear as neutral 3D context | PASS | `buildingMassingLayer` keeps physical height and forces neutral gray / no data lift for excluded buildings. |
| 7 | Eligible family residential buildings still show capacity scores | PASS | 3903 eligible buildings retain nonzero family capacity units. |
| 8 | New School / university-related buildings are audited | PASS | `docs/v5_5_building_eligibility_audit.md` includes university-related exclusions where present. |

## Category distribution
| Category | Count |
|---|---:|
| ordinary_residential | 3903 |
| office | 3024 |
| hotel_or_transient_lodging | 40 |
| school_university | 32 |
| religious_community_facility | 26 |
| student_housing_or_dormitory | 20 |
| medical_institution | 7 |
| shelter_or_institutional_housing | 6 |
| museum_cultural_institution | 3 |
| industrial_utility | 3 |
| public_facility | 2 |

## Mobile UI checks
| # | Requirement | Result | Evidence |
|---:|---|---|---|
| 9 | Left panel can be hidden | PASS | Info panel has open/collapsed state and Info toggle. |
| 10 | Right controls can be hidden | PASS | Control panel has open/collapsed state and Controls toggle. |
| 11 | Mobile opens panels as drawers / bottom sheets | PASS | CSS `<768px` uses fixed bottom-sheet transforms for panels. |
| 12 | No horizontal scrollbar | PASS | `html, body, #root, .app` overflow hidden and panels max to viewport width. |
| 13 | Map is usable full-screen when panels are hidden | PASS | Mobile defaults panels closed and map shell remains fixed full-screen. |
| 14 | Summary table is collapsed by default | PASS | `showTable` initializes false and opens through Summary button/bottom sheet. |
| 15 | Build passes | PASS | `npm run build` completed successfully; see `logs_v5_5_build.log`. |

Build result: PASS (`npm run build`).