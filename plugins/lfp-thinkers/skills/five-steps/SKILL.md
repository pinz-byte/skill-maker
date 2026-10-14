---
name: five-steps
description: >-
  Runs Elon Musk's five-step algorithm, strictly in order, on a requirement list, process,
  pipeline, or plan: make the requirements less dumb, delete the part or step, simplify,
  accelerate, automate -- and refuses a later step before the earlier ones are exhausted.
  Use whenever the user says "five steps", "cinco pasos", "the algorithm", "musk", "apply
  the algorithm", "question the requirements", "cuestiona los requisitos", "delete the
  part", "what can we delete", "simplify this process", "before we automate", "is this
  step necessary", or asks to optimize, streamline, or redesign any process. Also trigger
  PROACTIVELY when someone proposes a hook, cron, script, or any automation for a process
  nobody has questioned or pruned yet -- the reverse-order mistake this skill catches. NOT
  ceo-planner (reviews a finished plan's scope) or critical-thinker (attacks the premise):
  this works the requirement list and the process itself, deleting before it optimizes.
metadata:
  intent: reason
---

# Five Steps -- The Algorithm, In Order

The five-step process Elon Musk uses to design and fix production systems. It is a
sequence, not a checklist: each step is only legal once the previous one is exhausted.
Most process failures are not bad steps -- they are the right steps run in the wrong
order: a cron job that automates a report nobody reads, a faster pipeline for a stage
that should not exist. This skill exists to hold the order.

## Where this sits -- and what it is not

Object: a requirement list, a process, a pipeline, a spec, a build plan, a ritual.
Moment: BEFORE anything gets optimized, sped up, or automated -- and whenever an
existing process feels heavy.

- It does not attack the premise behind the thing -- `critical-thinker`.
- It does not set a plan's scope ambition (expand / hold / reduce) -- `ceo-planner`.
- It does not price external dependencies -- `dependency-audit`.
- It does not escape a recurring failure frame -- `loop-breaker`.

It can be called from any of those. It never re-implements them.

## The five steps -- strictly in order

### 1. Make the requirements less dumb

Assume every requirement is wrong until it survives a question. For each one, write
WHO asked for it -- a person, not a department. "Legal", "the team", "best practice"
and "we always did it" are not owners. A requirement with no owner is deleted in
step 2 by default. Requirements from smart or senior people are the most dangerous:
they get questioned least, so question them hardest. Everyone is wrong part of the
time, including the person running this pass.

### 2. Delete the part or the step

For every remaining part, step, file, job, store, check: try to remove it. The
default answer is delete; the burden of proof is on keeping. Reject every "in case"
argument -- an "in case" can be invented for anything, so it proves nothing.
Benchmark: if nothing you deleted ever has to be added back, you did not delete
enough. Expect to add back roughly one in ten; that is what a deep enough cut
looks like.

### 3. Simplify or optimize

Only now. Simplify what survived steps 1 and 2. Optimizing a part that should not
exist is the most common engineering error: it feels like progress and is pure
waste. If a surviving step is complex, first ask whether step 2 was skipped on it.

### 4. Accelerate cycle time

Only after 1-3. Make the surviving steps faster: shorter loops, fewer handoffs,
smaller batches. Speed applied to an unpruned process produces waste faster.

### 5. Automate

Last. Hooks, cron, launchd, scripts, bots, CI: only for a process that is already
lean and fast by hand. Automating a bad process freezes it and hides it from the
next person who would have questioned it.

## Reverse-order detector

Stop and name it when any of these appear:

- Automation (hook, cron, script, pipeline stage, bot) proposed for a process whose
  requirements have no written owners -- steps 1-2 were skipped.
- "Let's make X faster" where nobody has asked whether X should exist.
- A new part added to absorb a problem that deleting another part would solve.
- "Just in case" given as the reason a part survives.
- A requirement defended by who said it rather than by why.

The correction is always the same: go back to the lowest step that was skipped.

## How to run it

1. Name the object in one line and list its parts or steps, numbered.
2. Walk steps 1-5 in order, one pass. When a later step looks attractive, note the
   idea and finish the earlier step first.
3. Produce the table, one row per part:

```
  PART / STEP | OWNER (who asked) | WHY | VERDICT (delete / keep / simplify) | NOTES
```

4. Close with: what was deleted; what was kept and why; the ONE next action; and what
   the user should expect to add back later. If the answer is "nothing", say the cut
   was shallow.

Verdicts, not options. Lead with the recommendation.

## Principles

- **Order is the content.** The steps are well known; running them in order is the
  whole discipline.
- **Delete is the default.** A part survives by evidence, not by inertia.
- **Authority is not a reason.** The source of a requirement is a risk factor, not a
  justification.
- **"In case" is not an argument.** It is the absence of one.
- **The add-back rate is the metric.** Zero add-backs means timid deletion.
- **Automate last, and only what earned it.**

## Edge cases

- **The requirement is the user's own.** Question it the same way, and say plainly
  when it has no owner-level reason. That is the job.
- **The object is tiny.** Still run the order, in three lines. The point is the
  habit, not the ceremony.
- **The user wants step 5 now.** Do not start there. Run 1-3 in brief; if the process
  survives, automate what survived, not the original.
- **Steps 1-3 delete the whole thing.** That is a success. Report it and stop; do not
  invent a smaller thing to optimize.
- **Nothing to delete.** Suspect the pass, not the process. Report a zero deletion
  rate as a finding that is unlikely to be true.
