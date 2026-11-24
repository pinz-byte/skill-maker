---
name: mece-thinker
description: >-
  Turn a complex question into an issue tree with no overlaps or gaps. Use for
  MECE, "sin solapes ni huecos", auditing coverage or double counts, splitting
  work among owners, or locating a bottleneck across a defined pipeline.
  Use Logic Thinker to test an argument and Five Steps to remove or optimize
  process steps; MECE Thinker makes the map those decisions rely on.
metadata:
  intent: reason
---

# MECE Thinker

Build a map in which each item belongs exactly once and the branches cover
the parent. The output is a decision aid, not an action or a guarantee.

## Run the pass

1. **Frame one question.** State the decision, unit, universe, time cut, and
   exclusions. Use the smallest unit you can assign once: a unique order,
   a code plus role, or an individual task. Distinguish observed and assumed.
2. **Split on one axis at a time.** Pick the axis that serves the decision:
   first unsatisfied gate for a pipeline, next action for a queue, or an identity
   for a metric. Define each sibling by its entry rule. Split branches further
   only if the split could change action or ownership. Keep secondary views
   (e.g. team, cause, urgency) as tags, not additional counted branches.
3. **Test overlap and coverage.** Try a boundary case. Ask where it belongs,
   where it must not appear, and what is left out. For mixed cases, state a
   consistent tie-break or go to a finer unit. For enumerated data, deduplicate
   by the key, verify that branch intersections are empty and that the union
   matches the universe. Matching counts alone cannot prove either. Keep an
   explicit unclassified bucket for missing evidence; name the evidence needed
   to empty it. An unclassified bucket is not proof that the cause tree is complete.
4. **Assign and prioritize.** Give each actionable leaf one accountable owner,
   one next step, and a check of completion. Others can support. If ownership
   is unverified, label it proposed. Pick the constraint whose improvement
   best advances the goal, not merely the branch with the lowest number.
   Compare impact, confidence, effort, and dependencies; if evidence is thin,
   say what to measure next rather than guessing.
5. **Return the usable map.** In the user's language, give the scope, a compact
   tree or table, where overlap or gaps were found, and the first move. Mark
   counts as verified, estimates, or unknown. Do not equate assignment with
   execution or a passed sample with a universal result.

## Two boundary cases

- **Sales:** For one period, gross sales = unique buyers x orders per buyer x
  revenue per order. Define orders and revenue on the same basis. One action
  can influence several factors, so do not allocate all of its impact to each.
  If splitting buyers by acquisition and retention, count each unique buyer
  once by their pre-period purchase history, not once per order. A weak
  conversion number is not automatically the best opportunity.
- **Amorata:** To count where valid natal orders are stuck, assign each order
  to its **first unverified gate**: payment/back office, generation, review and
  approval, code delivery, or private access and delivery. Count it as complete
  only after the reading, interactive 3D, and downloadable illustration match
  the same approved natal revision. If the order's evidence cannot identify
  the first unverified gate, classify it as unclassified. A payment failure
  does not also count as a generation failure. Repository CI is a release
  dependency, not a customer-order stage. A real smoke test covers one order;
  independent cases and retry checks add confidence in the general workflow.
