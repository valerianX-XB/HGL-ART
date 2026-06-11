# Fix Round 2 QA Report

## Status

PASS. Validation and production build completed successfully.

## Build commands

- `npm run prepare:data`: PASS
- `npm run validate:data`: PASS
- `npm run build`: PASS

## Screenshot captures

Saved current-state QA screenshots:

- `docs/screenshots/01_building_mode.png`
- `docs/screenshots/02_street_mode.png`
- `docs/screenshots/03_zip_overview.png`
- `docs/screenshots/04_ooh_inventory.png`
- `docs/screenshots/05_heatmap.png`

## Main fixes verified

- Spatial alignment improved with official TIGERweb block group / block geometries, OSM building footprints, OSM street geometries, and LinkNYC KML point geometry.
- Synthetic grid surfaces no longer drive primary block group display.
- Building coverage increased to 3500 features.
- Street segment coverage increased to 2045 features.
- OOH asset inventory increased to 227 assets.
- OOH markers reduced in radius and status-coded.
- Bottom table is collapsed by default.
- UI advanced sliders are contextual and hidden under an Advanced visual controls disclosure.
- Legend now handles finite values and avoids infinity domains.
- Color ramp increased contrast.
- Height caps updated: ZIP 25m default / 45m cap; block group 22m; census block 14m; street 12m; building cap 80m; data lift 6m default.
- Tooltips use estimated / modeled language.
- No old HGL positioning language detected by validator.

## OOH inventory by type

{
  "LinkNYC": 218,
  "Subway / MTA": 1,
  "Bus shelters": 7,
  "Wallscapes": 1
}

## OOH inventory by status

{
  "Network bookable": 217,
  "Potentially bookable": 8,
  "Candidate to verify": 2
}

## Remaining limitations

- Building and street values remain modeled estimates, not actual residents or household-level facts.
- Block group and block attributes use official geometry with modeled attributes from the corrected research package; they should be interpreted as directional surfaces.
- OOH availability, pricing, impressions, and exact unit selection require vendor confirmation.
- HGL license/legal category, exact address, and staffing/curriculum claims require client confirmation before live creative.
