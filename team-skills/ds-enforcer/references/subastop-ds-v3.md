# Subastop Design System v3 — Canonical Reference

> Ground truth for all Subastop ecosystem UIs: dashboards, cockpits, landing pages, evaluators.
> Any code that deviates from this spec is WRONG until the spec says otherwise.

---

## CSS Custom Properties (Tokens)

```css
/* Colors */
--ink:       #08152F;   /* page background */
--navy:      #0D1F4E;   /* secondary surface */
--amber:     #F59E0B;   /* accent / CTA / numbers */
--green:     #10B981;   /* success / positive */
--error:     #DC2626;   /* danger / rejection */
--blue:      #1A56DB;   /* primary action */
--line-dk:   rgba(255,255,255,.08); /* subtle dividers */
--cream:     #F4F2EC;   /* text base */

/* Typography stacks */
--disp:  'Outfit', sans-serif;       /* display / headings / hero numbers */
--sans:  'Inter', sans-serif;        /* body / UI copy */
--mono:  'IBM Plex Mono', monospace; /* labels / metadata / code */
```

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
