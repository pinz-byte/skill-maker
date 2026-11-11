---
name: apple-design-craft
description: >
  Design or implement Apple-inspired product pages using continuous corners,
  tactile scroll-linked motion, and one-idea-at-a-time scrollytelling. Trigger on
  "Apple-style landing page", "squircle corners", "scroll product animation",
  or "chunked scrollytelling". Includes reduced-motion and performance fallbacks.
  For Pagebuilder Factory orchestration use factory-gate; for brand compliance
  use ds-enforcer or astrodiary-ds-enforcer. This skill supplies design craft
  within the existing design system.
metadata:
  intent: build
---

# Apple Design Craft

Turn product benefits into a clear visual story with continuous corners,
user-controlled motion, and focused sections. Apply only the techniques that
help explain the product; all three are optional. Preserve the project's brand,
tokens, stack, and the user's requested scope.

## Workflow

1. Inspect the existing page, design system, available product assets, target
   devices, and requested outcome. Infer from the project where possible; ask
   only for missing information that changes the design. For advice-only requests,
   deliver a design specification instead of editing or installing dependencies.
2. State the main product promise and desired next action. Outline the story as
   benefit -> visual evidence -> supporting detail. Identify what each proposed
   animation teaches and what remains understandable when it is removed.
3. Choose corner treatment, section sequence, and motion approach using the
   guidance below. Prefer the existing toolchain and the lightest adequate effect.
4. Deliver the requested implementation or specification. Verify ordinary and
   reduced-motion behavior; report observed results and anything untested.

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

## Verification and delivery

Check the actual artifact when execution tools are available:

- Desktop and mobile: readable type, unclipped sections, consistent corners,
  reachable actions, and no horizontal overflow or obstructed focus.
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

## Edge cases

- No sequence assets: use a static product image or a modest transform; identify
  missing assets instead of fabricating a production-ready sequence.
- A data-heavy or comparison task: keep tables and compact layouts where useful;
  scrollytelling is a product-explanation technique, not a universal page template.
- Existing design-system conflict: retain its tokens and propose compatible
  treatments. Do not restyle the whole product to imitate Apple.

## Principles

- Motion earns its place by explaining, orienting, or giving feedback.
- Treat safety/predictability, understanding, achievement, and joy as useful
  review questions, not an attributed Apple framework without a primary source.
- Smooth curves may suggest visual polish; claims about brain responses, ownership,
  desire, or conversion are hypotheses to test, not guaranteed outcomes.
- Do not claim all Apple pages use image sequences, a particular frame count, or
  springs. Distinguish an implementation option from a verified Apple practice.

Primary references for implementation decisions (check current platform details):

- [Apple HIG: Motion](https://developer.apple.com/design/human-interface-guidelines/motion)
- [SwiftUI continuous corners](https://developer.apple.com/documentation/swiftui/roundedcornerstyle/continuous)
- [WebKit: Responsive Design for Motion](https://webkit.org/blog/7551/responsive-design-for-motion/)
