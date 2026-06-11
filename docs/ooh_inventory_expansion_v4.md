# OOH Inventory Expansion v4

- Old OOH count: 245
- New OOH count: 875

## Count by vendor
- LinkNYC / Intersection: 555
- JCDecaux / NYC street furniture network: 248
- MTA / OUTFRONT or station media vendor: 53
- Unknown / OSM advertising feature: 9
- JCDecaux: 7
- OUTFRONT / MTA: 1
- OUTFRONT / LinkNYC: 1
- Angel Media: 1

## Count by asset type
- LinkNYC: 556
- Bus shelters: 255
- Subway / MTA: 54
- Candidate walls: 9
- Wallscapes: 1

## Count by ZIP
- buffer/unknown: 843
- 10014: 7
- 10013: 6
- 10003: 5
- 10011: 5
- 10010: 4
- 10012: 2
- 10003/10010: 1
- 10014/10012: 1
- 10014/10011: 1

## Count by status
- Network bookable: 803
- Potentially bookable: 61
- Candidate to verify: 11

## Sources used
- Previous v3 OOH candidate file
- NYC Open Data LinkNYC Kiosk Locations
- NYC Open Data Bus Stop Shelters
- NYS Open Data MTA Subway Stations and Complexes as station-advertising proxies

## Limitations
- Public feeds identify network/location presence, not guaranteed availability, price, impression delivery, or creative specifications.
- Vendor RFP/API acquisition is still required before purchase.
- Assets are deduplicated by rounded coordinate + vendor + asset type; adjacent faces may be collapsed if public feeds lack face-level IDs.
