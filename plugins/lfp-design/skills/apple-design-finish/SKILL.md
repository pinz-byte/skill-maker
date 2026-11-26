---
name: apple-design-finish
description: >
  Refine an existing Apple-inspired composition through corners, materials,
  depth, nested padding, and optical alignment. Trigger on "acabados Apple",
  "squircle corners", or "pulir interfaz Apple". For layout, hierarchy, and
  typography work use apple-design-composition instead.
metadata:
  intent: build
---

# Apple Design Finish

## Scope and execution

Preserve the project's brand, tokens, stack, existing decisions, and requested
fidelity. Inspect the supplied artifact and content before making changes. Ask
only about missing information that materially changes the requested result.
This skill executes its own task directly; no other Apple skill is a prerequisite.
For an explicitly bounded frame or part, deliver it and await feedback before
expanding. Keep implementation notes outside the product interface.

Use to refine an existing composition. Preserve its content, reading order, and action hierarchy unless a concrete defect requires a local correction.

## Result and handoff

Deliver the refined artifact: coherent radius and surface roles, nested padding,
aligned text and icons, and appropriate separation between content and controls.
Inspect it at actual display sizes. Explain only the consequential changes.

A rounded button or a glass card is not by itself an Apple design treatment.
Do not add motion or rebuild the narrative as part of a finish-only request.

## Depth and materials

- Give layering a job: distinguish navigation, an overlay, an active control, or
  a change of context. Define which surfaces contain content and which operate it.
- Native Apple components should follow the target platform and OS version. The
  current HIG reserves Liquid Glass for the functional layer; it is not a reason
  to turn every content card into glass. Prefer supported system components.
- On the web, blur and translucency are optional adaptations. Use opaque surfaces
  when they communicate the relationship more clearly or cost less to render.
  Check text over changing backgrounds and provide appropriate transparency and
  contrast alternatives. Keep focus, dismissal, and the reading order coherent.

## Continuous corners

- Use continuous corner smoothing on appropriate cards, product frames, icons,
  or controls when compatible with the brand. Keep a small family of radius
  tokens; tune smoothing and radius independently when supported.
- A conventional rounded rectangle joins straight edges to circular arcs;
  continuous corners soften that transition. "Squircle", "superellipse", and
  a platform's continuous-corner implementation are related terms, not promises
  of identical geometry. Do not assert exact Apple geometry or G2 continuity
  without inspecting the actual implementation.
- In native Apple UI, use the platform's continuous-corner API when appropriate.
  In Framer or another design tool, verify the current smoothing control rather
  than inventing a property name or numeric range. For web CSS, check target-browser
  support before using newer corner-shape features; provide border-radius as a
  usable fallback. Use SVG/path clipping only when its visual benefit justifies
  the complexity, and preserve visible focus rings and shadows.
- Check small controls and nested containers at actual sizes. Avoid tiny inner
  corners that visually collide with larger outer curves.

## Verify the result

Inspect the rendered artifact at relevant desktop and mobile sizes. Check type
wraps, contrast, enlarged text, padding, crops, overflow, reachable actions, and
visible keyboard focus. Report what was inspected and anything untested. If no
viewer is available, limit conclusions to the evidence you can actually observe.

## Edge cases

If an effect obscures text or focus, use a simpler surface. Keep the existing
brand tokens when an Apple-like treatment would conflict with them.

## Principles

- Apply the guidance only where it serves the requested task.
- Preserve useful navigation, accessible content, and recovery paths.
- Separate observed results from specifications and untested expectations.
- Use [primary sources](references/sources.md) for Apple attributions; recheck
  current implementation APIs when needed. Do not promise conversion effects
  or universal numeric recipes without evidence appropriate to the claim.
