# Subastop Design System v3 — Canonical Reference

> Ground truth for all Subastop ecosystem UIs: dashboards, cockpits, landing pages, evaluators.
> Any code that deviates from this spec is WRONG until the spec says otherwise.

> **Token provenance (2026-07-03):** the token block below was verified byte-for-byte against
> `subastop-system.css` (`:root`) in the canonical **Subastop DS** project. Two errors were found
> and fixed in this pass: `--line-dk` was recorded as `rgba(255,255,255,.08)` — the real value is
> `.16`; and a token named `--cream` did not exist anywhere in the source — the real token at
> `#F4F2EC` is named `--paper`. Both were silent drift from an earlier hand-copy of this reference,
> not intentional divergence. If you find another mismatch, the CSS file wins, not this document.
>
> **Scope limit — read before trusting the component patterns below:** only the *tokens* section
> was cross-checked against the canonical DS project. The dashboard-specific component patterns
> further down (`.section-header`, `.glass-cell`, `.fnode`, `.sig`) do **not** appear anywhere in
> the canonical Subastop DS project — that project covers the public marketing site and a
> React starting-point library (Button, StatusBadge, StatCard, GlassPanel), not internal
> dashboards/cockpits. Those patterns presumably originate from an actual dashboard codebase
> (AVT / CarMatch / VMC) that was not available to check against. Treat the tokens below as
> verified; treat the component patterns as unverified until checked against a real dashboard repo.

---

## CSS Custom Properties (Tokens)

Full `:root` block, copied verbatim from `subastop-system.css` — do not hand-restate or rename
these; hand-copies are exactly how the `--cream` / `--line-dk` drift happened.

```css
:root{
  --ink:#08152F; --navy:#0D1F4E; --navy-700:#162B6A;
  --blue:#1A56DB; --blue-700:#1D4ED8; --amber:#F59E0B;
  --paper:#F4F2EC; --paper-2:#EDEAE1; --white:#fff;
  --line:rgba(8,21,47,.14); --line-dk:rgba(255,255,255,.16); --muted:#5B6473;
  --green:#10B981; --error:#DC2626;
  --disp:'Outfit',sans-serif; --sans:'Inter',sans-serif; --mono:'IBM Plex Mono',monospace;
  --rglass:18px;
}
```

| Token | Value | Role | Used in dashboard scope? |
|---|---|---|---|
| `--ink` | `#08152F` | Page/body background | Yes — always the body bg |
| `--navy` | `#0D1F4E` | Secondary surface | Yes |
| `--navy-700` | `#162B6A` | Navy step (dark cards) | Yes, where used |
| `--blue` | `#1A56DB` | Primary action | Yes |
| `--blue-700` | `#1D4ED8` | Blue hover | Yes |
| `--amber` | `#F59E0B` | Accent / CTA / numbers | Yes |
| `--paper` | `#F4F2EC` | Warm off-white, light-section bg | **No** — dashboards never use a light bg |
| `--paper-2` | `#EDEAE1` | Paper hover fill | **No** — marketing-site only |
| `--white` | `#fff` | Card surface | Rarely |
| `--line` | `rgba(8,21,47,.14)` | Hairline on light | **No** — pairs with `--paper`, not used on dark |
| `--line-dk` | `rgba(255,255,255,.16)` | Hairline on dark | Yes — the dashboard default divider |
| `--muted` | `#5B6473` | Secondary text on light | **No** — light-surface only |
| `--green` | `#10B981` | Success / positive | Yes |
| `--error` | `#DC2626` | Danger / rejection | Yes |
| `--disp` | `'Outfit', sans-serif` | Display / hero numbers | Yes |
| `--sans` | `'Inter', sans-serif` | Body / UI copy | Yes |
| `--mono` | `'IBM Plex Mono', monospace` | Labels / metadata / code | Yes |
| `--rglass` | `18px` | Glass panel radius | Yes |

`--paper`, `--paper-2`, `--muted`, and `--line` exist in the canonical token set but belong to the
marketing site's light "paper" sections — flag any dashboard/cockpit code that references them,
since dashboards are dark-only per the Enforcement Checklist below.

---

## Component Patterns — DO NOT DEVIATE

### 1. Section Headers

**CORRECT:**
```html
<div class="section-header">
  <span class="section-title">
    <span class="s-no">01</span> — Section Name
  </span>
  <div class="section-rule"></div>
  <button class="collapse-btn" onclick="toggleSection(this)">▼</button>
</div>
```

**Required CSS:**
```css
.section-title {
  font-family: var(--mono); font-size: .72rem; font-weight: 500;
  letter-spacing: .14em; text-transform: uppercase;
  color: rgba(244,242,236,.55);
  display: flex; align-items: center;
  white-space: nowrap; flex: none;
}
.s-no { color: var(--amber); font-weight: 600; font-family: var(--mono);
        font-size: .72rem; letter-spacing: .14em; margin-right: .3em; }
.section-rule { flex: 1; height: 1px; background: var(--line-dk); }
```

**WRONG — never do these:**
- `<div class="section-header" style="border-bottom: ...">` — no border-bottom
- `<h2>01. Section Name</h2>` — wrong element
- Section number without `.s-no` wrapper
- Missing `<div class="section-rule"></div>`
- ` — ` separator missing between number and title

---

### 2. GlassPanel (`.glass-cell`)

**CORRECT CSS:**
```css
.glass-cell {
  position: relative;
  background: linear-gradient(140deg, rgba(255,255,255,.16) 0%, rgba(255,255,255,.05) 100%);
  -webkit-backdrop-filter: blur(26px) saturate(185%) brightness(1.06);
  backdrop-filter: blur(26px) saturate(185%) brightness(1.06);
  border: 1px solid rgba(255,255,255,.22);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.5),
              inset 0 -1px 0 rgba(0,0,0,.14),
              0 20px 50px rgba(8,21,47,.28);
  border-radius: 18px;
}
.glass-cell::before {
  content: ""; position: absolute; top: 0; left: 0; right: 0; height: 42%;
  background: linear-gradient(180deg, rgba(255,255,255,.16), transparent);
  pointer-events: none; border-radius: 18px 18px 0 0;
}
.glass-cell > * { position: relative; z-index: 1; }
```

**WRONG — common deviations:**
- `rgba(255,255,255,.07)` — too transparent, panel invisible on dark bg
- `backdrop-filter: blur(12px)` — wrong blur value
- Missing `saturate(185%) brightness(1.06)` — kills the glass effect
- Missing `::before` highlight — panel looks flat
- `border-radius: 8px` — wrong radius (should be 18px)

---

### 3. Funnel / Flow Diagrams

**CORRECT: `.fnode` flex layout**
```html
<div class="fnode-cols" style="min-height:320px;">
  <div class="fnode-col">
    <div class="fnode-col-label">Column Label</div>
    <div class="fnode-stack">
      <div class="fnode f-blue" style="flex:4832;">
        <span class="fn-label">Node Label</span>
        <span class="fn-val">4,832</span>
        <span class="fn-pct">100%</span>
      </div>
    </div>
  </div>
  <div class="fnode-arrow">›</div>
</div>
```

**`.fnode` color variants:**
- `.f-blue` — published / primary
- `.f-blue2` — secondary blue
- `.f-mute` — neutral / empty / no-deal
- `.f-green` — sold / above reserve / accepted
- `.f-green2` — secondary green
- `.f-amber` — below reserve / warning
- `.f-red` — breach / incumplimiento
- `.f-red2` — rejection / secondary red

**WRONG: SVG funnels**
```html
<!-- NEVER for flow diagrams -->
<svg id="funnel-svg" viewBox="0 0 900 200">...</svg>
```
SVG funnels are replaced by `.fnode` flex layout. Never create new SVG funnels.

**`.fnode-arrow` CSS:**
```css
.fnode-arrow {
  flex: none; width: 22px; align-self: stretch;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  color: rgba(244,242,236,.18); font-size: 20px;
}
```

---

### 4. Signal Callouts (`.sig`)

**CORRECT:**
```html
<div class="sig">Signal text here.</div>
```
```css
.sig {
  background: rgba(245,158,11,.06);
  border-left: 2px solid var(--amber);
  padding: 9px 13px;
  font-family: var(--mono);
  font-size: .67rem;
  letter-spacing: .02em;
  color: rgba(244,242,236,.72);
  line-height: 1.55;
  border-radius: 0 6px 6px 0;
}
```

**WRONG (deprecated):**
- `.cell-signal` with `◆` prefix
- `.funnel-signal`

---

### 5. Typography Hierarchy

| Role | Font | Weight | Size |
|---|---|---|---|
| Hero numbers / KPI | `var(--disp)` | 800 | `clamp(1.6rem, 3vw, 2.4rem)` |
| Section titles | `var(--mono)` | 500 | `.72rem` |
| Column labels | `var(--mono)` | 400 | `.58rem` |
| Body copy | `var(--sans)` | 400 | `.875rem` |
| Signal text | `var(--mono)` | 400 | `.67rem` |
| Button labels | `var(--mono)` | 600 | `.68rem` |

---

### 6. Ticker Bar

```html
<div class="ticker-wrap">
  <div class="ticker-track">
    <span>ITEM</span><span class="tk-sep">·</span>
    <!-- duplicate for seamless loop -->
    <span>ITEM</span><span class="tk-sep">·</span>
  </div>
</div>
```
```css
.ticker-wrap {
  overflow: hidden;
  -webkit-mask-image: linear-gradient(90deg, transparent, #fff 8%, #fff 92%, transparent);
  mask-image: linear-gradient(90deg, transparent, #fff 8%, #fff 92%, transparent);
}
.ticker-track { display: flex; gap: 28px; animation: tkmove 28s linear infinite; white-space: nowrap; }
@keyframes tkmove { from { transform: translateX(0); } to { transform: translateX(-50%); } }
```

---

## Body Background

```css
body { background: var(--ink); color: var(--cream); }
```
Never use a light background for any Subastop dashboard or cockpit.

---

## Enforcement Checklist

- [ ] All colors reference CSS custom properties — no hardcoded hex/rgb outside `:root`
- [ ] Section headers: amber `.s-no` + ` — ` + text + `.section-rule` div
- [ ] Funnels/flows: `.fnode` flex layout — zero SVG funnels
- [ ] GlassPanel: `rgba(255,255,255,.16)` gradient start + `saturate(185%) brightness(1.06)` + `::before`
- [ ] Signals: `.sig` class — not `.cell-signal`, not `.funnel-signal`
- [ ] `.fnode-arrow`: `align-self: stretch` + `justify-content: center`
- [ ] Typography: section labels → `--mono`, heroes → `--disp`, body → `--sans`
- [ ] Body background: `var(--ink)` (#08152F) — never light
