# V4 Building Capacity QA

## Status: PASS

- Full visual 3D building features: 8895
- Residential capacity overlay features: 7066
- All six target ZIPs have non-zero visual 3D building massing counts.
- Non-residential buildings are set to 0 residential capacity by the model/validator.
- Primary building metric is now HGL Building Opportunity Score, supported by residential capacity units and under-5 capacity signal.

| ZIP | visual 3D buildings | residential capacity buildings | commercial / non-residential | unmatched / unknown |
|---|---:|---:|---:|---:|
| 10003 | 1830 | 1467 | 363 | 188 |
| 10010 | 603 | 372 | 231 | 84 |
| 10011 | 1990 | 1624 | 366 | 272 |
| 10012 | 1098 | 881 | 217 | 182 |
| 10013 | 1357 | 926 | 431 | 372 |
| 10014 | 2017 | 1796 | 221 | 175 |

## Caveat
Capacity is modeled from public building/property data; it is not actual residents or children.
