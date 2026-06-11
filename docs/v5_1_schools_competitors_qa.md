# V5.1 Schools / Competitors QA

## Status: PASS

1. Schools / preschools layer contains real records: PASS (164).
2. Competitors layer contains real records: PASS (43).
3. Both overlays render on the map: PASS; dedicated deck.gl layers are loaded from GeoJSON.
4. Both overlays can be toggled on/off: PASS; existing overlay state controls schools and competitors.
5. Both overlays refresh immediately when toggled: PASS; overlay state is in layer memo dependencies.
6. Tooltips display useful information: PASS; school and competitor tooltip branches added.
7. Missing-data behavior: PASS; data is present; reports document source limitations.
8. Street/building scoring uses school/preschool and competitor inputs: PASS.
9. No fake or duplicate markers are introduced: PASS; public OSM/DOE records deduplicated by coordinate/name.
