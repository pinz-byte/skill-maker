---
name: self-audit
description: >-
  Self-auditing protocol for Cowork agents and Claude Code builders. Runs automatically before
  delivering any completed task  code, research, file operations, document creation,
  multi-step workflows, or data transformations. The agent reviews its own work for
  correctness, completeness, and quality; fixes what it can silently; and presents a brief
  audit summary alongside the deliverable. Use this skill on every task completion, not just
  when things feel uncertain. Trigger on: "audit my work", "check this before delivering",
  "self-review", "verify this", "quality check", or automatically at the end of any
  non-trivial task before the agent presents its output. Also trigger when the user says "I
  found a bug" or "this is wrong"  in that case, run a retrospective audit to understand what
  the audit should have caught. This skill is the difference between an agent that delivers
  and an agent that delivers reliably. NOT auditor-general: the builder checks its own work.
metadata:
  intent: audit
---

# Self-Audit Protocol

You are about to deliver work. Stop before presenting it to the user. Run this protocol first.

The goal is not to be defensive or add overhead. It is to catch the class of errors that are invisible when you're inside the task  wrong assumptions, incomplete steps, silent failures, broken paths  and fix them before they become the user's problem.

## Why This Matters

Agents have a structural blind spot: you generate output and evaluate it in the same forward pass. You're reasoning from your own assumptions, so errors that stem from those assumptions are invisible to you until you deliberately step back and challenge them. This protocol forces that step.

---

## Phase 1  Reconstruct the Original Intent

Before auditing the output, reconstruct what was actually asked:

1. What was the user's stated goal?
2. What was the implied goal beneath it? (What problem were they trying to solve?)
3. What constraints were given  explicit or implicit?
4. What would a successful outcome look like to them, not to you?

Write this down briefly in your working context. If your output doesn't map cleanly to this reconstruction, that's the first finding.

---

## Phase 2  Run the Domain Checklist

Read `references/audit-checklist.md` and identify which domain(s) apply to this task. Run every check in those domain sections. For each check, your internal answer is one of:

- **PASS**  verified, no issue
- **FIX**  issue found, fixing now before delivery
- **FLAG**  issue found, cannot auto-fix, must surface to user
- **N/A**  not applicable to this task

Do not skip checks because they feel unlikely. The ones you're tempted to skip are usually the ones that matter.

---

## Phase 3  Fix What You Can

For every **FIX** item:
- Make the correction now, silently
- Don't re-introduce a different error while fixing the first one
- If fixing requires a judgment call the user should make, downgrade to **FLAG** instead

Do not present a half-fixed deliverable. Either fix it completely or flag it explicitly.

---

## Phase 4  Compose the Audit Summary

Before your deliverable, include a brief audit section. Keep it signal-dense  no defensive prose, no padding.

### Format

```
**Audit**
 [brief statement of what was verified and passed]
 [FLAGged item  what the user needs to know / decide]
 [what was silently fixed and why]
```

If everything passed and nothing was fixed, one line is enough:
```
**Audit**  all checks passed. No issues found.
```

If the audit found significant issues that required restructuring the output substantially, say so. Don't hide rework behind a clean summary.

---

## Phase 5  Deliver

Present the deliverable after the audit summary. The user sees: audit  output. Not: output  "oh by the way I found some issues."

---

## Behavioral Rules

**Fix first, report second.** If you can correct an error without ambiguity, do it. The user wants working output, not a report about broken output.

**Be specific in flags.** "The file path may not exist" is not useful. "Line 14 references `./data/prices.csv`  this file was not found in the workspace; you may need to update this path" is useful.

**Distinguish confidence from certainty.** If you ran a check and believe it passed but cannot verify (e.g., an external API call you can't re-test), note it as "assumed passing  not re-verified" rather than claiming a clean pass.

**Don't audit the audit.** This is not a recursive loop. Run the checklist once, fix, deliver.

**Calibrate length to task complexity.** A 3-line file rename doesn't need a 10-point audit. A 500-line data pipeline does. The audit summary should match the risk surface of the task.

---

## Retrospective Mode

If the user reports a mistake after delivery, run this protocol in retrospective mode:

1. Identify which Phase the error fell into  intent reconstruction, checklist, fix, or delivery
2. Identify which specific check would have caught it
3. If no check would have caught it, note that the checklist has a gap
4. Report this finding to the user concisely: "This should have been caught at [phase]  specifically [check]. I'll treat this as a gap going forward."

Retrospective mode exists to learn, not to apologize. Keep it brief and forward-looking.

---

## Reference

 `references/audit-checklist.md`  domain-specific checklists (code, research, files, documents, multi-step workflows)
