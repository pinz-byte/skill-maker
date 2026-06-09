# GSTACK SYNTHESIS — What to Steal, What to Build, What For

**Date:** 2026-06-09
**Author:** Architect (critical-thinker mode) for POPs / LFP ecosystem
**Source:** Full structural audit of `garrytan/gstack` (3 stars, 2 contributors — one
person's opinionated config, mined for ideas, not venerated as a standard)

---

## 0. The one finding that reframes everything

gstack is not 31 clever commands. Strip the surface and **every quality mechanism in
the repo is the same primitive: an independent verifier with fresh context that cannot
see the generator's reasoning, scored on a numeric gate, with anti-anchoring discipline
and a max-iteration cap.** It repeats five times:

| Skill | The verifier |
|---|---|
| `/office-hours` (YC partner) | adversarial Spec Review Loop — independent subagent scores the design doc 1-10 on 5 axes, max 3 iterations, BEFORE the doc is shown to you |
| `/cso` (security) | Parallel Finding Verification — "fresh context, cannot see the initial scan's reasoning, only the finding itself"; anti-anchoring (line number ONLY); discard < 8/10 |
| `/spec` | codex quality gate — "a second AI model scores the spec 0-10 for executability"; fail-closed secret redaction PRECEDES dispatch |
| `/codex` | cross-model review — "two doctors, same patient"; Claude review never seen by Codex |
| `benchmark-models` | LLM judge as independent tiebreaker, 0-10 |

This is gstack's actual answer to the question I raised earlier — *"how do you know an
artifact is good when there's no success signal?"* The answer is not a success signal.
It is **blind independent re-judgment.** A second evaluator with no stake, no visibility
into the reasoning that produced the artifact, scoring against a fixed rubric.

**Your entire gate stack is the inferior version of this.** `self-audit`, `pre-deliver`,
`work-retrospective`, `apex-builder-gate` — all SELF-verification: same model, same
context, same reasoning that produced the work now grading the work. Self-review inherits
the author's blind spots by construction. That is the single highest-leverage structural
upgrade available to you, and it is the through-line of the whole repo.

---

## 1. The CEO skill vs your IB — the blind spot it exposes

gstack has two "CEO" skills: `/plan-ceo-review` (CEO/founder-mode *plan* review with three
scope modes — expansion / hold / reduction) and `/office-hours` (YC-partner demand
interrogation). For the IB blind-spot argument the one that matters is `/office-hours`,
because **it is the direct analog of your IB's demand axis — and where they diverge is
exactly your weakness.** `/plan-ceo-review` is a different and separately useful thing,
reviewed below.

**`/office-hours` mechanics (verbatim):** hard gate — output is ONLY a design doc, no
code. Six Forcing Questions, asked ONE AT A TIME, stage-routed (pre-product / has-users /
paying / infra):
1. **Demand Reality** — "strongest evidence someone would be genuinely upset if it
   disappeared tomorrow — not 'interested,' not a waitlist signup"
2. **Status Quo** — "what are users doing right now to solve this, even badly? what does
   the workaround cost them?"
3. **Desperate Specificity** — "name the actual human. Their title. What gets them
   promoted. What gets them fired."
4. **Narrowest Wedge** — "smallest version someone would pay real money for THIS WEEK"
5. **Observation & Surprise** — "have you watched someone use this without helping?"
6. **Future-Fit** — "in 3 years does this become more essential or less?"

Operating principles: *"Specificity is the only currency. Interest is not demand. Watch,
don't demo. The status quo is your real competitor. Narrow beats wide, early."*

**Your IB:** Phase 1 Intention Matrix (necessity -> supposition -> challenges -> hypothesis)
-> Phase 2 Purpose Pyramid (5 tasks -> 4 objectives -> 2 responsibilities -> purpose).

**The dot:** office-hours and IB are the same archetype — a structured pre-build
interrogation that converts ambiguity into a locked artifact. But they interrogate
different axes:

- **IB interrogates STRUCTURE.** It architects execution bottom-up. It is a machine for
  turning an intention into a coherent pyramid.
- **office-hours interrogates DEMAND.** Is this even worth building? Who is the human?
  What is the wedge?

**The blind spot:** IB's "necessity" and "supposition" are *self-asserted by you* and
never pressure-tested against demand reality. IB will happily architect a flawless pyramid
for something nobody wants — and for a platform-gravity builder running many interlocking
ventures, that is precisely the dominant failure mode: beautiful systems for unvalidated
demand. **The Six Forcing Questions are the demand-reality stress test your IB structurally
lacks.** This is uncomfortable by design — which, by your own doctrine (discomfort as proof
of growth), is the signal it is load-bearing.

**The build is not "adopt office-hours."** It is: **prepend a Demand-Reality Gate as IB
Phase 0.** Six questions, one at a time, before the Intention Matrix runs. If the demand
evidence is "interest" not "demand," IB refuses to proceed to architecture. That single
change closes the gap between your strongest skill and its weakest assumption.

Two mechanical steals from office-hours, independent of the above:
- **The adversarial Spec Review Loop** (the keystone from Section 0 — IB artifacts scored
  blind before you see them).
- **"The Assignment"** — every office-hours doc ends with one concrete real-world action,
  "not 'go build it.'" IB ends at architecture; it never forces a non-building next step.

---

## 2. Build map — what to build, what for (purpose-driven)

Ranked by leverage x feasibility. **Tier 1 is the keystone; everything else is gated
behind proof it fires.** This ordering is deliberate sprawl-defense: you have 60+ skills
and 5 meta-skills already governing them. The discipline is one primitive, verified, then
compose.

### TIER 1 — Build first

**A. The Independent Verifier primitive** (`verify` / a reusable sub-skill)
- *What:* any skill passes it an artifact + a rubric. It spawns a subagent with FRESH
  context that cannot see the author's reasoning, scores 0-10 against the rubric, returns
  PASS / specific-ambiguities, max 3 iterations, fail-closed on detected secrets.
- *What for:* upgrade `self-audit` / `pre-deliver` from self-review to independent review
  across the WHOLE ecosystem — IB artifacts, builder prompts, APEX council verdicts, copy
  decks, dashboard specs. This is the success-signal substitute and the gstack through-line
  in one buildable unit.
- *Feasibility:* high. You already spawn subagents. Anti-anchoring + numeric gate +
  iteration cap is ~a page of skill prose.

**B. Demand-Reality Gate — IB Phase 0**
- *What:* the Six Forcing Questions, one at a time, before the Intention Matrix. Refuses to
  architect on "interest."
- *What for:* stop building structurally perfect ventures for unvalidated demand. Directly
  fixes IB's blind spot.
- *Feasibility:* high. It is prose + AskUserQuestion routing bolted to the front of an
  existing skill.

### TIER 2 — Build next (after Tier 1 fires in real use)

**C. The Surface Compiler** (`SurfaceConfig` for Cowork vs Claude-Chat)
- *What:* gstack's declarative `HostConfig` pattern. One skill source compiles to N surfaces
  via typed transforms (frontmatter allowlist/denylist, `descriptionLimit` behavior, name
  rewrites, path rewrites, ASCII strip).
- *What for:* replace your tribal-knowledge invariants (strip non-ASCII, desc <=1024, no
  "claude" in name, GROUP assignment) with a typed compile target. Author once, compile to
  every surface. You have MORE surfaces than gstack (Cowork M1/M2/M3 + Chat) and a worse
  failure mode (silent rejection).
- *GATE:* verify first that Chat and Cowork frontmatter rules actually differ. If they are
  near-identical, this is ceremony, not leverage.

**D. Taste-Profile primitive** (decaying preference memory)
- *What:* gstack's `taste-profile.json` — per-dimension approved/rejected entries, confidence
  decays 5%/week at READ time (file only grows on change), top-3 signals bias generation,
  conflicts flagged.
- *What for:* generalize beyond design. Brand voice for `copy-deck` (learn what POPs approves
  in copy), design consistency across Subastop products, even APEX setup-selection (learn
  which trade setups you take vs pass). A clean preference-memory primitive your manual
  capsule system lacks — and one that fits your "experience as data" instinct natively.

**E. Spec -> Worktree execution** (`--execute` automation)
- *What:* gstack's `/spec --execute` spawns a fresh git worktree on a pinned SHA and runs
  `claude -p` headless with the spec piped in; `/ship` closes the loop. Fail-closed secret
  redaction before dispatch.
- *What for:* close the gap your IB pipeline stops short of — the manual IB -> builder-session
  handoff. Combined with `git-ops`, intention becomes execution without a human relay.

### TIER 3 — Gaps to close (heavier, but real)

**F. Security skill** (`/cso` adapted) — **highest RISK item**
- *What:* OWASP Top 10 + STRIDE + zero-noise 8/10 confidence gate + independent finding
  verification (anti-anchoring) + variant analysis. Note exclusion #1's carve-out: LLM
  cost/spend amplification IS treated as financial risk — directly relevant to your
  API-heavy stack where runaway spend is the actual threat.
- *What for:* you have ZERO security review across auctions, payments, tokenization, and
  user data (Subastop, CarMatch, tokens). A tokenized auction platform with no security
  skill is a standing liability. This is the most important out-of-scope item by risk, even
  if not by excitement.

**G. Cross-model second opinion** (`/codex` analog)
- *What:* a SECOND model (GPT/Gemini via CLI) adversarially challenges Claude's output.
- *What for:* the multi-model version of your `critical-thinker`. You are Opus-locked
  (hence `offload`); a different model has genuinely different blind spots.
- *GATE:* run `dependency-audit` first — this adds an external paid CLI dependency.

---

## 3. Out-of-scope automations — rated honestly

| Automation | Verdict |
|---|---|
| Taste-memory (decaying preference profile) | **BUILD (Tier 2D).** Genuinely novel, generalizes, fits your psychology. |
| `/cso` security | **BUILD (Tier 3F).** Real gap, highest risk. |
| `/spec --execute` worktree | **BUILD (Tier 2E).** Closes your IB->builder gap. |
| Cross-model `/codex` | **MAYBE (Tier 3G).** Valuable; dependency-audit it. |
| `/retro` eng-manager analytics | **SKIP for now.** Git per-person analytics is for teams; M1/M2/M3 are machines, not people. `/retro compare` (window-over-window throughput) is marginal solo. |
| `/canary` + web `/benchmark` | **DEFER.** You have `herald-health-monitor` (currently noisy — fix with `herald-config-doctor` first). canary's screenshot-baseline-diff is more rigorous; harvest the idea only after Herald is clean. |
| `/pair-agent` shared browser | **DEFER.** You coordinate via the `agent-bridge` async message bus, not live shared browsers. Different coordination model; not urgent. Revisit if you ever need two agents on one live session. |

---

## 4. Where you are already ahead

Do not read gstack as the thing to catch up to. It is a **single-builder brain** (gbrain
syncs one person's memory across machines). You run a **federation** — `agent-bridge`, UUID-
addressed Notion inboxes, 19 projects across 3 machines + Chat. That is architecturally more
ambitious than anything in gstack. The synthesis move is to push gstack's INTRA-skill
discipline (preamble, completion-status vocabulary `DONE / DONE_WITH_CONCERNS / BLOCKED /
NEEDS_CONTEXT`, learning provenance) DOWN into your INTER-agent federation, so bus messages
carry standardized state instead of freeform prose.

---

## 5. The honest constraint

This document lists seven builds. Handing seven new things to a platform-gravity builder is
the exact sprawl that produced 60 skills + 5 meta-skills to govern them. **Resist it.** Build
**A (the Independent Verifier) only.** It is the keystone: it doubles as the success-signal
substitute, it is gstack's actual architecture, and it upgrades every gate you already own.
Ship it, watch it fire in real use, and only then unlock B through G. If A does not change
how a real session goes, nothing downstream will either — and you will have learned that
cheaply instead of after building all seven.
