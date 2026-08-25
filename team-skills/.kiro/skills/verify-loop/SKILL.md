---
name: verify-loop
description: >
  Builds an independent check alongside a generation task, before finishing, and
  iterates until it passes for the right reason. Not the same as reviewing your own
  output: a check built from the same assumptions that produced a mistake will pass
  while confirming it. Use when a task has checkable ground truth -- a spec,
  input/output pairs, an invariant -- and no test yet exists: parsers, formatters,
  calculations, data transforms, API handlers. Trigger on: "test this as you go",
  "verify while you build", "give yourself a way to check this", "write tests for
  this", "make sure this actually works", "check your work while coding", "iterate
  against tests", "self-check this build". Does NOT apply with no independent oracle
  -- ambiguous requirements, subjective quality, "is this the right approach" --
  self-judgment there is theater; route to critical-thinker or self-audit. Not for
  reviewing a finished deliverable after the fact -- that is self-audit (pre-
  delivery) or auditor-general (post-hoc, external examiner).
metadata:
  intent: audit
---

# Verify Loop -- Build Against an Independent Check

## The claim, and its limit

"Give it a way to check itself" is real leverage. A builder that runs its own tests
before declaring a task done fixes more, and fixes it faster, than one that generates
once and stops. This holds whenever the task has ground truth external to the model's
own judgment: an expected input/output, an invariant, a spec.

It fails silently the moment the check and the generation share the same blind spot.
If the same reasoning that produced a bug also produced the test, the test encodes
the bug's assumption and will pass while confirming the wrong thing. A green
checkmark from a self-written test on an ambiguous requirement is not verification --
it is the model grading its own homework and calling the grade a fact.

The rule this skill enforces: build the check from the spec, not from the
implementation. Verify against something the implementation cannot have biased.

## Before writing code: find the oracle

Answer this before touching the implementation. State the answer explicitly in your
working context, not just in your head.

1. What defines "correct" here -- a spec, a set of example pairs, an invariant that
   must hold, a reference implementation? Name it.
2. Is that oracle independent of the code you are about to write? A test derived from
   the requirements, written before the code, from examples the user gave -- yes. A
   test you infer from reading your own draft implementation -- no; discard it.
3. If no independent oracle exists -- the requirement is itself ambiguous, or
   "correct" is a judgment call -- say so now. Do not fabricate a test to create the
   appearance of rigor. Route this case to self-audit (reconstruct the user's actual
   intent) or ask the user, rather than manufacturing a self-written test to feel done.

If the oracle cannot be named in one sentence, it does not exist yet. Get one before
writing the implementation, not after.

## Build order

1. Write the check first -- assertions, expected pairs, invariants -- derived from the
   oracle identified above, not from the code that does not exist yet.
2. Write the implementation.
3. Run the check. Read the actual failure, not just pass or fail.
4. Fix the implementation, not the check -- unless the check itself encoded a wrong
   assumption, in which case say so explicitly ("the test assumed X, which is wrong")
   and correct it. Never quietly move the goalpost to make a failing test pass.
5. Repeat until it passes for the right reason, not merely until it passes.

## Distinguishing real convergence from a moved goalpost

Watch for these tells that verification became theater instead of a check:

- The test changed more than once to accommodate the implementation, and you can no
  longer state cleanly what it verifies.
- Every test passes but covers only the happy path considered first -- no boundary
  values, no adversarial input, no case that would contradict the first assumption.
- There is no external spec at all, and the "test" is really the model re-deriving its
  own earlier reasoning in a different form and calling that agreement confirmation.

If any of these are true, say so plainly rather than presenting a clean pass.

## When to escalate past self-check

This skill is the right tool when the oracle is deterministic and the risk is a
coding mistake. It is the wrong tool when:

- The risk is a misunderstood requirement, not a coding error. A test cannot catch a
  misunderstanding it was written under. Reconstruct intent instead, or ask.
- The deliverable is inherently non-deterministic or judgment-based -- copy, strategy,
  architecture choice, design quality. There is no pair of expected values to check
  against. Use critical-thinker or an independent second pass, not a self-test.
- The stakes are high enough that even a genuinely independent self-written test is
  not sufficient assurance. Hand it to an external reviewer -- auditor-general, a
  subagent with no visibility into the implementation, or the user.

## What this looks like in practice

Applies cleanly: parsing, formatting, calculations, data transforms, API contract
handlers. Write the input/output pairs from the spec first. Implement. Run. Iterate on
real failures.

Does not apply: "write better copy for this page," "pick the right architecture," "is
this a good plan." No self-administered test resolves these -- route to
critical-thinker, an independent reviewer, or the user's judgment.

## Principles

- An oracle built from your own implementation is not a check -- it is an echo.
- Convergence toward a passing test is only progress if the test was correct before
  the loop started.
- Admitting "there is no way to verify this deterministically" is worth more than a
  fabricated green checkmark. Say so and route to the right tool instead of
  manufacturing false confidence.
- This skill only claims what self-testing actually buys: fewer coding mistakes,
  faster iteration on checkable work. It does not resolve ambiguity, taste, or
  strategic correctness -- those need a different tool, not a harder-working test.
