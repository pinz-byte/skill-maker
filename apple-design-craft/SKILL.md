---
name: apple-design-craft
description: >
  Design, implement, or audit Apple-inspired websites and interfaces using
  source-backed HIG and WWDC principles: clear hierarchy, typography, purposeful
  depth, continuous corners, fluid interaction, and progressive disclosure.
  Trigger on "Apple design", "diseno Apple", "Apple-style landing page",
  "squircle corners", "scroll product animation", or "chunked scrollytelling".
  Includes visual review, accessibility, reduced-motion and performance fallbacks.
  For Pagebuilder Factory orchestration use factory-gate; for brand compliance
  use ds-enforcer or astrodiary-ds-enforcer. This skill supplies design craft
  within the existing design system.
metadata:
  intent: build
---

# Apple Design Craft

Translate Apple's design principles into decisions people can see and use.
Preserve the project's brand, tokens, stack, and requested scope. Choose techniques
for the person's task: product storytelling, an everyday workflow, and a dense
comparison require different compositions.

Read [references/apple-evidence.md](references/apple-evidence.md) when establishing
the design direction or checking an Apple attribution. It maps primary sources to
decisions and separates native-platform guidance from adaptations for the web.

## Workflow

1. Inspect the existing page or interface, design system, available product assets, target
   devices, and requested outcome. Infer from the project where possible; ask
   only for missing information that changes the design. For advice-only requests,
   deliver a design specification instead of editing or installing dependencies.
2. State the person's goal and the observable success criterion. For a product
   page, identify its promise, proof, and next action. For an application, identify
   the main task, orientation cues, feedback, and recovery path. Name assumptions.
3. Resolve hierarchy, reading order, typography, spacing, and action priority
   before choosing corners, materials, or motion. Record the reason for each major
   choice. Prefer the existing toolchain and the lightest adequate effect.
4. Deliver an artifact at the requested fidelity. A mockup needs a visible
   composition; an implementation needs working behavior. If asked to work frame
   by frame, complete the requested frame before expanding the sequence. Keep
   review annotations outside the product composition.
5. Inspect the actual result, fix the most consequential mismatch, and recheck.
   Use the verification section; report observed results and anything untested.

## Human needs and design direction

WWDC17's *Essential Design Principles* explicitly connects design to safety and
predictability, knowledge and understanding, achievement, and beauty and joy.
Use these as review questions: can people anticipate an action, understand their
options, finish their task, and enjoy the experience? They are not conversion
guarantees or a prescription for a visual style.

For the current HIG principles and their dates, consult the evidence reference.
Translate relevant principles into concrete choices rather than attaching an
Apple label to a generic layout.

## Clarity, hierarchy, and restraint

- Give the page or task one clear visual entry point. For a marketing hero, make
  the promise dominant, the explanatory subtitle secondary, and the main action
  recognizable. A second emotional headline must not compete with the first.
- Use a layout grid and existing spacing tokens. Group related items more tightly
  than unrelated ones; inspect optical alignment, line wrapping, and rhythm at
  actual viewport sizes. Empty space should clarify relationships.
- Express product benefits with evidence: a useful screenshot, result, detail,
  or demonstration. Do not invent metrics, testimonials, or product capabilities.
- Establish action priority without deleting useful alternatives. Preserve
  navigation, comparison, cancellation, and recovery when they serve the task.
  Repeated primary actions should have consistent labels and real destinations.
- Remove an element when the task and meaning survive its removal. Keep needed
  prices, conditions, and specifications accessible before a commitment.

## Typography and optical craft

- Define roles for display, heading, body, label, and supporting text using the
  project's type system. Check size, weight, leading, measure, and contrast as a
  composition. Use readable weights; thin lettering is not an Apple requirement.
- In native Apple UI, prefer system text styles and support Dynamic Type. On the
  web, use the existing licensed typeface or a suitable system stack, scalable
  text, and layouts that survive zoom and longer translations. Do not transplant
  native point-size tables into CSS pixel requirements.
- Use optical sizing when the chosen font and renderer support it. Inspect icons
  beside text, button labels, baselines, nested padding, and awkward headline
  breaks. Check the rendered result before claiming optical refinement.

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

## One idea at a time

- Give each section one dominant benefit, one leading visual, and a concise
  headline. Include enough proof to make the claim credible. Example: processing
  speed -> camera detail -> battery endurance -> comparison -> purchase.
- Let content determine height. A focused section need not occupy exactly one
  viewport; avoid clipping copy or creating empty scroll distance on small screens.
- Use pinned scenes only when the extra scroll explains a meaningful transition.
  Release them predictably. Keep reading order and essential text in semantic DOM
  content, even when visuals are drawn on canvas.
- Keep the primary action easy to find. A sticky CTA is optional; ensure it does
  not obscure content, keyboard focus, or mobile controls. Keep useful specs and
  comparisons available when the user's task requires them.
- Distinguish sequential storytelling from progressive disclosure. Disclosure
  reveals relevant detail when needed, through an accessible expansion, a detail
  view, or a contextual step. A long page of viewport-sized sections alone does
  not implement it. Retain discoverability and preserve a useful summary.

## Verification and delivery

Check the actual artifact when execution tools are available:

- Desktop and mobile: readable type, unclipped sections, consistent corners,
  reachable actions, and no horizontal overflow or obstructed focus.
- Hierarchy and craft: inspect the first viewport and the whole sequence. Confirm
  the intended entry point, secondary levels, spacing, type wraps, optical
  alignment, image crops, and action priority. A blur test can diagnose emphasis;
  it does not establish usability.
- Interaction: check keyboard navigation, accessible names, focus visibility,
  loading/empty/error/success states where relevant, and recovery. Test enlarged
  text, contrast, and relevant light/dark or transparency preferences. Do not
  communicate a required state through color or motion alone.
- Motion: fast scrolling, reverse scrolling, resizing, and touch navigation remain
  predictable. Look for dropped frames, long tasks, and memory/network cost on a
  representative device; simplify when the effect cannot run smoothly.
- Reduced motion: honor `prefers-reduced-motion` or the platform equivalent.
  Replace spatial motion and unnecessary pinning with a static image and normal
  document flow; preserve the same information and actions. Test runtime preference
  changes when supported.
- Resilience: slow or failed assets do not block reading or navigation. Keep
  essential content usable without animation, and without JavaScript on web pages
  when the project's architecture supports it.

For a design specification, provide section order, corner treatment, motion
purpose/medium, needed assets, and mobile/reduced-motion alternatives. For an
implementation, explain the concrete changes and checks actually performed.
For an audit, prioritize findings by impact and give each an observed location,
the task it obstructs, a specific correction, and a way to verify the correction.
Separate source-backed guidance, design judgment, and hypotheses to test. A
screenshot can support visual findings; it cannot prove working interactions.

## Edge cases

- No sequence assets: use a static product image or a modest transform; identify
  missing assets instead of fabricating a production-ready sequence.
- A data-heavy or comparison task: keep tables and compact layouts where useful;
  scrollytelling is a product-explanation technique, not a universal page template.
- Existing design-system conflict: retain its tokens and propose compatible
  treatments. Do not restyle the whole product to imitate Apple.

## Principles

- Motion earns its place by explaining, orienting, or giving feedback.
- Ground attributions in the linked HIG pages and WWDC talks. The human needs
  above have a primary source; the supplied post's implementation recipes need
  their own evidence before being called universal Apple rules.
- Smooth curves may suggest visual polish; claims about brain responses, ownership,
  desire, or conversion are hypotheses to test, not guaranteed outcomes.
- Do not claim all Apple pages use image sequences, a particular frame count, or
  springs. Distinguish an implementation option from a verified Apple practice.
- Visible polish and functional accessibility belong in the same review. Passing
  a static checklist does not establish visual quality or HIG conformance.
