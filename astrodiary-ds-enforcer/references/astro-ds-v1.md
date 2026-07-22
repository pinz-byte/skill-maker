# Astro DS v1 — Canonical Reference (AstroDiary)

> Ground truth for all AstroDiary UI: the daily diary screen, foundation/chart
> screens, calendar, settings, splash/landing, and any new surface.
> Any code that deviates from this spec is WRONG until the spec says otherwise.

> **Token provenance (2026-07-22):** the token blocks below are copied verbatim
> from `tokens/colors.css` and `tokens/typography.css` in the canonical Claude
> Design project **"AstroDiary mobile screens"**
> (`655b21bd-4e83-40b5-80af-99463a4436e6`). `tokens/fonts.css` supplies the
> webfont `@import`. Component patterns are copied from the project's
> `components/core/*.jsx` — those five files are the actual production
> primitives, not approximations of them. If the design project changes, re-pull
> before trusting this document; don't hand-edit tokens from memory — that's
> exactly how silent drift starts (see the equivalent warning in
> `subastop-ds-v3.md`).

---

## What AstroDiary is (so drift is recognizable, not just rule-following)

AstroDiary is a daily astrology diary PWA. Every morning it reads the user's
birth chart against today's sky and writes a short page; the user writes back;
the diary replies next visit. Its differentiator is **calculation accuracy**
(planetary positions ≤0.5° vs JPL Horizons) and the design makes that rigor
legible everywhere — the proof line, console readouts, the phase-true moon.

The visual language mimics an **e-ink panel**: matte paper, pure ink, no
shadows, no glows, no gradients — color exists only as washed, dithered
accents, as if printed by the panel itself. Utilitarian, retro-futuristic,
built for someone who checks it before coffee. Every deviation check below
exists to protect that one sentence.

---

## CSS Custom Properties (Tokens)

Full `:root` blocks, copied verbatim from `tokens/colors.css` and
`tokens/typography.css` — do not hand-restate or rename these.

```css
/* tokens/colors.css */
:root {
  /* base — e-ink light (paper) */
  --paper: #e6e5e0;
  --ink: #1a1a17;
  --gray-1: #55544f;
  --gray-2: #78776f;
  --hairline: #9b9a93;
  --rule-soft: #c8c7c0;
  --frame-border: #b8b7b0;

  /* washed e-ink accents — never used flat, always through dither */
  --eink-red: #c65545;
  --eink-red-hi: #cf6a58;
  --eink-blue: #5a6e8c;
  --eink-blue-hi: #67799a;
  --on-accent: #f2f1ec;
  --on-accent-soft: #f2e4df;

  /* dither / hatch recipes */
  --dither-red: repeating-linear-gradient(45deg, var(--eink-red) 0 2px, var(--eink-red-hi) 2px 3px);
  --dither-blue: repeating-linear-gradient(45deg, var(--eink-blue) 0 2px, var(--eink-blue-hi) 2px 3px);
  --hatch-moon: repeating-linear-gradient(45deg, var(--eink-blue) 0 1.2px, transparent 1.2px 3px);
  --hatch-sealed: repeating-linear-gradient(45deg, rgba(26, 26, 23, 0.12) 0 2px, transparent 2px 5px);
  --tint-today: repeating-linear-gradient(45deg, rgba(198, 85, 69, 0.14) 0 2px, transparent 2px 5px);

  /* semantic aliases */
  --surface-page: var(--paper);
  --text-body: var(--ink);
  --text-secondary: var(--gray-1);
  --text-label: var(--gray-2);
  --border-strong: var(--ink);
  --border-rule: var(--rule-soft);
  --accent-active: var(--eink-red);
}

/* dark — "after sunset" theme: paper and ink swap, accents stay washed */
.theme-dark {
  --paper: #1a1a17;
  --ink: #e6e5e0;
  --gray-1: #c8c7c0;
  --gray-2: #9b9a93;
  --hairline: #4a4a44;
  --rule-soft: #3a3a35;
  --frame-border: #3a3a35;
  --eink-blue: #7d90ad;
  --hatch-sealed: repeating-linear-gradient(45deg, rgba(230, 229, 224, 0.14) 0 2px, transparent 2px 5px);
}

/* film grain — creamy e-ink finish overlay on every screen surface:
   position:relative + ::after { inset:0; background:var(--grain-url) repeat;
   background-size:170px; opacity:var(--grain-opacity); mix-blend-mode:overlay;
   pointer-events:none } */
:root {
  --grain-url: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)'/%3E%3C/svg%3E");
  --grain-opacity: 0.42;
}
```

```css
/* tokens/typography.css */
:root {
  /* families */
  --font-display: 'Bodoni Moda', Didot, 'Bodoni MT', serif; /* hero numerals, readouts, headings */
  --font-reading: Georgia, 'Iowan Old Style', serif;        /* the diary's writing — always warm */
  --font-chrome: 'IBM Plex Mono', Menlo, monospace;         /* micro-chrome only: tabs, stamps, footers, status */

  /* display scale — the date is the hero */
  --display-hero: 400 184px/0.8 var(--font-display);   /* oversized date numeral */
  --display-xl: 400 52px/1 var(--font-display);        /* page titles: July, Settings, 2026 */
  --display-name: 400 56px/1 var(--font-display);      /* "Maya" */

  /* readouts — Bodoni caps, tracked lightly (.08–.1em) */
  --readout-label: 500 12px var(--font-display);       /* PHASE / ILLUM / MOON IN */
  --readout-strong: 700 15px var(--font-display);      /* JULY */
  --readout-section: 700 11px var(--font-display);     /* THE SKY SAYS */

  /* reading — the writing itself */
  --reading-body: 400 16.5px/1.62 var(--font-reading);
  --reading-user: italic 400 13px/1.55 var(--font-reading); /* user ink is always italic */

  /* micro-chrome — mono caps, tracked wide (.14–.24em) */
  --chrome-stamp: 700 10px var(--font-chrome);
  --chrome-cta: 700 11px var(--font-chrome);
  --chrome-tab: 700 8.5px var(--font-chrome);
  --chrome-footnote: 400 9px var(--font-chrome);

  --track-readout: 0.08em;
  --track-chrome: 0.16em;
  --track-wordmark: 0.02em;
}
```

```css
/* tokens/fonts.css */
@import url('https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..900;1,6..96,400..900&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
/* Georgia is a system font — no import needed. */
```

| Token | Value | Role |
|---|---|---|
| `--paper` | `#e6e5e0` (light) / `#1a1a17` (dark) | Page/body background |
| `--ink` | `#1a1a17` (light) / `#e6e5e0` (dark) | Primary text, strong rules |
| `--gray-1` / `--gray-2` | `#55544f` / `#78776f` | Secondary text / labels |
| `--hairline` / `--rule-soft` | `#9b9a93` / `#c8c7c0` | 1px dividers vs. soft row rules |
| `--eink-red` / `--eink-blue` | `#c65545` / `#5a6e8c` | Accent hues — **never used flat**, always via `--dither-*` |
| `--dither-red` / `--dither-blue` | 45° repeating-linear-gradient | The ONLY way accent color appears as a fill |
| `--hatch-moon` | 45° repeating-linear-gradient, blue | Moon disc dark side |
| `--hatch-sealed` | 45° repeating-linear-gradient, ink @ .12 | Locked/sealed content texture |
| `--tint-today` | 45° repeating-linear-gradient, red @ .14 | "Today" row tint — texture, not a flat highlight |
| `--font-display` | Bodoni Moda | Date hero, readouts, page titles |
| `--font-reading` | Georgia | Diary prose; user's own ink is always italic |
| `--font-chrome` | IBM Plex Mono | Tabs, stamps, footers, status — micro-chrome ONLY |

`.theme-dark` is a **class toggle that remaps the same tokens** — never a
separate hardcoded dark stylesheet. Accent hues stay identical between themes
except `--eink-blue` (`#5a6e8c` → `#7d90ad`) and `--hatch-sealed`'s opacity base
(ink-tinted → paper-tinted), both intentional.

---

## Component Patterns — DO NOT DEVIATE

Each pattern below is transcribed from the project's actual
`components/core/*.jsx`. If the target codebase is React, import these
components directly — don't hand-recreate them. If the target is plain
HTML/CSS (most UI builders), use the CSS below verbatim.

### 1. StampTag (`TODAY`, `SO FAR`, etc. — one per screen)

**CORRECT:**
```html
<span class="stamp-tag stamp-red">TODAY</span>
```
```css
.stamp-tag {
  padding: 4px 9px;
  font: var(--chrome-stamp);            /* 700 10px IBM Plex Mono */
  letter-spacing: var(--track-chrome);  /* .16em */
  display: inline-block;
}
.stamp-red { background: var(--dither-red); color: var(--on-accent); }
.stamp-ink { background: var(--ink); color: var(--paper); }
```
**WRONG:**
- Flat `background: var(--eink-red)` or a hardcoded hex instead of `var(--dither-red)`
- Sans-serif or body font instead of `var(--chrome-stamp)` (IBM Plex Mono)
- More than one stamp visible on a single screen

---

### 2. InkButton (full-width bar CTA)

**CORRECT:**
```html
<button class="ink-button ink-button--red">
  <span>WRITE BACK →</span>
  <span class="ink-button__trailing">the diary replies tomorrow</span>
</button>
```
```css
.ink-button {
  display: flex; align-items: center; justify-content: space-between;
  width: 100%; border: none; cursor: pointer; padding: 14px 16px;
  font: var(--chrome-cta); letter-spacing: 0.18em;
}
.ink-button--red { background: var(--dither-red); color: var(--on-accent); }
.ink-button--ink { background: var(--ink); color: var(--paper); }
.ink-button__trailing {
  font: italic 400 13px var(--font-reading);
  color: var(--on-accent-soft); letter-spacing: 0; text-transform: none;
}
```
**WRONG:**
- `border-radius` on the button (it's a square bar)
- `box-shadow` or hover `scale()` — spec allows opacity/invert only
- Trailing microcopy set in the chrome font instead of italic Georgia
- Two red (`tone="red"`) CTAs on one screen — red is reserved for the screen's
  single primary action; secondary actions use the ink tone

---

### 3. ConsoleReadout (instrument-panel label/value row)

**CORRECT:**
```html
<div class="console-readout">
  <div class="readout-cell"><span class="readout-label">PHASE</span>WANING GIBBOUS</div>
  <div class="readout-divider"></div>
  <div class="readout-cell"><span class="readout-label">ILLUM</span>71%</div>
  <div class="readout-divider"></div>
  <div class="readout-cell" style="text-align:right"><span class="readout-label">MOON IN</span>TAURUS</div>
</div>
```
```css
.console-readout {
  display: flex;
  border-top: 1.5px solid var(--ink);
  border-bottom: 1px solid var(--hairline);
  font: var(--readout-label); letter-spacing: var(--track-readout); color: var(--ink);
}
.readout-cell { flex: 1; padding: 10px 0; }
.readout-divider { width: 1px; background: var(--hairline); }
.readout-label { display: block; color: var(--gray-2); margin-bottom: 4px; }
```
**WRONG:**
- `border-top`/`border-bottom` weights swapped (top must be the heavier 1.5px
  ink rule; bottom the 1px hairline) — this asymmetry is intentional, it reads
  as "opening" a console
- Any divider other than a 1px `--hairline` fill
- Values not in `var(--font-display)` (Bodoni)

---

### 4. MoonDisc (phase-true moon — the one luminous object per screen)

**CORRECT:**
```html
<div class="moon-disc" style="width:40px;height:40px">
  <div class="moon-disc__lit" style="margin-left: 26px"></div>
</div>
```
```css
.moon-disc {
  border-radius: 50%;
  border: 1.5px solid var(--ink);
  background: var(--hatch-moon);   /* dark/unlit side */
  overflow: hidden;
}
.moon-disc__lit {
  width: 100%; height: 100%; border-radius: 50%;
  background: var(--paper);        /* lit side, offset by phase */
}
```
The lit-disc's `margin-left` is computed as `size * (phase * 0.92)` — the
offset must track the real phase value, never a fixed decorative crescent.

**WRONG:**
- A static/decorative crescent icon instead of a phase-computed offset
- Solid fill instead of `var(--hatch-moon)` on the dark side
- More than one moon disc, or any other starfield/celestial wash on the same
  screen — "exactly one luminous celestial object per screen"

---

### 5. ScopeTabs (YEAR / MONTH / WEEK / DAY switcher)

**CORRECT:**
```html
<div class="scope-tabs">
  <button class="scope-tab">YEAR</button>
  <button class="scope-tab scope-tab--active">MONTH</button>
  <button class="scope-tab">WEEK</button>
  <button class="scope-tab">DAY</button>
</div>
```
```css
.scope-tabs { display: flex; gap: 20px; font: 700 9px var(--font-chrome); letter-spacing: var(--track-chrome); }
.scope-tab { background: none; border: none; padding: 0; cursor: pointer; font: inherit; letter-spacing: inherit; color: var(--gray-2); }
.scope-tab--active {
  color: var(--accent-active);
  text-decoration: underline;
  text-underline-offset: 4px;
}
```
**WRONG:**
- Active state shown as a filled pill/background instead of the red-dithered
  underline
- Underline without `text-underline-offset: 4px`
- A 5th tab, or tabs outside `YEAR / MONTH / WEEK / DAY` for this switcher

---

### 6. The bottom tab bar (screen-level chrome, not a `components/core` file but load-bearing)

**CORRECT:** exactly 4 mono-caps tabs — `TODAY · FOUNDATION · CALENDAR · SETTINGS`
— `font: var(--chrome-tab)` (700 8.5px IBM Plex Mono), active tab in
`var(--accent-active)`.

**WRONG:** any other tab count, label set, or font.

---

### 7. The proof line (required on every full screen surface)

**CORRECT:**
```html
<div class="proof-line">POSITIONS Δ ≤ 0.5° · CHECKED AGAINST JPL HORIZONS</div>
```
```css
.proof-line { font: var(--chrome-footnote); letter-spacing: var(--track-chrome); color: var(--gray-2); }
```
**WRONG:** omitted, reworded, or rendered in a non-chrome font. This line is
the brand's one factual claim and must be verbatim.

---

## Visual Foundations (screen-level rules, not tied to one component)

- **No shadows. No glows. No gradients** other than the 45° dither/hatch
  textures — those are textures, not tone gradients. No transparency/blur.
- **Corners:** nothing above 12px except device frames (36px) and the app icon
  (squircle-ish 19/13/8px by size). Everything else is square.
- **Active states:** red-dithered underline for text/tab selection; buttons are
  solid dithered-red or solid ink bars. Hover/press: opacity or invert only —
  never `scale`, never anything faster than "a page-turn".
- **Layout:** 390px mobile frames, 26px side padding, flex/grid with `gap`
  (not manually-tuned margins).
- **Iconography:** no icon font, no SVG icon set. Only unicode astronomical
  glyphs as text (☉ ☽ ↑ ☿ ♀ ♂ ♃ ♄ ♅ ♆ ♇ ℞ ✦) and CSS-drawn primitives (moon
  disc, crescent-page icon, dither/hatch swatches). No emoji, ever.
- **Voice (when the enforcement touches copy):** direct, warm, concrete,
  unmystical; states what a thing IS in the first sentence; max one metaphor
  per reading; labels are ALL-CAPS and terse (`PHASE`, `ILLUM`, `MOON IN`,
  `THE SKY SAYS`); the user's own writing is always italic Georgia, gray-1.

## Body Background

```css
body { background: var(--paper); color: var(--ink); }
/* .theme-dark on <body> or a root wrapper — never a second hardcoded stylesheet */
```

---

## Enforcement Checklist

- [ ] All colors reference CSS custom properties — no hardcoded hex/rgb outside `:root`
- [ ] Every accent fill uses `var(--dither-red)` / `var(--dither-blue)` — zero flat accent fills
- [ ] Zero `box-shadow`, glow, blur, or non-dither gradients anywhere
- [ ] Dark mode is `.theme-dark` token remap — not a second hardcoded stylesheet
- [ ] Proof line `POSITIONS Δ ≤ 0.5° · CHECKED AGAINST JPL HORIZONS` present on every full screen
- [ ] Fonts: chrome → `var(--font-chrome)`, display/readouts → `var(--font-display)`, reading → `var(--font-reading)`
- [ ] User's own writing is italic Georgia (`--reading-user`)
- [ ] `border-radius` ≤ 12px except device frame (36px) / app icon
- [ ] Bottom tab bar: exactly TODAY · FOUNDATION · CALENDAR · SETTINGS, mono caps
- [ ] Active tab/state: red-dithered underline, `text-underline-offset: 4px` — never a filled pill
- [ ] Exactly one phase-true MoonDisc per screen, offset computed from real phase — no decorative crescents, no starfields
- [ ] No icon fonts/SVG icon sets, no emoji — unicode glyphs and CSS-drawn primitives only
- [ ] Max one metaphor per reading/copy block
- [ ] Motion: opacity/invert only, never `scale`, never faster than a page-turn
