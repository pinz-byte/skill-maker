---
name: apple-design-composition
description: >
  Design or implement a static Apple-inspired hero, screen, or page composition:
  hierarchy, typography, spacing, product evidence, and action placement. Trigger
  on "hero Apple", "composicion Apple", or "tipografia estilo Apple". For
  surfaces and corners on an existing layout use apple-design-finish instead.
metadata:
  intent: build
---

# Apple Design Composition

## Scope and execution

Preserve the project's brand, tokens, stack, existing decisions, and requested
fidelity. Inspect the supplied artifact and content before making changes. Ask
only about missing information that materially changes the requested result.
This skill executes its own task directly; no other Apple skill is a prerequisite.
For an explicitly bounded frame or part, deliver it and await feedback before
expanding. Keep implementation notes outside the product interface.

Use for a hero, page layout, or interface structure. Start from the supplied content or existing screen; infer only what is needed for this composition.

## Result and handoff

Deliver the requested visible composition or implemented layout, with real
content, type hierarchy, spacing, image crop, and action placement. Use a static
version first so the reading order can be inspected without motion. A table of
intentions alone does not satisfy a mockup or implementation request.

Check the requested viewport and its mobile adaptation when relevant. Resolve
competing headlines and unreadable copy before proceeding to surface details.
If the task is composition only, stop after delivering this result.

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

## Verify the result

Inspect the rendered artifact at relevant desktop and mobile sizes. Check type
wraps, contrast, enlarged text, padding, crops, overflow, reachable actions, and
visible keyboard focus. Report what was inspected and anything untested. If no
viewer is available, limit conclusions to the evidence you can actually observe.

## Edge cases

If content or assets are incomplete, use clearly identified placeholders only
where the requested fidelity permits them. Do not invent product evidence.

## Principles

- Apply the guidance only where it serves the requested task.
- Preserve useful navigation, accessible content, and recovery paths.
- Separate observed results from specifications and untested expectations.
- Use [primary sources](references/sources.md) for Apple attributions; recheck
  current implementation APIs when needed. Do not promise conversion effects
  or universal numeric recipes without evidence appropriate to the claim.
