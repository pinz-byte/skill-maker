---
name: apple-design-craft
description: >
  Coordinate a complete Apple-inspired design or build spanning multiple
  specialist skills, or handle an explicit apple-design-craft invocation.
  Trigger on "diseno Apple completo" or "Apple-style landing page". For a single
  hero or layout use apple-design-composition; for a focused audit use
  apple-design-review instead. Does not duplicate the specialist instructions.
metadata:
  intent: build
---

# Apple Design Craft

Compatibility entrypoint for complete Apple-inspired work. Each specialist below
is an independent skill and can be invoked directly. Preserve the user's scope,
brand, tokens, stack, and requested fidelity.

## Choose the skill

| Task | Independent skill | Result |
| --- | --- | --- |
| Brief or story | [apple-design-direction](../apple-design-direction/SKILL.md) | Task/promise, proof, next action, and sequence |
| Static layout or typography | [apple-design-composition](../apple-design-composition/SKILL.md) | Visible or implemented composition |
| Surfaces, corners, and optical finish | [apple-design-finish](../apple-design-finish/SKILL.md) | Refined existing composition |
| Transitions, gestures, or scroll animation | [apple-design-motion](../apple-design-motion/SKILL.md) | Working behavior and static alternative |
| Audit or verification | [apple-design-review](../apple-design-review/SKILL.md) | Observed findings or scoped checks |

## Execution

For a focused request, use the matching skill and deliver its result directly.
For a complete build, use only the necessary skills in order: direction if
unresolved, composition, finish, motion if useful, and review. Carry decisions
forward without introducing mandatory approval gates or extra planning documents.
Do not load all specialist instructions for a single-part request.

For "one part at a time" or an explicitly bounded frame, deliver that part and
await feedback before expanding. A mockup needs a visible composition; a build
needs working implementation; an audit needs findings. Report observed checks
and anything untested.

## Evidence and edge cases

[Apple evidence](references/apple-evidence.md) supports source questions. It is
not a mandatory research exercise before every change. Individual specialists
carry their own source pointers and can operate without this router.

If a specialist is not exposed in the skill catalog, read its linked sibling
SKILL.md from the installed plugin when accessible. If it is unavailable, state
that limitation rather than claiming it ran. No agent delegation is required.

## Principles

- Complete the requested scope with the smallest applicable set of skills.
- Keep useful navigation, accessibility, and resilience in the result.
- Do not treat optional motion as a prerequisite for Apple-inspired design.
