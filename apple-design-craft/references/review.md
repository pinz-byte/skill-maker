# Review and correction

Use to audit an existing artifact or verify a completed change. Read the relevant craft module only when a finding needs its technical detail; do not redesign before observing the result.

## Result and handoff

For an audit-only request, deliver prioritized findings with observed location,
user impact, a concrete correction, and the check that would prove it fixed.
Do not mutate the artifact unless the user also requested fixes.

For authorized implementation work, correct the most consequential observed
mismatch and recheck the affected behavior. Report what changed, what passed,
and what could not be inspected. Match the checks to the delivered scope:
a static hero does not require a frame-sequence performance exercise.

## Verification and delivery

Choose the applicable checks below. Inspect the actual artifact when execution tools are available:

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

A screenshot can support visual findings; it cannot prove working interactions.
Separate source-backed guidance, design judgment, and hypotheses to test.
