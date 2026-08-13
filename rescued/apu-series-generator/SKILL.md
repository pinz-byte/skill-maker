---
name: apu-series-generator
description: Generate APU production series lines and stamp them onto badge artwork for laser engraving. Use whenever the user wants to set, change, or produce a series/edition line in the format "YEAR SERIES NNN - N ##" (e.g. "2026 SERIES 002 - N 01"), assign an asset code, or stamp a series number onto an APU badge for a coaster/vaso engrave. Trigger on "series generator", "new series", "set the series", "change the series line", "series 002", "edition number", "stamp the series", "generate the series code", or any request that names a year + series + unit number for an APU production piece. Also fire when the user confirms a series and expects the engraving-ready file back.
---

# APU Series Generator

Produces the canonical APU production series line, an asset code, and (when a badge image is supplied) stamps the line onto the badge's bottom arc and exports laser-engraving-ready files.

## Format (locked)

```
DISPLAY:    {YEAR} SERIES {SSS} - {N} {NN}
EXAMPLE:    2026 SERIES 002 - N 01

ASSET CODE: APU-{YEAR}-S{SSS}-{N}{NN}
EXAMPLE:    APU-2026-S002-N01
```

- `YEAR` — 4-digit year, as given.
- `SSS` — series number, zero-padded to 3 digits (`2` → `002`).
- `NN` — unit/edition number, zero-padded to 2 digits (`1` → `01`).
- `N` — literal label (default `N`, for "Número"). Override with `--n-label` if a different prefix is wanted.

Padding is configurable (`--series-pad`, `--number-pad`) but **defaults are the production standard — do not change without explicit instruction.**

## Workflow

When the user confirms a series (e.g. "2026, series 2, number 1"):

1. Run the generator in **string mode** to produce and show the display line + asset code:
   ```bash
   python3 scripts/series.py --year 2026 --series 2 --number 1
   ```
2. If a badge image is in play (the user wants the engraving file), run **stamp mode**:
   ```bash
   python3 scripts/series.py --year 2026 --series 2 --number 1 \
       --badge <path-to-clean-badge.png> --out <outdir>
   ```
   This erases the existing bottom-arc series text and renders the new line on the same arc, then exports:
   - `{ASSET}_BW.png` — clean 1-bit raster (primary engrave file)
   - `{ASSET}_GRAY.png` — grayscale (edge-smoothed alternative)
   - `{ASSET}_100mm.svg` — vector trace, scaled to 100 mm, aspect preserved

3. Present the files. State the display line and asset code back to the user for confirmation.

## Badge calibration (important)

The arc geometry defaults are tuned for the **RT004 "Ritual" circular badge** (1254×1254 px, center 626/627). A different badge has a different center, radius, and text-band position. Before stamping a new badge layout, calibrate:

- `--cx --cy` — circle center in pixels (find via the border-ring extents).
- `--r-base` — baseline radius where the text sits.
- `--band-rmin --band-rmax --band-amin --band-amax` — polar mask that erases the *old* text. `r` in px from center; `a` in degrees (0 = right, 90 = bottom, 180 = left). The defaults erase a bottom-arc band spanning ~51°–129°.
- `--font-size --letter-spacing` — tune so the line fills the arc without curling the end characters too steeply.

**Calibration loop:** stamp once, crop the bottom arc, view it, adjust the band/radius, repeat. Verify the mask removes the old glyphs without clipping the inner ornaments or the outer border ring.

## Constraints & gotchas

- **Font:** defaults to FreeSerif (Times-like inscriptional serif). It approximates the APU badge caps; it is not an exact match to the original lettering. If exact match matters, supply the real typeface via `--font`.
- **Text length:** longer strings span a wider arc and rotate the end characters steeply. If "N 01" → "N 12+" or the year/series grows, re-check the end-character angle and reduce `--font-size` ~10% if it curls.
- **`N`/`Nº`:** the default label is a plain `N`. For a superscript ordinal (`Nº`), that's a glyph change, not a parameter — flag it and edit the text directly.
- **Dependencies:** Pillow (raster + text), potrace (SVG trace). Install: `apt-get install -y potrace && pip install --break-system-packages pillow`.
- **Resolution floor:** at 100 mm on pine, small arc text is near the CO2 resolution limit; fine serifs may thicken. Bump trace/raster DPI before adding power if the test engrave muddies.

## Quick reference

| Need | Command |
|------|---------|
| String + code only | `series.py --year Y --series S --number N` |
| Stamp + export | add `--badge IMG --out DIR` |
| Different unit label | add `--n-label Nº` |
| New badge layout | calibrate `--cx --cy --r-base --band-*` |
| Different size | add `--target-mm 90` |
