# V3 Hover / Overflow QA

- CSS sets html/body/#root/app/mapShell to fixed/clipped overflow hidden.
- Tooltip uses fixed positioning, viewport clamp, and pointer-events none.
- Bottom table scrolls internally; control panel constrained to viewport.
- Hover handler is stable and layers are memoized by state dependencies.
