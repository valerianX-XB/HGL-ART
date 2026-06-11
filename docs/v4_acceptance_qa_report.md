# V4 Acceptance QA Report

## Status: PASS

1. All six ZIPs show 3D buildings: PASS.
2. Non-residential buildings have residential capacity 0: PASS.
3. Residential buildings use UnitsRes/capacity logic where possible: PASS.
4. Repeated values audited and explained: PASS; see docs/repeated_building_value_audit.md.
5. Under-5 capacity signal replaces actual-resident logic: PASS.
6. OOH inventory expanded or source limitation documented: PASS; 245 -> 875 assets.
7. OOH markers are smaller: PASS.
8. No old HGL positioning appears: PASS by validator.
9. No individual-level personal data appears: PASS by validator.
10. No actual residents / actual children claims appear as primary building facts: PASS.
11. Build passes: PASS.

## Required caveats
- Capacity is modeled from public building/property data.
- Capacity and under-5 signals are not actual residents or children.
- OOH availability must be vendor-confirmed.
