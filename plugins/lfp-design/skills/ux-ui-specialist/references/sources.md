# Sources and repository selection

Reviewed 2026-11-26. This skill is an original synthesis of design practice;
it does not vendor an upstream skill or claim affiliation with these teams.
Links are selective references, not runtime prerequisites. Recheck current
APIs, support, license, and stack fit before choosing a dependency. A library's
accessibility support does not certify a finished application.

## Human behavior, usability, and measurement

- [Jakob Nielsen: usability heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/).
  Use for feedback, predictable interaction, recognition, and error recovery.
  These are broad evaluation heuristics, not empirical proof that a particular
  screen improves completion or conversion.
- [Google Research: user-centered metrics / HEART](https://research.google/pubs/measuring-the-user-experience-on-a-large-scale-user-centered-metrics-for-web-applications/),
  Kerry Rodden, Hilary Hutchinson, Xin Fu, CHI 2010. Use to connect product goals,
  behavioral signals, and metrics. Select relevant measures rather than treating
  engagement volume as a sufficient outcome.
- [WCAG 2.2 quick reference](https://www.w3.org/WAI/WCAG22/quickref/).
  Use the actual success criterion and its exceptions for a web accessibility
  requirement. Conformance depends on the applicable scope and level.
- [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/).
  Use for complex widget semantics, keyboard operation, and focus behavior.
  Guidance and examples support implementation; WCAG supplies conformance criteria.

## Platform systems and implementation repositories

| Source | Useful for | Selection boundary |
| --- | --- | --- |
| [Apple HIG](https://developer.apple.com/design/human-interface-guidelines) | Platform conventions and interaction guidance | Documentation, not a general web component repository or permission to impose Apple styling |
| [Material Design 3](https://m3.material.io/) | Google's system guidance and component patterns | Select the implementation for the actual platform |
| [Material Web](https://github.com/material-components/material-web) | Inspecting Material web components | README reports maintenance mode pending maintainers at review; evaluate support before adopting |
| [AWS Cloudscape components](https://github.com/cloudscape-design/components) and [patterns](https://cloudscape.design/patterns/) | Operational web apps, resource workflows, forms, tables, feedback | Built for AWS experiences; this is not Amazon retail's design system or a universal visual style |
| [Adobe React Spectrum / React Aria](https://github.com/adobe/react-spectrum) | Accessible interaction primitives and custom React design systems | React Aria is unstyled; Spectrum is Adobe's styled system. Preserve the product's own brand |
| [IBM Carbon](https://github.com/carbon-design-system/carbon) | An implementation reference for an established design system | Assess product, stack, and interaction fit rather than adding a second component system |

Prefer the project's established system when it works. For a new React interface
with custom branding, React Aria is a candidate for complex interaction behavior.
For a resource-heavy operational application, evaluate Cloudscape's workflow
patterns. These are conditional selection judgments, not a recommendation to
install either library automatically.

## Existing skills reviewed

- [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill):
  a relevant existing candidate with searchable visual styles, palettes,
  typography, and stack guidance. Its catalog is a design aid; proposed matches
  still need evaluation against real users, tasks, content, and existing tokens.
- [Vercel web-design-guidelines](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines),
  [entrypoint](https://raw.githubusercontent.com/vercel-labs/agent-skills/main/skills/web-design-guidelines/SKILL.md),
  and [web interface guidance](https://vercel.com/design/guidelines):
  useful for focused UI code review. The reviewed entrypoint uses a bundled,
  pinned guideline snapshot. Review coverage is different from understanding
  a product's audience or carrying a new task flow through implementation.

No installation scripts from these repositories are required or executed by
this skill. Consult original sources for attribution; distinguish upstream
documentation from this skill's contextual design judgments.
