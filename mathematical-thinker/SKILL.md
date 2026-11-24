---
name: mathematical-thinker
description: >
  Solve problems through abstraction, simpler cases, structural analogies,
  decomposition and verification, adapted from Terence Tao's mathematical
  thinking class guide. Use when the user asks for "pensamiento matematico",
  "mathematical thinking", "metodo de Terence Tao", "mathematical thinker",
  or wants to model a problem, design informative tests, or get unstuck on a
  mathematical or practical problem with explicit constraints. Use for finding
  a solution; argument auditing alone belongs to logic-thinker. Routine
  arithmetic does not need the full workflow.
metadata:
  intent: reason
---

# Mathematical Thinker

Turn a difficult problem into a representation that makes useful progress
possible. Adapted from Terence Tao's MasterClass guide; this workflow is an
editorial synthesis, not a named algorithm or a claim to speak as Tao.

Work in the user's language. Scale the method to the difficulty: a simple
problem may need only a model, a calculation and a check. For a hard problem,
iterate the moves below as evidence demands rather than filling every section.

## How to work

### 1. Define the problem worth solving

- State the requested result and what would count as success: an exact answer,
  a proof, an estimate, a feasible plan, or a reduction in uncertainty.
- Identify known quantities, unknowns, constraints and assumptions. Preserve
  the user's objective; if several objectives conflict, make the tradeoff
  explicit. Ask only for missing information that materially changes the answer.
- For an open problem, choose an attainable subproblem near the edge of the
  available tools. Explain how solving it advances the original goal.

### 2. Strip to essentials and choose a representation

- Separate the relationships that determine the answer from narrative detail.
  Use variables with units, a diagram, a table, a graph, or a set of possible
  scenarios when that representation clarifies the structure.
- Say what each object represents and what the model leaves out. Do not remove
  a constraint merely because it makes the problem difficult.
- When simplifying, distinguish an equivalent reformulation from an
  approximation or a deliberately altered practice problem. Record what must
  be restored before transferring an answer to the original setting.

### 3. Learn from a smaller problem

- Try a small instance, a boundary case, or a version with fewer variables.
  Use it to discover a pattern, an invariant, or a reason a proposed method fails.
- Decompose into subproblems whose outputs actually combine into a solution;
  retain interactions and dependencies between them.
- Look for a solved problem with the same relationships. State the structural
  correspondence and where it breaks. A suggestive analogy is not a proof.
- Reuse a known tool when it fits. For example, local linearization can make
  a curve tractable, but its validity range must survive the return to reality.

### 4. Make the next move informative

- Choose a calculation, construction, experiment or counterexample that could
  resolve the most consequential uncertainty. Prefer a concrete attempt over
  repeatedly describing a possible approach.
- In identification problems, distinguish objects from hypotheses about them.
  A coin's identity and whether it is heavier or lighter are different unknowns.
- Where a reliable test has two outcomes and scenarios are equally plausible,
  aim to split the remaining scenarios roughly evenly. With unequal priors,
  reason about probability mass; with costs, noisy tests or asymmetric losses,
  account for those too. Equal-size groups of objects need not yield equally
  informative outcomes. Do not claim an optimal strategy without establishing it.
- If an attempt fails, identify the assumption, case or representation it ruled
  out. Use that result to choose a different move.

### 5. Change approach when blocked

- Name the specific obstruction: missing data, an unjustified step, a difficult
  subproblem, or attachment to one representation.
- Change something substantive: numbers to a diagram, objects to scenarios,
  the full problem to a smaller case, or an exact calculation to a justified bound.
- Consult a complementary perspective or propose a focused review question
  when it would help. Collaboration does not itself authorize spawning agents
  or contacting anyone; follow the current environment's permissions.
- Allow partial progress and a deliberate pause. If another attempt would add
  no information, return the established result, the exact obstruction and the
  next useful experiment or missing input. Do not keep cycling indefinitely.

### 6. Return to the original problem and check

- Restore omitted constraints and test whether the model's answer still fits.
- Check arithmetic, units, limiting cases and feasibility. For a universal
  claim, seek a counterexample or a proof; a few successful examples are not enough.
- Use computation when enumeration or numerical checking materially reduces
  error. Distinguish a verified finite search from an unrestricted theorem,
  and a simulation from a proof. Report only checks actually performed.
- Label the outcome as established, conditional on named assumptions,
  approximate with stated limits, or partial. Keep exact expressions separate
  from rounded numbers.

## Useful response

Give the answer or current result first, then a concise, checkable explanation:
the essential model, the decisive transformation or calculation, the verification,
and any limitation that changes how the result can be used. Include equations or
a small visual only when they make the result easier to assess. If unresolved,
end with the specific next step. Do not produce a transcript of private deliberation.

## Edge cases

- **Missing evidence:** derive a conditional answer, bound or decision rule if
  useful. Do not manufacture numbers to make the model solvable.
- **Human decisions:** quantify what is measurable and retain preferences,
  incentives and qualitative constraints. A numerical model cannot establish
  the user's values or turn an association into causation.
- **Approximate method:** explain why it applies and what could invalidate it;
  a solution to the simplified problem may not solve the original one.
- **Practice request:** if the user asks for hints, reveal a useful representation
  or smaller case before the full solution, respecting their requested depth.

## Source and examples

Based on *Terence Tao Teaches Mathematical Thinking*, MasterClass class guide
(2022), especially printed pp. 25-27, 31-38 and 45. See
[references/source-and-examples.md](references/source-and-examples.md) for source
mapping and worked examples of model choice, informative tests and exactness.
The skill is self-contained and does not require access to the original PDF.

## Principles

- Simplification must preserve the path back to the real problem.
- Intuition generates candidates; evidence and verification establish results.
- Failure is useful when it changes what is known or what to try next.
- Measure progress by resolved uncertainty and justified results, not by notation
  volume, speed alone, or the appearance of a sudden breakthrough.
