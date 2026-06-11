# Methodology

The v2 map upgrades the prior ZIP/ZCTA overview into a street/building/OOH intelligence map while preserving public safety and the corrected HGL ART positioning.

## Data hierarchy

- ZIP/ZCTA overview: Census Reporter TIGER 2024 ZCTA polygons plus corrected aggregate research package fields.
- Block-group surface: modeled low-height surfaces derived from ZCTA aggregate data where official block-group joins were not available in this build. These are directional visualization surfaces, not official household records.
- Census block surface: modeled sub-surfaces derived from aggregate ZCTA/block-group-like surfaces. They are not individual-level data.
- Building massing: OSM building footprints clipped to the target study area. Building resident and child signals are modeled from aggregate census/ZCTA indicators and heuristic public-footprint measures. They are not actual building populations.
- Street ribbons: OSM highway segments clipped to the target area, scored using nearby aggregate ZIP/ZCTA signals.
- OOH assets: corrected OOH candidate inventory expanded into a public-safe asset schema with strict availability status and verification fields.

## Height logic

No raw metric is used directly as height.

- ZIP overview default max height: 45m; hard cap: 90m.
- Block group surface default max height: 35m.
- Census block surface default max height: 25m.
- Street ribbon default max height: 8m.
- Building height multiplier default: 0.35.
- Building height cap default: 80m.
- Market-data lift on buildings is capped at 12m.

Use color for primary comparison; height is only a subtle visual cue.
