---
name: apple-design-direction
description: >
  Define an Apple-inspired product brief, promise, information sequence, or
  progressive disclosure plan. Trigger on "Apple design brief", "narrativa Apple",
  or "ordenar la historia del producto". Produces direction and structure; for
  the visible layout use apple-design-composition instead.
metadata:
  intent: build
---

# Apple Design Direction

## Scope and execution

Preserve the project's brand, tokens, stack, existing decisions, and requested
fidelity. Inspect the supplied artifact and content before making changes. Ask
only about missing information that materially changes the requested result.
This skill executes its own task directly; no other Apple skill is a prerequisite.
For an explicitly bounded frame or part, deliver it and await feedback before
expanding. Keep implementation notes outside the product interface.

Use for the brief, product story, or information sequence. Reuse an existing brief; do not reopen settled product decisions.

## Result and handoff

Deliver a short direction: audience/task, primary promise or task outcome,
available evidence, next action, and the ordered concepts or workflow steps.
For a full design request, carry this forward into composition without making
an extra planning document. For a brief-only request, this is the deliverable.

Decide which information stays visible and which is revealed on demand. If the
request is for one hero, do not expand it into a whole landing page.

## Human needs and design direction

WWDC17's *Essential Design Principles* explicitly connects design to safety and
predictability, knowledge and understanding, achievement, and beauty and joy.
Use these as review questions: can people anticipate an action, understand their
options, finish their task, and enjoy the experience? They are not conversion
guarantees or a prescription for a visual style.

For the current HIG principles and their dates, consult [sources.md](references/sources.md).
Translate relevant principles into concrete choices rather than attaching an
Apple label to a generic layout.

## One idea at a time

- Give each section one dominant benefit, one leading visual, and a concise
  headline. Include enough proof to make the claim credible. Example: processing
  speed -> camera detail -> battery endurance -> comparison -> purchase.
- Let content determine height. A focused section need not occupy exactly one
  viewport; avoid clipping copy or creating empty scroll distance on small screens.
- Keep the primary action easy to find. A sticky CTA is optional; ensure it does
  not obscure content, keyboard focus, or mobile controls. Keep useful specs and
  comparisons available when the user's task requires them.
- Distinguish sequential storytelling from progressive disclosure. Disclosure
  reveals relevant detail when needed, through an accessible expansion, a detail
  view, or a contextual step. A long page of viewport-sized sections alone does
  not implement it. Retain discoverability and preserve a useful summary.

## Verify the direction

Check that the sequence supports the stated task, each claim has available
proof, and the next action has a real destination or an explicitly unresolved
one. Keep essential conditions and comparison information discoverable.

## Edge cases

A comparison or data-heavy workflow may need a table and compact controls.
Do not turn it into a long marketing story to fit an aesthetic.

## Principles

- Apply the guidance only where it serves the requested task.
- Preserve useful navigation, accessible content, and recovery paths.
- Separate observed results from specifications and untested expectations.
- Use [primary sources](references/sources.md) for Apple attributions; recheck
  current implementation APIs when needed. Do not promise conversion effects
  or universal numeric recipes without evidence appropriate to the claim.
