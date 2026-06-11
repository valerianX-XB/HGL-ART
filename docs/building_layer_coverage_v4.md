# Building Layer Coverage v4

Sources: NYC Building Footprints (5zhs-2jue) joined to NYC PLUTO/MapPLUTO (64uk-42ks) by BBL where available. Coverage pulled for the six target ZIPs with an approximate 0.5-mile bbox buffer. Confidence is highest where PLUTO UnitsRes and land-use/class are available.

| ZIP | total buildings/lots checked | visual 3D buildings | residential-capacity buildings | commercial / non-residential | unmatched / unknown-use |
|---|---:|---:|---:|---:|---:|
| 10003 | 2018 | 1830 | 1467 | 363 | 188 |
| 10010 | 687 | 603 | 372 | 231 | 84 |
| 10011 | 2262 | 1990 | 1624 | 366 | 272 |
| 10012 | 1280 | 1098 | 881 | 217 | 182 |
| 10013 | 1729 | 1357 | 926 | 431 | 372 |
| 10014 | 2192 | 2017 | 1796 | 221 | 175 |

- Full visual 3D building features: 8895
- Residential capacity overlay features: 7066
- PLUTO target lots without joined footprint in pulled footprint set: 1273
- Non-residential buildings remain in the all-building massing layer but have residential capacity, household capacity, and under-5 capacity signal set to 0.
- All capacity values are public-data modeled signals, not actual residents or children.
