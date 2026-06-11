# Data Dictionary

## buildings_enriched.geojson
Real OSM footprint geometry with modeled aggregate fields:
- estimated_residents
- estimated_under5
- estimated_households
- estimated_family_households
- estimated_income_signal
- hgl_building_opportunity_score

All building values are estimates or modeled signals unless explicitly labeled as public property attributes such as floors or footprint geometry.

## block_groups_enriched.geojson
Modeled block-group-like low surface features from aggregate ZCTA data. Not official individual household data.

## census_blocks_enriched.geojson
Modeled census-block-like surface features. Not actual residents or actual children.

## street_segments_enriched.geojson
OSM street segments with modeled opportunity signals.

## ooh_assets_expanded.geojson
OOH asset points with status taxonomy, source, retrieval date, verification need, pricing status, and caveat.
