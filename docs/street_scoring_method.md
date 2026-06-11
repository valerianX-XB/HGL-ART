# Street Scoring Method

Street opportunity scores are now calculated at the individual OpenStreetMap street-segment level rather than painted directly from raw ZIP/ZCTA values.

## Inputs

Each street segment uses:

- OSM street geometry
- Target ZCTA assignment by segment centroid
- Nearby modeled building density within approximately 120m
- Nearby OOH asset count within approximately 180m
- Aggregate income signal from the assigned ZCTA
- Aggregate children/family signal from the assigned ZCTA
- HGL ZIP/ZCTA opportunity score as a background market context factor

## Score logic

The modeled street score combines:

- Estimated children / family signal
- Nearby building intensity
- Nearby OOH asset density
- Income / premium education signal
- Background HGL opportunity score

This produces a distinct score per street segment.

## Required fields

Each street segment includes:

- street_segment_id
- street_name
- from_intersection
- to_intersection
- adjacent_block_groups
- estimated_resident_signal
- estimated_children_signal
- income_signal
- family_anchor_density
- ooh_asset_density
- competitor_density
- hgl_street_opportunity_score
- score_drivers
- confidence_level
- caveat

## Caveat

Street-level values are modeled opportunity signals based on nearby aggregate census, building, OOH, and family-anchor data. They are not exact street population counts and are not household-level facts.
