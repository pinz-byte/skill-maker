---
name: soul-builder
description: >
  Builds and maintains a project's SOUL.md -- the always-present, distilled INTENTION of a
  project (its model, invariant, core flow), wired to load every session so a co-worker never
  loses the thread. Use whenever starting/initializing a project, when an IB is done and should
  become persistent guidance, when a session keeps losing comprehension or reasoning from the
  data up instead of the model down, when the user says the agent "lost the thread", or when
  setting up the harness-loaded primitives. Trigger on: "soul", "SOUL.md", "soul builder",
  "distill the IB", "make the intention persist", "project soul", "ground the session", "the
  co-worker doesn't understand the initiative". Also fire when a project's model gets clarified
  mid-session -- update SOUL.md so the correction persists. Continuity seeds persist STATE; the
  soul persists the MODEL.
metadata:
  type: meta-grounding
---

# Soul Builder -- make the intention persist

## The problem this solves
A co-worker can hold the STATE of a project (continuity seeds do that) and still lose the
THREAD -- what the initiative IS, its invariant, why each move matters. Reconstructing the model
from derivative seeds -> reasons data-up, extends wrong frames through reframes, builds machinery
on a misunderstood base. Drift is invisible to the drifting agent.

The fix: put the distilled intention where the harness ALREADY auto-loads it, and trigger
re-anchoring on OBSERVABLE events (reframe, frustration, repeated correction) not self-awareness.

## Architecture -- two primitives
CLAUDE.md (build harness, auto-loaded, carries the SOUL ANCHOR) + SOUL.md (intention, via the
anchor: distilled IB -- model, invariant, core flow, load-bearing facts, reasoning discipline).
IB_*.md = full schema, on demand. Continuity seed = state, on demand. SOUL.md is to comprehension
what the seed is to state.

## How it persists
CLAUDE.md is always in context -> a standing "read SOUL.md before any work; re-anchor on reframe"
directive there is the most reliable trigger available. The soul's irreducible core is echoed
inline in the anchor (guaranteed); the full soul is one mandated read away. Re-anchoring fires on
observable events, not on noticing drift.

## Building / wiring / maintaining
Distill (don't copy) the IB to ~one screen: what it IS, the active-initiative model, the
invariant + misreads-to-avoid, a one-line test that catches a wrong-at-the-base plan, the
reasoning discipline. Insert a SOUL ANCHOR near the top of CLAUDE.md. Update SOUL.md whenever the
model is clarified mid-session (that's how corrections persist). Keep it short; single source of
truth -- retire any duplicate grounding doc/skill and point at SOUL.md.

## Composition rules (so it doesn't collide with IB / the harness / the optimizer)
1. IB is the full schema; SOUL.md is its distillation. When the model is clarified and SOUL.md is
   updated mid-session, you MUST reconcile the IB too -- either re-distill SOUL.md from the
   updated IB, or stamp the IB's model layer "superseded by SOUL.md (<date>)". Never let a live
   SOUL.md and a stale IB disagree; that recreates the drift problem one level up.
2. The SOUL ANCHOR loads FIRST in CLAUDE.md -- model before state before mounts (the soul read is
   cheap and is what everything else should be read in light of). Wrap the anchor in a
   `<!-- custom -->` ... `<!-- /custom -->` block so projectmd-optimizer leaves it untouched on
   its next pass (its standing rule is not to rewrite custom-marked sections).
3. Keep the inline anchor echo to a few lines (the irreducible core only). Load the full SOUL.md
   by PLAIN-PATH pointer, never `@import` -- @import pulls the whole file into every session and
   defeats the tiering that projectmd-auditor/optimizer exist to enforce.
4. reentry owns session-start surfacing: it reads SOUL.md as its first "what is this project"
   line, so the model has one coordinated entry point instead of the anchor and reentry both
   gesturing at it.
