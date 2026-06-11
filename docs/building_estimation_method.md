# Building Estimation Method

Building footprints are sourced from OpenStreetMap building ways in the study area. Each footprint is assigned to a target ZCTA by centroid-in-polygon testing.

Estimated resident and child signals are modeled from aggregate ZCTA data and public footprint attributes. They do not represent actual residents, children, families, or households.

Visual building height uses compressed physical massing:

`display_height_m = min(building_height_m * 0.35, 80) + data_lift_m`

`data_lift_m` is symbolic and capped at 12m.

Confidence is Low-Medium by default because unit counts and official tax-lot joins are not fully verified in this public build.
