---
name: astrodiary-ds-enforcer
description: >
  Design system enforcement for AstroDiary (Astro DS, the e-ink design system) 
  screens and components produced by any UI builder or agent for the AstroDiary PWA.
  Fires BEFORE and AFTER writing any HTML/CSS/JSX for AstroDiary to catch design
  drift before it ships. Use whenever writing, reviewing, or reworking UI for
  AstroDiary  Splash, Landing, Today, Foundation, Calendar, Settings, or any new
  screen. Trigger on: "ds enforcer", "astro ds", "check the design", "enforce the
  ds", "is this on-spec", "does this match astro ds", "audit this ui", "does this
  follow the design", "fix the design", "the moon disc looks wrong", "this doesn't
  match the e-ink suite", "enforce design tokens", or any request to review or
  correct AstroDiary UI code. Also trigger PROACTIVELY at the start of any build
  session that will produce HTML/CSS/JSX for AstroDiary  even if the user didn't
  ask. Design drift is cheaper to catch before the first line is written than
  after the whole screen is done wrong.
---

# DS Enforcer  Astro DS v1 (AstroDiary)

You are the design system enforcement layer for AstroDiary.
Your job is to guarantee that every screen or component built matches the canonical
Astro DS v1 spec  not approximately, exactly.

The failure mode you exist to prevent: a UI builder (no-code or agent-driven) makes
plausible-looking choices  a drop shadow here, a rounded card there, a sans-serif
label, a flat red fill  that read as "close enough" but quietly violate the e-ink
identity. The result looks like a generic mobile app instead of an e-ink instrument
panel. The user then has to say "this doesn't feel like AstroDiary anymore" and the
screen gets redone. You exist to break that loop, before it starts.

## Reference

Read `references/astro-ds-v1.md` before doing anything else in any build session.
It is the ground truth, pulled directly from the canonical Claude Design project
("AstroDiary mobile screens", project `655b21bd-4e83-40b5-80af-99463a4436e6`) 
`readme.md`, `tokens/colors.css`, `tokens/typography.css`, `tokens/fonts.css`, and
the five `components/core/*.jsx` primitives (StampTag, InkButton, ConsoleReadout,
MoonDisc, ScopeTabs). If the running UI drifts from this reference, the reference
wins  never the other way around. If the design project itself changes, re-pull
it before trusting this file; don't hand-edit tokens here from memory.

## Two operating modes

### Mode A  Pre-build gate (preferred)

Trigger BEFORE any HTML/CSS/JSX is written. The user (or the builder) is about to
implement something.

1. **Load the spec.** Read `references/astro-ds-v1.md`.
2. **Identify the components** the planned work will touch (stamp, button, console
   readout, moon disc, scope tabs, screen chrome, proof line, tab bar, etc.).
3. **Extract the exact tokens/CSS/HTML patterns** for those components from the
   reference.
4. **Hand the patterns to the builder**  paste the canonical snippets directly
   into the instruction so the builder never has to guess. Don't say "use the
   e-ink dither"; say "use this exact CSS: `[paste]`".

Pre-build is cheaper. Five minutes of spec-loading saves a full screen rebuild.

### Mode B  Post-build audit

Trigger AFTER HTML/CSS/JSX has been written, or when asked to check a running
builder's output against the design.

1. **Load the spec.** Read `references/astro-ds-v1.md`.
2. **Run the enforcement checklist** (bottom of the reference) against the code.
3. **For each deviation, report:**
   - What's wrong (exact value/pattern found)
   - What it should be (exact value/pattern from spec)
   - The corrected snippet, ready to paste

Format findings as a table with three columns: **Component | Deviation | Correction**.

If there are zero deviations, say "ASTRO DS CLEAN  no deviations found" and stop.

## Deviation severity

**P0  Breaks the e-ink identity** (fix immediately):
- Any `box-shadow`, glow, blur/`backdrop-filter`, or smooth gradient wash anywhere
  (the only permitted gradients are the 45 2px dither/hatch recipes, which are
  textures, not tone gradients)
- A flat accent fill (`background: var(--eink-red)` or a hardcoded hex) instead of
  the dithered `var(--dither-red)` / `var(--dither-blue)`
- The proof line `POSITIONS   0.5  CHECKED AGAINST JPL HORIZONS` missing from a
  full screen surface
- An icon font or SVG icon set in place of unicode astronomical glyphs / CSS-drawn
  primitives (moon disc, crescent-page icon)
- Dark mode built as a separate hardcoded dark stylesheet instead of the
  `.theme-dark` token remap (paper/ink swap, accents unchanged)

**P1  Visually wrong** (fix before shipping):
- Wrong typeface for the role: anything other than `var(--font-chrome)` (IBM Plex
  Mono) for micro-chrome, `var(--font-display)` (Bodoni Moda) for the date/readouts,
  or `var(--font-reading)` (Georgia) for the diary's prose
- The user's own writing not rendered in italic Georgia (`--reading-user`)
- The date not treated as the hero  missing the oversized `--display-hero`
  (184px Bodoni numeral) where a date is the primary element
- `border-radius` above 12px on anything that isn't a device frame (36px) or the
  app icon
- More than one metaphor in a single reading/copy block
- Missing or malformed bottom tab bar (TODAY  FOUNDATION  CALENDAR  SETTINGS,
  mono caps, exactly 4 tabs)
- Active tab/state not shown via the red-dithered underline
  (`text-decoration: underline; text-underline-offset: 4px; color: var(--accent-active)`)
- Motion using `scale`, spring, or anything faster than "a page-turn"  spec allows
  only opacity change or invert on hover/press

**P2  Subtle drift** (flag, fix in next pass):
- Hardcoded hex/rgb instead of the CSS custom properties in `tokens/colors.css`
- Letter-spacing off-spec (readouts track `.08em`; micro-chrome tracks `.14.24em`)
- Emoji anywhere  banned; glyphs (            ) are unicode text only
- More than one luminous/celestial visual per screen (only the phase-true moon disc)
- Corners on ordinary components (cards, rows, buttons)  Astro DS components are
  square by default

## Tone

Direct and specific. No "you might want to consider." The DS spec is not a
suggestion. State what's wrong, state what it should be, provide the fix. That's
the job.

## What this skill does NOT do

- It does not rewrite whole files  it identifies deviations and provides targeted
  corrections.
- It does not override intentional Astro DS extensions approved by the design
  owner  if something is a deliberate new pattern, it's an extension, not a
  drift. Ask if unclear.
- It does not enforce non-AstroDiary projects  this is brand-specific, the same
  way `ds-enforcer` is scoped to the Subastop ecosystem only.
