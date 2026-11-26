# Motion and direct manipulation

Use only when the requested task calls for animation or interaction behavior, or when a specific transition needs to explain a relationship. A static layout request does not need this module.

## Result and handoff

Identify what the motion explains and select the lightest suitable medium.
Work from the existing composition and assets; do not invent a product sequence.
Deliver the requested working interaction or, for a specification-only request,
its trigger, states, transition, interruption behavior, and static alternative.

Verify input, reverse movement, resizing, asset failure, and reduced motion as
applicable. Keep content and actions usable with the effect removed. Report
which behaviors were actually exercised; an animation description is not a
working interaction.

## Scroll-linked motion that explains

Use rotation, assembly, reveal, or a change of viewpoint to demonstrate a real
property, such as a hinge or lens. Generic stock imagery sliding around the page
rarely earns the rendering and attention cost.

Choose the simplest medium that communicates the change:

| Need | Suitable starting point |
| --- | --- |
| A small position, scale, or opacity change | Existing CSS or animation tooling |
| A fixed, art-directed rotation or assembly | Pre-rendered image sequence |
| A linear demonstration that need not follow scroll | Video with appropriate controls |
| Arbitrary user-controlled viewpoints | Interactive 3D, only with assets and budget |

For an image sequence:

- Map section progress deterministically: `p = clamp((scrollY - start) / distance, 0, 1)`;
  `index = round(p * (frameCount - 1))`. Recalculate geometry after layout changes.
  Ensure a positive scroll distance; use a static image when there is no usable range.
- Select frame count and resolution from the actual motion, bandwidth, and memory
  budget. A range such as 60-150 frames is an example, never an Apple standard.
  Decoded memory is roughly width * height * 4 bytes per frame; compressed file
  size alone does not describe the cost.
- Show a poster immediately. Load and decode a bounded working set, avoid drawing
  unavailable frames, and keep the last valid image or poster on asset failure.
  Prefer a lighter mobile treatment if the sequence does not fit its budget.
- Schedule visual updates with requestAnimationFrame or equivalent framework
  scheduling; avoid repeated layout reads and draws when the index has not changed.
  Pause offscreen work, bound canvas resolution/device pixel ratio, and clean up
  listeners and animation loops.
- Keep scroll progress directly controllable. Springs can suit discrete state
  transitions; use velocity-preserving interruption when supported. Do not add
  spring lag or overshoot to a frame scrubber by default. Reverse scrolling should
  return to the corresponding view immediately and predictably.

Never hijack wheel/touch scrolling or require the animation to finish before a
person can continue.

For direct manipulation, make the response immediate and allow interruption or
retargeting from the current state. WWDC18 supports velocity-aware continuity and
starting elastic transitions without overshoot. Check the selected API: a damping
ratio of 1 is not interchangeable with a library's raw damping coefficient. Keep
gesture-release projection distinct from deterministic scroll-to-frame mapping.

- Use pinned scenes only when the extra scroll explains a meaningful transition.
  Release them predictably. Keep reading order and essential text in semantic DOM
  content, even when visuals are drawn on canvas.
