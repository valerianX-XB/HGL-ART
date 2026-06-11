# Color and Legend Rules

## Color ramp

The map now uses a stronger sequential color ramp:

- Low: pale blue / light neutral
- Mid: teal / green
- High: amber / orange / red highlight

This makes high-value areas easier to identify without using oversized vertical shapes.

## Legend domain handling

Legend values are calculated from finite values only.

Rules:
- Ignore null, empty, NaN, Infinity, and -Infinity.
- Use percentile-bounded ranges where possible to reduce outlier distortion.
- If a metric has no finite values, display `N/A` instead of broken domains.
- Format currency, percentage, score, and integer values in human-readable form.

## Encoding hierarchy

- Color is the primary visual encoding.
- Height is only a subtle secondary cue.
- Buildings use compressed physical massing plus symbolic data lift capped at 6m by default.
- OOH assets use small status-coded points, not large circles or columns.

## Caveat

3D height is normalized for visual comparison only. It does not represent physical building height except where the building massing layer uses compressed physical height.
