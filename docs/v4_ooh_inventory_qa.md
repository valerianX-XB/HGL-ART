# V4 OOH Inventory QA

## Status: PASS

- Old OOH count: 245
- New OOH count: 875
- Every v4 OOH asset has source/status/verification fields per validator.
- Marker defaults reduced in src/layers/oohAssetLayer.ts and app default radius is 4 px.
- Not recommended assets are hidden from the default rendered asset layer.

## Counts by asset type
- LinkNYC: 556
- Subway / MTA: 54
- Bus shelters: 255
- Wallscapes: 1
- Candidate walls: 9

## Counts by status
- Network bookable: 803
- Potentially bookable: 61
- Candidate to verify: 11

## Caveat
Availability, pricing, impressions, and exact unit selection require vendor confirmation.
