# Screenshot Review Issues — Round 2

## A. Spatial accuracy issues
- Some earlier modeled surface overlays appeared skewed or visually offset against the basemap because block-like rectangles were generated as synthetic lon/lat grid cells rather than official geometry.
- Street ribbons needed to use actual OSM street geometry rather than inherited ZIP/ZCTA centroids or aggregate ZIP values.
- Building coverage was too narrow and did not cover the full six-ZCTA study area.
- OOH points needed expanded network-level coverage and smaller markers.

## B. Visual encoding issues
- ZIP overview could dominate the map visually.
- 3D heights were either too weak in some fine-grain views or too visually dominant in broad views.
- Color contrast was too muddy and did not make high-value areas obvious.
- Legend domain handling could show invalid values such as infinity when data arrays were empty.
- OOH circles were too large and visually overwhelming.

## C. Data-model issues
- Street scoring appeared too dependent on ZIP-level values.
- Building estimates were too sparse and too weak.
- Fine-grain layers risked false precision if not clearly labeled as modeled estimates.
- OOH inventory depth was insufficient for a client-facing inventory map.

## D. UI/UX issues
- Geography, map mode, metric, overlays, and sliders were all visible at once and confusing.
- Bottom table occupied too much map area.
- Tooltips were too dense and too technical.
- Some labels exposed internal modeled IDs rather than client-readable labels.

## E. Client-facing language issues
- The map needed to preserve corrected HGL ART positioning as multilingual early childhood education / preschool-style school integrating English, Mandarin Chinese, Spanish, and art-based education.
- Tooltip and caveat language needed to emphasize estimates and aggregate data, not actual residents or household facts.
