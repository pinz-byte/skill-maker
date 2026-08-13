---
name: pre-deliver
description: Pre-delivery gate for strategic artifacts in AVT_CarMatch_meta. Runs six checks BEFORE shipping — canonical-read, scope-split, confidence-calibration, reframe-vs-extend, memory-hit, self-pattern-match — emits PASS or BLOCK with corrections. Trigger BEFORE writing or editing BUILDER_PROMPT_*.md, IB_*.md, DIAGNOSTIC_*.md, AUDIT_*.md, RECON_*.md, FERRY_*.md, ANALYSIS_*.md, REFRAME_*.md in this project; BEFORE recommending a strategic fork (α vs β, this vs that, abort vs continue); BEFORE reframing session direction; BEFORE sending strategic recommendation longer than ~40 lines. Trigger AFTER POPs reframes mid-session (frustration markers, "indignante", "te equivocas", "actually", direction change). Also use on "/pre-deliver", "gate this", "before I send", "run the gate", "is this ready". Enforcement layer for feedback_* memories that exist as documentation but don't fire at decision time.
---

# Pre-Deliver Gate
Updated: 2026-06-02

> Documentation that lives in memories is not enforcement. This skill is the enforcement.

The agent invokes this skill BEFORE producing any strategic artifact in AVT_CarMatch_meta. The skill emits a GATE REPORT. If any gate BLOCKS, the agent corrects before delivering.

## When this fires

**Always before:**
- Writing or editing `BUILDER_PROMPT_*.md`, `IB_*.md`, `DIAGNOSTIC_*.md`, `AUDIT_*.md`, `RECON_*.md`, `FERRY_*.md`, `ANALYSIS_*.md`, `REFRAME_*.md` in `/Users/lfp/Dev/AVT_CarMatch_meta`
- Recommending a strategic fork (α/β, this/that, abort/continue)
- Reframing session direction
- Sending a strategic recommendation > 40 lines

**Always after:**
- POPs reframes the session ("indignante", direction change, frustration markers)

## The six gates

Run all six. Each emits PASS or BLOCK with one-line reason. If any BLOCK, do NOT deliver — fix and re-run.

### Gate 1 — Canonical Read

For the deliverable's domain, what files already exist in canonical?

```
ls /Users/lfp/Dev/AVT_CarMatch_meta/ | grep -iE "<domain_keyword>"
```

For each match:
- READ it this session, OR
- Mark "intentionally skipped because <reason>"

**BLOCK if:** any unread canonical match exists without explicit justification.

This operationalizes `feedback_read_canonical_first`. Today's PARLAY incident is the canonical failure case.

### Gate 2 — Scope

Count seams / owners / components touched by the deliverable.

- 1 seam → PASS
- > 1 seam → **BLOCK** unless POPs explicitly requested batched work this turn.

Split into N per-seam asks before proceeding. Default is lean. Mega-prompts require explicit invocation, not the inverse.

Project rule: "prefer 3 focused prompts over 1 mega-prompt unless the work genuinely shares a single steward."

### Gate 3 — Confidence Calibration

For each substantive claim in the deliverable, attach marker:

- `✓` verified (cited file:line, direct observation, POPs stated explicitly)
- `⚠` inferred (best hypothesis, not verified against source)
- `🚫` unknown (mentioned but no evidence; flagged for verification)

**BLOCK if:** > 80% of claims in a single inference chain are `✓`. Real chains have mixed confidence. Uniform high confidence across multiple inferential hops is the over-pattern-matching signature.

Today's PARLAY reframe failed this: three mappings presented at uniform high confidence, two were inferential at flow-level (not code-level).

### Gate 4 — Reframe-vs-Extend

Did POPs reframe in the last 3 turns? Markers:
- "actually...", "no, te equivocas", "indignante", "lo que dices no es..."
- Direction change ("prefiero X" after asking for Y)
- Frustration markers
- "you've got mail" pattern shifting topic

If yes:
1. Re-read POPs's turn 1 of the reframe.
2. Identify: which frame is the current deliverable extending? Was it validated by POPs explicitly, or did the agent assume continuity?
3. If unvalidated frame → **BLOCK**. Restart from POPs's stated frame.

Operationalizes `feedback_recommended_hint_anchors_wrong_scope`: "POPs reframes mid-session ARE the signal that previous frame was wrong — re-read turn 1, don't extend wrong branch."

### Gate 5 — Memory Hit

Which `feedback_*.md` memories match the deliverable type?

Quick map:

| Deliverable type | Memories to check |
|---|---|
| Builder prompt | feedback_meta_owns_prompt_authoring, feedback_builder_prompt_recipient_header, feedback_function_deploy_scope_discipline, feedback_scope_reachability_gate |
| Audit | feedback_audit_prescriptive_substitution, feedback_audit_measurement_basis, feedback_audit_findings_to_single_owner, feedback_code_existence_not_runtime_success |
| Diagnostic | feedback_pipeline_truth_first, feedback_regression_framing, feedback_extractor_key_format_drift |
| Strategic reframe | feedback_read_canonical_first, feedback_critical_thinker_default, feedback_macro_means_filter_not_catalogue |
| Mega-prompt | project rules (3 focused > 1 mega) |
| IB | feedback_ib_scope_contamination |

For each relevant memory:
- Does the deliverable comply or violate?

**BLOCK if:** any violation. Cite the memory and the specific clause violated.

### Gate 6 — Self-Pattern Match

Does the deliverable contain self-criticism about a behavioral pattern (e.g., "I've been menu-asking", "I keep re-deriving")?

If yes:
- Does the deliverable itself commit the same pattern at any point?

**BLOCK if:** the self-criticism appears alongside an instance of the criticized pattern. Rewrite to remove the pattern, not to apologize for it.

Today's session repeated this: self-criticized menu-asking, then ended with a menu question. Self-criticized mega-prompts, then shipped a 600-line ferry.

## Output format

After running all six gates, emit:

```
PRE-DELIVER GATE REPORT
=======================
Deliverable: <one-line description>
Domain: <area: pipeline / UX / IB / audit / etc>

Gate 1 — Canonical Read:     PASS | BLOCK
  Read this session: <files>
  Skipped (with reason): <files + reason>

Gate 2 — Scope:              PASS | BLOCK
  Seams touched: N
  Owners involved: N
  Action: <proceed as 1-seam ask | split into N>

Gate 3 — Confidence:         PASS | BLOCK
  Claims: X ✓ / Y ⚠ / Z 🚫
  Chain uniformity: <yes | no>

Gate 4 — Reframe-vs-Extend:  PASS | BLOCK
  POPs reframed last 3 turns: <yes | no>
  Frame source: <POPs explicit | agent-assumed>

Gate 5 — Memory Hits:        PASS | BLOCK
  Relevant memories: <list slugs>
  Violations: <list or none>

Gate 6 — Self-Pattern:       PASS | BLOCK
  Self-criticism present: <yes | no>
  Pattern recurrence: <yes | no>

VERDICT: PASS | BLOCK
If BLOCK: <specific corrections required>
```

## After PASS

Proceed with delivery. The gate is the only "permission to ship."

## After BLOCK

Do NOT deliver. For each BLOCKING gate, apply the specific correction listed. Re-run the skill. Iterate until PASS.

If a gate keeps BLOCKING after 2 iterations, the deliverable is structurally wrong — escalate to POPs with the gate report instead of attempting a third correction.

## Honest limits

This skill cannot enforce. It can only check. The agent must invoke it before authoring; if the agent skips it, no gate fires.

Mitigations:
1. SKILL.md description above contains explicit triggers for all known delivery moments — agents matching descriptions should hit them.
2. POPs may invoke `/pre-deliver` manually before accepting any strategic deliverable from the agent.
3. Pair with CLAUDE.md rule referencing this skill at session start so it's in primary context.

This is mitigation, not enforcement. Real enforcement requires a hook layer that doesn't exist in this environment. This is the closest approximation available without that hook.

## Invocation examples

```
/pre-deliver
```

```
gate this before I send
```

```
run the pre-deliver check on FERRY_D1
```

```
[automatic] About to Write BUILDER_PROMPT_FOO.md — invoking pre-deliver first
```
