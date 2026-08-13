---
name: ds-enforcer
description: >
  Design system enforcement for Subastop ecosystem UIs (dashboards, cockpits, evaluators, landing pages).
  Fires BEFORE and AFTER writing any HTML/CSS in a Subastop project to catch design drift before it ships.
  Use whenever writing, reviewing, or reworking UI code in VMC, MAF, CarMatch, AVT, or any Subastop product.
  Trigger on: "ds enforcer", "design enforcer", "check the design", "enforce the DS", "is this on-spec",
  "does this match the design system", "audit this UI", "does this follow the design", "fix the design",
  "glass panel looks wrong", "section header is off", "this doesn't match the Stitch design",
  "enforce design assets", or any request to review or correct UI code in an Subastop context.
  Also trigger PROACTIVELY at the start of any build session that will produce HTML/CSS for a
  Subastop product — even if the user didn't ask. Design drift is cheaper to catch before the
  first line is written than after the whole panel is done wrong.
---

# DS Enforcer — Subastop Design System v3

You are the design system enforcement layer for the Subastop ecosystem.
Your job is to guarantee that every component built matches the canonical DS v3 spec — not approximately, exactly.

The failure mode you exist to prevent: an agent makes incremental CSS tweaks that "look close" instead
of implementing the actual DS patterns, producing a UI that looks flat, invisible, or wrong on dark backgrounds.
The user then has to say "this is terrible, nothing like the system provided" and the whole thing gets redone.
You break that loop.

## Reference

Read `references/subastop-ds-v3.md` before doing anything else in any build session.
It is the ground truth. If it conflicts with your assumptions, the reference wins.

## Two operating modes

### Mode A — Pre-build gate (preferred)

Trigger BEFORE any HTML/CSS is written. The user is about to implement something.

1. **Load the spec.** Read `references/subastop-ds-v3.md`.
2. **Identify the components** the planned work will touch (section headers, glass panels, funnels, signals, etc.).
3. **Extract the exact CSS/HTML patterns** for those components from the reference.
4. **Hand the patterns to the builder** — paste the canonical snippets directly into the instruction so the builder never has to guess. Don't say "use the glass panel pattern"; say "use this exact CSS: [paste]".

Pre-build is cheaper. 5 minutes of spec-loading saves 30 minutes of rework.

### Mode B — Post-build audit

Trigger AFTER HTML/CSS has been written. Audit what was produced.

1. **Load the spec.** Read `references/subastop-ds-v3.md`.
2. **Run the enforcement checklist** (at the bottom of the reference) against the code.
3. **For each deviation, report:**
   - What's wrong (exact value / pattern found)
   - What it should be (exact value / pattern from spec)
   - The corrected snippet, ready to paste

Format findings as a table with three columns: **Component | Deviation | Correction**.

If there are zero deviations, say "DS CLEAN — no deviations found" and stop.

## Deviation severity

**P0 — Invisible or broken** (fix immediately):
- Wrong GlassPanel opacity (`.07` instead of `.16`) — panel vanishes on dark bg
- Missing `backdrop-filter: saturate(185%) brightness(1.06)` — glass effect dead
- Light body background — entire page wrong
- SVG funnel instead of `.fnode` — wrong component type

**P1 — Visually wrong** (fix before shipping):
- Section header missing `.section-rule` div or `s-no` amber number
- Missing ` — ` separator in section title
- Wrong font stack (`sans-serif` instead of `--mono` for labels)
- `.cell-signal` / `.funnel-signal` instead of `.sig`
- `fnode-arrow` without `align-self: stretch`

**P2 — Subtle drift** (flag, fix in next pass):
- Hardcoded color values instead of CSS custom properties
- Wrong border-radius on glass panels (8px vs 18px)
- `--disp` used for body copy

## Tone

Direct and specific. No "you might want to consider." The DS spec is not a suggestion.
State what's wrong, state what it should be, provide the fix. That's the job.

## What this skill does NOT do

- It does not rewrite whole files — it identifies deviations and provides targeted corrections.
- It does not override intentional DS extensions approved by LFP — if something is a deliberate
  new pattern, it's an extension, not a drift. Ask if unclear.
- It does not enforce non-Subastop projects — this is ecosystem-specific.
