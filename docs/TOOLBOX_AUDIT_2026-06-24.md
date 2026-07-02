# Toolbox Audit — 2026-06-24

Scope: the 36 skills in the SKILL MAKER repo (source of truth for the `lfp-skills`
marketplace). Audited against the project's own invariants: grouped/propagable,
description <=1024, ASCII-clean, no reserved word "claude", trigger collisions.

**Headline: the build is clean. The problems are architecture and quality, not breakage.**
No ungrouped skills, no missing dirs, no over-limit descriptions, no reserved names. The
propagation guard that failed in the past (2026-06-04) is holding. So this audit is about
what will *rot* next, ranked by leverage.

---

## Clean bill (verified, no action)
- **Propagation:** 36 on-disk skills, 36 grouped slots, 0 ungrouped, 0 referenced-but-missing.
- **Hard limits:** 0 descriptions over 1024 chars; 0 names containing "claude"; every `name:`
  field matches its directory.
- Plugins: 3 (lfp-thinkers 6, lfp-core 25, lfp-apex 5).

---

## F1 — `lfp-core` is a 25-skill mega-plugin (highest-leverage issue)
Everything that isn't a thinker or an apex skill lands in `lfp-core` — 25 of 36 skills. The
whole point of splitting into plugins (per CLAUDE.md: "scope apex to trading projects only")
is *scoped install*. A 25-skill core defeats that: installing core drags comms, git, QA, meta,
hygiene, and project tooling into every workspace whether it needs them or not.
**Action:** split `lfp-core` along install-intent lines, e.g.
- `lfp-comms` — agent-bridge, inbox-triage
- `lfp-build` — git-ops, machine-bridge, project-migrate, self-audit
- `lfp-meta` — projectmd-auditor, projectmd-optimizer, meta-no-bare-names, skill-miner
- `lfp-hygiene` — space-steward, workspace-plugin-audit, session-rules
- `lfp-continuity` — reentry, continuity-seed, soul-builder
- keep the rest in a lean core.
This is a `GROUPS` edit + one publish. No skill content changes.

## F2 — the council cluster has probable duplication (needs a consolidation call)
Five council skills with overlapping jobs:
- `council-call` and `council-debate` **both do a live single-ticker 7-voice audit** — different
  triggers ("call the council" vs "/debate <ticker>"), likely the same underlying work. Probable
  functional duplicate → collapse to one, or make the boundary explicit.
- `council-global` claims `/council` + bare `"council"` (read-only cached show). An
  `anthropic-skills:council` skill in a *different* marketplace does the same read-only show on
  the same `/council` trigger → **cross-marketplace duplicate** (same failure class as the
  brief-bridge ownership question). Decide which marketplace owns `/council`.
- `apex-ultra-council` is clean — it disclaims bare "council" and owns "apex ultra".
**Action:** one decision — collapse call/debate, and pick the owner of `/council`.

## F3 — two descriptions are one edit away from silent failure
`logic-thinker` = 1018/1024, `loop-breaker` = 1016/1024. Any added trigger word crosses 1024
and Cowork drops the description silently. **Action:** trim ~80 chars of slack from each now,
before the next edit does it accidentally.

## F4 — non-ASCII in 16/36 skills (mostly cosmetic, some structural)
The build's `strip_non_ascii()` removes these at package time; source keeps them.
- **Cosmetic** (em-dash only, ~12 skills): prose reads "word  word" post-strip. Low priority.
- **Structural** (fix these): `reentry` (box-drawing ╔╗╚╝║─═ in the hutch layout), `self-audit`
  (✓ ⚠ 🔧 status glyphs), `session-rules` (─ rules), `agent-bridge` (• → ↔ in message
  templates). Post-strip these mangle the skill's *output format*, not just prose.
**Action:** normalize the structural four to ASCII equivalents (`+`/`-`/`|` boxes, `[x]`/`[!]`
markers, `->`). Optionally sweep the em-dashes in a single pass.

## F5 — trigger overlaps (mostly fine; one to watch)
- `"you've got mail"` (agent-bridge + inbox-triage): **not a collision** — inbox-triage quotes
  it to *disclaim* it ("to read/act, invoke agent-bridge"). Partition is clean.
- `"commit this"` / `"git status"` (git-ops + meta-no-bare-names): **intended** gate+actor —
  meta-no-bare-names is a pre-commit gate meant to fire alongside git-ops. Risk: nothing
  *enforces* the gate runs first; it relies on both firing and the agent sequencing them.
  Acceptable, but note it.
- bare `"council"`: contested inside the cluster — resolves once F2 is decided.

---

## Recommended order
1. **F3** (trim 2 descriptions) — 5 min, removes a silent-failure landmine.
2. **F2** (council consolidation decision) — needs your call, not code.
3. **F1** (split lfp-core) — GROUPS edit + publish, biggest structural win.
4. **F4** (normalize the structural 4) — quality.
5. F5 — monitor; no action unless the git gate misfires.
