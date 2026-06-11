# Spatial Alignment QA

## Fixes applied

- Replaced synthetic grid-only block group surfaces with official Census TIGERweb block group geometries where available.
- Replaced synthetic block rectangles with official TIGERweb census block geometries where available.
- Expanded building footprints with OpenStreetMap building geometry queried per target ZCTA bounding box.
- Street ribbons now use OpenStreetMap highway geometries and no longer inherit ZIP centroids.
- OOH assets now combine the corrected OOH research inventory with expanded LinkNYC KML points clipped to the target ZCTA polygons.

## CRS / coordinate system

All public GeoJSON is stored in WGS84 longitude/latitude coordinates, EPSG:4326, which is the expected coordinate system for deck.gl and MapLibre GeoJSON layers.

## Spot-check logic

The data preparation script uses:
- Census Reporter TIGER 2024 ZCTA polygons for target study areas.
- Census TIGERweb block group and census block geometries in WGS84.
- OpenStreetMap building and street geometries in WGS84.
- LinkNYC KML coordinates in WGS84.
- Centroid-in-polygon assignment to target ZCTA polygons.

## Sample alignment checks

The following sample classes were checked by source and geometry type:

1. ZCTA 10003 polygon: Census Reporter TIGER geometry.
2. ZCTA 10010 polygon: Census Reporter TIGER geometry.
3. ZCTA 10013 polygon: Census Reporter TIGER geometry.
4. Block group surfaces: TIGERweb geometry layer 8, WGS84.
5. Census block surfaces: TIGERweb geometry layer 12, WGS84.
6. Building footprints: OSM building ways, WGS84.
7. Street ribbons: OSM highway ways, WGS84.
8. LinkNYC assets: LinkNYC KML, WGS84.
9. Existing OOH candidate points: corrected research package coordinates.
10. Micro-market grid: derived from official block group polygons, not synthetic screen-space geometry.

## Remaining limitations

- OSM building footprints may be incomplete or vary in quality.
- Building estimates are modeled and are not actual residents or households.
- Some OOH locations are intersections or corridor approximations from source files and still require vendor confirmation.
