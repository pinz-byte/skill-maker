---
name: apple-design-craft
description: >
  Design, implement, or audit an Apple-inspired page or interface in focused
  parts: direction, composition and typography, surface finish, purposeful motion,
  or review. Trigger on "Apple design", "diseno Apple", "Apple-style landing
  page", "squircle corners", "scroll product animation", or "chunked
  scrollytelling". Select only the parts needed for the requested artifact.
  For factory orchestration use factory-gate; for brand compliance use
  ds-enforcer or astrodiary-ds-enforcer instead.
metadata:
  intent: build
---

# Apple Design Craft

Apply Apple HIG and WWDC principles to the requested artifact. This entrypoint
selects the work; each module supplies its execution detail. Preserve the
project's brand, tokens, stack, and the user's requested fidelity and scope.

## Select the part

Start from the user's request and the existing artifact. State the part and
observable result in one sentence, then do the work. Read only the module(s)
needed for that result, not the whole library.

| Requested work | Read | Concrete result |
| --- | --- | --- |
| Define the promise, brief, or story | [Direction](references/direction.md) | Task/promise, proof, next action, and sequence |
| Design a hero, screen, or page; fix hierarchy or type | [Composition](references/composition.md) | Visible or implemented static composition |
| Refine corners, materials, depth, or optical alignment | [Finish](references/finish.md) | Refined existing composition |
| Add an explanatory transition, gesture, or scroll animation | [Motion](references/motion.md) | Working behavior and its static alternative |
| Audit a result or check a completed change | [Review](references/review.md) | Observed findings or scoped verification |

## Execute within the request

- For a focused request, complete that part. Use an adjacent module only to solve
  a dependency of that result. Do not restart the whole design process.
- For a complete design or build, work through the necessary parts in order:
  direction if unresolved, composition, finish, motion if useful, then review.
  Carry decisions forward and continue within the authorized task. These are
  working parts, not mandatory approval gates or separate planning documents.
- For "frame by frame", "one part at a time", or an explicitly bounded phase,
  deliver that artifact and await feedback before expanding it.
- Use existing content and assets where possible. Ask only for missing information
  that materially changes the result; name reasonable assumptions otherwise.
- Match the output to the request: a mockup needs a visible composition; a build
  needs the implementation; advice needs a specification; an audit needs findings.
  Keep review notes and technical caveats outside the product interface.
- After implementing, use the relevant checks in the review module. Report
  observations and limits; reading instructions is not evidence of visual quality.

## Evidence and edge cases

Read [Apple evidence](references/apple-evidence.md) when explaining an Apple
attribution or resolving a source question. This is supporting evidence, not a
prerequisite research exercise for every design change. Recheck current API or
browser behavior before relying on it in an implementation.

- No sequence assets: use a static image or a modest transform within scope.
- A comparison or data-heavy task: retain useful tables and compact controls.
- An existing design system: adapt the treatment to its tokens and components.
- An unviewable artifact: identify the missing observation and limit conclusions;
  do not claim the design or interaction was visually verified.

## Principles

- Motion explains, orients, or provides feedback; it is optional.
- Keep accessibility and resilience in the part being implemented.
- Attribute the four human needs to WWDC17; preserve the source distinction
  between platform guidance and this skill's web adaptations.
- Do not promise conversion effects, exact Apple geometry, or universal numeric
  recipes without evidence appropriate to that claim.
