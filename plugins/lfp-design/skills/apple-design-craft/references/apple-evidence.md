# Apple design: evidence and application

Primary sources checked 2026-11-12. Recheck current guidance when implementing
platform APIs or matching a particular OS. These notes are decision aids, not a
copy of the HIG or a claim that Apple endorses this skill.

## Foundation and attribution

| Source | Supported idea | Use in a design decision |
| --- | --- | --- |
| [HIG: Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles) | The current principles are Purpose, Agency, Responsibility, Familiarity, Flexibility, Simplicity, Craft, and Delight. | Start with the task; preserve control and recovery, familiar patterns, adaptation, focus, refinement, and appropriate emotion. |
| [WWDC17: Essential Design Principles](https://developer.apple.com/videos/play/wwdc2017/802/) | The opening names safety/predictability, knowledge/meaning/understanding, accomplishment, and beauty/joy. Later it discusses wayfinding, feedback, affordance, and progressive disclosure. | Review orientation, understandable consequences, task completion, and experience quality. Reveal secondary complexity while keeping it discoverable. |
| [WWDC18: Designing Fluid Interfaces](https://developer.apple.com/videos/play/wwdc2018/803/) | Direct manipulation, interruptible motion, elastic behavior, and velocity-based projection support continuity. The spring discussion recommends starting without overshoot. | Match motion to intent. Preserve continuity when retargeting; check the API's parameter meanings. |

The current principles page records a June 8, 2026 reintroduction. Treat dated
WWDC concepts as their own sources rather than presenting every historical theme
as the current HIG taxonomy. Native interface guidance can inform web design;
the web adaptation is a design decision, not automatically an Apple mandate.

## Typography, materials, and accessibility

- [HIG: Typography](https://developer.apple.com/design/human-interface-guidelines/typography):
  legibility, visual hierarchy, scalable text styles, and optical sizing matter.
  Its guidance discourages very light weights. Read platform-specific details
  for a native implementation; use appropriate web typography on websites.
- [HIG: Materials](https://developer.apple.com/design/human-interface-guidelines/materials):
  materials communicate layering. Liquid Glass belongs primarily to controls
  and navigation; content uses different treatments. Check contrast over the
  actual background and the effects of accessibility settings.
- [HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility):
  support varied abilities and input methods. Inspect readable content,
  meaningful alternatives, and adjustable presentation throughout the workflow.
- [HIG: Motion](https://developer.apple.com/design/human-interface-guidelines/motion):
  consult when choosing motion's role and adapting it to accessibility needs.
- [SwiftUI: Continuous rounded corners](https://developer.apple.com/documentation/swiftui/roundedcornerstyle/continuous):
  consult for a native corner implementation, not a universal web geometry.
- [WebKit: Responsive Design for Motion](https://webkit.org/blog/7551/responsive-design-for-motion/):
  implementation guidance for reduced-motion preferences on the web.

## How to use the supplied playbook

Keep its emphasis on clarity, depth, restraint, detail, and purposeful movement.
For numerical prescriptions and causal claims, require evidence at that level:

| Claim or recipe | Treatment |
| --- | --- |
| One idea per section | A useful storytelling option. Choose density from the task; do not impose one viewport or one sentence. |
| Progressive disclosure means scrolling through full-screen features | Scrolling sequences ideas; disclosure controls when complexity is exposed. Choose deliberately. |
| One CTA, or no navigation | Give one action priority where appropriate. Keep useful routes and decisions reachable. |
| Every corner must have the same radius | Use a coherent family adapted to size and nesting. Consistency does not require identical radii. |
| Squircle equals Apple's exact shape | Do not equate a generic superellipse with every continuous-corner implementation. |
| Damping = 1 | Valid for a normalized critical damping ratio; not a portable setting across animation libraries. |
| Every product spin uses 60-150 photographs | A possible production technique and example range. Choose media and frame count from assets and budget. |
| Curves imply safety or premium quality; rotation increases ownership or conversion | Treat as hypotheses unless supported by evidence applicable to the design. Measure outcomes rather than promising them. |
| Precise percentages, response thresholds, and attributed quotations | Locate the original source before repeating as a fact. Otherwise omit or label an explicit project target. |

## Review examples

- A landing page has two equally large promises: choose the primary proposition,
  subordinate the supporting line, and inspect both desktop and mobile wraps.
- An analyst dashboard needs simultaneous comparison: keep its useful table and
  filters; improve grouping, labels, and feedback before adding a narrative scroll.
- A glass toolbar crosses a bright image: inspect its legibility in that state;
  choose a more robust material or opaque surface if necessary.
- A requested static hero has no motion assets: deliver the composition with
  typography, product evidence, spacing, and a clear action. Motion is optional.
