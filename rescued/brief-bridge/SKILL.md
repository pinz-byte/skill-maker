---
name: brief-bridge
description: >
  Converts an initiative's IB output + design tokens + real copy into a ready-to-paste
  Stitch prompt that generates the complete HTML/CSS site. Use this skill whenever the
  user says "brief bridge", "crear el brief de [iniciativa]", "promptear a Stitch",
  "preparar el sitio de", "armar el brief para diseño", "llenar el brief bridge", or
  whenever an IB has just been completed and the next step is moving to design.
  Also trigger when the user says "necesito el prompt para Stitch", "vamos con el diseño",
  "Task C", or "siguiente paso después del IB". This skill is the bridge between strategic
  intention (IB) and visual execution (Stitch). Fire it any time a new initiative needs
  a design prompt — it works for any site in the ecosystem, not just Subastop.
---

# Brief Bridge — IB → Stitch Prompt

You are executing the BRIEF BRIDGE process: converting an initiative's strategic brief
into a single, paste-ready chat prompt for Stitch that produces the complete HTML/CSS
site. This is Task B of the PAGE_BUILDER pipeline.

## What Stitch needs (and what it doesn't)

Stitch receives **one chat message** and outputs **HTML/CSS files** for the complete site.

It does NOT need:
- Strategy or audience analysis
- Market context or competitive positioning
- Why the site exists

It DOES need:
- Exact design tokens (HEX values, font names, px values)
- Exact page structure (sections in order, layout descriptions)
- Exact copy (real text or clearly marked [COPY_PENDIENTE])
- Non-negotiable technical rules (accessibility, semantics, CSS structure)

Your job is to collect what Stitch needs and assemble it into that one message.

---

## Step 1 — Gather the IB output

Check if an IB has been completed for this initiative. Look for:
- A completed IB in the current conversation
- An IB file in the project directory
- The user pasting IB output

Extract only what's relevant for the brief:
- NECESSITY (what problem this site solves — 1-2 lines max)
- PURPOSE (one line)

If no IB exists, ask: "¿Tienes el IB completado para esta iniciativa? Si no, dame la
necesidad en 1-2 líneas y el propósito en 1 línea — arrancamos desde ahí."

---

## Step 2 — Verify design tokens

You need ALL of these before assembling the prompt. Check what's available from:
- The project's BRIEF_BRIDGE instance (if filled)
- The conversation history
- The initiative's brand assets

Ask only for what's missing. Never invent values.

Required tokens:
```
COLORS (all as HEX):
- Primary (CTA, links, buttons)
- Primary dark (hover state)
- Primary light (tinted backgrounds)
- Secondary (hero bg, header, display text)
- Surface alt (alternate sections)
- Accent (badges, live indicators) — optional

TYPOGRAPHY:
- Display font name + weight (headlines, H1, H2)
- Body font name + weight (body text, UI)
- H1 size as clamp(min, vw, max) — or confirm ARCHITECT base applies

SHAPE:
- Border radius in px (sharp=2-4px / medium=8px / round=16px+)

LOGO:
- Logo on dark background: file path or "use text placeholder"
- Logo on light background: file path or "use text placeholder"
```

If tokens are missing, ask in one grouped question — not field by field.

---

## Step 3 — Build the page map

For each page in the site, collect:
- Page name and slug
- Goal (one line — what conversion/action it drives)
- Primary CTA (button text → destination)
- Secondary CTA if any
- Every section in order: name, layout, content

**Critical rule: no invented copy.**
- If real copy exists (from a document, from the user, from a brand doc) → use it exactly
- If copy is not yet written → mark it `[COPY_PENDIENTE: description of what goes here]`
- Numbers and stats: must be from a verified source. Mark source inline.
  Example: `"19,830 subastas completadas" — source: VMC replay API, March 2026`
  If not verified: `[STAT_PENDIENTE: total subastas — fuente: VMC DB]`

Ask the user for page structure if not already defined. If a BRIEF_BRIDGE instance exists
for this initiative, read it and use Section C as the page map.

---

## Step 4 — Assemble the Stitch prompt

Once you have Steps 1-3 complete, assemble Section D: the Stitch chat prompt.

Use this exact structure — do not deviate from the format:

```
[STITCH PROMPT — {INITIATIVE NAME}]
════════════════════════════════════════════════════════════

ROLE
────
You are a senior UI/UX designer building a complete website.
Output: clean, semantic HTML + CSS — one complete HTML file per page.
Mobile-first (375px base). Desktop breakpoint: 1280px. 8px grid throughout.

WHAT YOU'RE BUILDING
────────────────────
{NECESSITY — 1-2 lines, no strategy jargon}

DESIGN SYSTEM
─────────────
Primary:       {HEX}   ← CTA, links, buttons
Primary dark:  {HEX}   ← hover state
Primary light: {HEX}   ← tinted backgrounds
Secondary:     {HEX}   ← hero backgrounds, headers
Surface alt:   {HEX}   ← alternate sections
Accent:        {HEX}   ← badges, live indicators (omit if not defined)
Text on dark:  #FFFFFF

Display font:  {font name} {weight} — Google Fonts @import
Body font:     {font name} {weight}
H1:            clamp({min}, {vw}, {max})
Border radius: {value}px on all elements (buttons, cards, inputs)
Pills:         9999px — status badges only

Logo dark bg:  {path} OR render "{BRAND}" in white, weight 900
Logo light bg: {path} OR render "{BRAND}" in {secondary HEX}, weight 900

TECHNICAL RULES (non-negotiable)
─────────────────────────────────
- Semantic HTML5: <header>, <nav>, <main>, <section>, <footer>
- Skip link: first element in body, visually hidden, visible on :focus
- All <img>: alt text required. Decorative images: aria-hidden="true"
- Forms: visible <label> above every input — never placeholder-only
- Focus: 3px solid {primary HEX} outline on :focus-visible, offset 3px
- Touch targets: minimum 44×44px
- Body text contrast: minimum 4.5:1 against background
- CTA buttons: maximum contrast — never reduced opacity
- Mobile nav: hamburger button + overlay, aria-expanded on toggle
- Dynamic counters: aria-live="polite" + data-source="static" if hardcoded
- No horizontal scroll on mobile
- No stock photography with generic people
- CSS: custom properties (--var-name) for all design tokens — no Tailwind, no Bootstrap
- JavaScript: only for mobile nav toggle and interactive elements (accordion, counters)
- Section comments in HTML for dev handoff: <!-- SECTION: Name -->
- Image placeholders: CSS geometric shapes in secondary + primary colors, not <img> tags
- Forms: include error state (red border + message below field) and success state

════════════════════════════════════════════════════════════
PAGE {N}: {NAME} ({/slug})
════════════════════════════════════════════════════════════
Goal: {one line}
Primary CTA: "{button text}" → {destination}
Secondary CTA: "{text}" → {destination}  [omit if none]

SECTION 1 — {NAME}
  Layout:   {exact layout description}
  H1:       "{real copy or [COPY_PENDIENTE: description]}"
  Subtitle: "{real copy or [COPY_PENDIENTE: description]}"
  {other elements with real copy}

SECTION 2 — {NAME}
  Layout:   {exact layout description}
  {elements with real copy}

{...all sections in order}

════════════════════════════════════════════════════════════
PAGE {N+1}: {NAME} ({/slug})
════════════════════════════════════════════════════════════
{same structure}

{...repeat for all pages}

════════════════════════════════════════════════════════════
OUTPUT FORMAT
════════════════════════════════════════════════════════════
- One complete HTML file per page — no separate CSS files
- All CSS inside <style> in <head> using CSS custom properties
- Google Fonts via @import at top of <style>
- JavaScript inline at bottom of <body>
- Forms: error state + success state in HTML
- Placeholder images: CSS-drawn geometric shapes
- Deliver each file separately — don't combine all pages into one file
```

---

## Step 5 — Deliver and confirm

Present the assembled Stitch prompt to the user and confirm:

1. Show the full prompt in a code block — the exact text to paste into Stitch
2. Call out any `[COPY_PENDIENTE]` or `[STAT_PENDIENTE]` items — list them explicitly
   so the user knows what still needs to be filled before the design is 100% real
3. Ask: "¿Hay algo que corregir antes de enviarlo a Stitch?"

After confirmation: "Listo para pegar en Stitch. Cuando tengas el HTML de vuelta,
revisamos contra el checklist de post-Stitch antes de pasarlo a dev."

---

## Post-Stitch audit (when HTML comes back)

When the user shares Stitch's HTML output, run this audit before handing to dev:

**Structure**
- Semantic landmarks present (header, nav, main, section, footer)
- Skip link exists and is functional
- One H1 per page, correct heading hierarchy (no skipped levels)

**Copy integrity**
- All copy matches the brief — nothing invented by Stitch
- Numbers have data-source attribute or are marked pending
- CTA text matches brief exactly

**Design system**
- CSS custom properties used consistently for all tokens
- Border radius applied uniformly
- Hover states on all interactive elements
- Mobile nav functional (hamburger + overlay)

**Accessibility**
- Body text contrast ≥ 4.5:1 (verify: webaim.org/resources/contrastchecker)
- All images have alt text
- All form inputs have visible labels
- Focus visible on all interactive elements

**Forms**
- Error state: red border + message below field
- Success state: confirmation message after submit

**Dev handoff**
- HTML valid and complete
- CSS with custom properties, no frameworks
- Section comments in HTML
- Placeholder assets documented with comments

Flag anything that fails. Return a clean pass/fail list to the user.

---

## Rules that never change

1. **No invented copy.** If you don't have the real text, mark it `[COPY_PENDIENTE]`.
2. **No invented numbers.** If you don't have a verified source, mark it `[STAT_PENDIENTE]`.
3. **No invented tokens.** If a HEX value isn't confirmed, ask before proceeding.
4. **One prompt, complete.** The Stitch prompt must cover all pages in one message.
5. **Stitch outputs HTML.** The brief exists to produce HTML — not a strategy doc.
