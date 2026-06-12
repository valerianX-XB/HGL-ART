# V5.5.2 Panel Reopen QA

Scope: UI-only panel reopen fix. No scoring, data model, or building classification changes were made.

| # | QA item | Result | Evidence |
|---:|---|---|---|
| 1 | Desktop left info panel can close | PASS | Info panel has an accessible close button setting `infoOpen=false`. |
| 2 | Desktop left info panel can reopen by clicking Info | PASS | Persistent `Info` floating button toggles `panelState.infoOpen`. |
| 3 | Desktop right controls panel can close | PASS | Controls panel has an accessible close button setting `controlsOpen=false`. |
| 4 | Desktop right controls panel can reopen by clicking Controls | PASS | Persistent `Controls` floating button toggles `panelState.controlsOpen`. |
| 5 | Layers button opens overlay/filter controls | PASS | `Layers` sets `controlsOpen=true` and `layersOpen=true`; panel heading becomes `Layers & Filters`. |
| 6 | Summary button opens summary table | PASS | Persistent `Summary` button toggles `summaryOpen`; bottom drawer renders table only when open. |
| 7 | Buttons remain visible after all panels are closed | PASS | Floating action bar is outside panels, fixed-position, z-index 40; collapsed panels use pointer-events none. |
| 8 | Tablet/mobile panels are collapsed by default | PASS | Initial panel state uses desktop breakpoint; <1024px starts closed. |
| 9 | Mobile Info opens info panel | PASS | Info button opens bottom-sheet info panel. |
| 10 | Mobile Controls opens controls panel | PASS | Controls button opens bottom-sheet controls panel. |
| 11 | Mobile Layers opens overlay/filter view | PASS | Layers button opens controls drawer focused on overlay/filter controls. |
| 12 | Mobile Summary opens bottom summary drawer | PASS | Summary opens bottom sheet with max-height and internal scroll. |
| 13 | Tapping outside closes mobile panels | PASS | Mobile backdrop closes info, controls/layers, and summary. |
| 14 | ESC closes open panels on desktop | PASS | ESC closes topmost open panel in order: summary, layers/controls, controls, info. |
| 15 | No horizontal scrollbar | PASS | Root/app overflow hidden; panels fixed, max-width constrained; hidden panels pointer-events none. |
| 16 | Build passes | PASS | `npm run build` completed successfully; see `logs_v5_5_2_build.log`. |

## Z-index / pointer-events policy
- Map canvas: base layer.
- Tooltip: z-index 28.
- Panels and summary drawer: z-index 30.
- Mobile backdrop: z-index 25, below panels and floating buttons.
- Floating action buttons: z-index 40, always visible/clickable.
- Closed panels use off-screen transforms and `pointer-events:none`.
