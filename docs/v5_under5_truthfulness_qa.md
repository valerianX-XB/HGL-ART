# V5 Under-5 Truthfulness QA

## Status: PASS

1. No street tooltip shows block-group Under 5 as street count.
2. No building tooltip shows official Under 5 as building count.
3. Modeled values are labeled capacity signal.
4. Commercial/non-residential buildings have residential capacity 0.
5. All six ZIPs have visual 3D buildings.
6. Public UI distinguishes Official aggregate vs Modeled signal in legend/tooltips.
7. No individual child / household / resident data is implied.
8. Build passes when npm run build exits 0.

Caveat: Street/building values are modeled capacity signals, not actual children.
