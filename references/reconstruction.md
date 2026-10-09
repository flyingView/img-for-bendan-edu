# Software reconstruction and delivery

Break the last generated draft into panels, labels, shapes, arrows, plots and genuine research imagery. Choose a tool based on what must remain editable:

| Content | Typical suitable tools |
| --- | --- |
| Quantitative plots | Matplotlib, R/ggplot2, or the user's existing statistics software |
| Architecture, workflows and relationships | SVG, TikZ, Graphviz, diagrams.net or Inkscape |
| Freely editable composite layouts | PowerPoint, Illustrator or Inkscape |
| Spatial geometry or scientific structures | Blender or a field-specific application |

Record the choice in `redraw/plan.md` using the [redraw template](../assets/templates/redraw-plan.md). Trial a representative panel when tool suitability is uncertain. Preserve the final draft's composition, proportions, hierarchy and color meanings while correcting its errors.

## A few implementation cues

- Route connectors to clear attachment points; avoid crossings, label collisions and ambiguous arrow endpoints. Group related objects and keep reusable styles consistent.
- Match colors to data semantics and pair important distinctions with a label, marker or line type. Keep legends readable and consistent across panels.
- Plot real values, units, uncertainty and missing observations accurately. Check that axis ranges and shared color scales preserve the intended comparisons.
- Verify physical output size after export. Cropping may change dimensions; editable text depends on font availability. Keep editable source even if delivery requires outlined fonts.

Build actual vector objects, text, data-driven plots or a reproducible scene. For real research images, retain their source and processing record.

Save source/code and used data under `redraw/` and `data/`. Export an appropriate manuscript format plus a PNG preview under `final/`, with caption/insertion and reproduction instructions. Choose actual dimensions and resolution for the target publication; verify publisher rules when a specific venue is named.

Open the delivered files at manuscript size. Check scientific meaning, the six figure expression rules, fonts, legend, clipping and layout. Compare with the last draft, then re-export from saved source. Record the result in `delivery.md` using the [delivery template](../assets/templates/delivery.md).
