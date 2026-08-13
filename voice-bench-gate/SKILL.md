---
name: voice-bench-gate
description: >-
  Grounds outbound copy in verified sources before it gets written — pulls the project's voice
  lock, forbidden words, and confirmed policies, and requires every new claim or angle to cite
  a validated precedent or a real-world check before it ships. Use whenever writing or
  revising sales emails, sequences, ad copy, or customer-facing text for a project with a
  brand voice or policy history — trigger on "escribe el copy", "redacta el correo", "dame el
  ángulo", "arma la secuencia", "Touch 2/3/4", "ángulo para [vertical]", "necesito copy para",
  "write the email", "draft the sequence", or any marketing/sales text request. Also trigger
  proactively before delivering drafted copy in a project with existing voice-lock/brand docs
  — the failure this prevents (rewriting after contradicting a rule or repeating an unverified
  claim) is silent unless checked before delivery. NOT copy-deck (writes the copy): this
  grounds every claim in a verified source before the copy gets written.
metadata:
  intent: write
---

# Voice Bench Gate

## Why this exists

Reactive drafting — writing sales or marketing copy from pattern-matching or a first
instinct — produces three specific failures, all of which look fine in isolation and
only surface when someone actually checks:

1. **Redundant escalation.** A sequence's Touch 2 restates Touch 1's claim in different
   words instead of adding something new, so the "curve" of the sequence flattens
   without anyone noticing until they read all the touches back to back.
2. **Ungrounded claims.** An angle, objection, or piece of industry detail gets invented
   because it *sounds* plausible, without checking it against the project's own
   confirmed policy or against how the target audience actually operates.
3. **Craft on autopilot.** The copy leans on generic LLM tells instead of a real
   persuasion technique — most commonly the false-contrast rhetorical move ("X is not
   a Y, it's a Z" / "no es un problema, es una oportunidad") that sounds like insight
   but carries no actual argument. This happens even when checks 1 and 2 pass — the
   facts can be grounded and the angle can be fresh, and the copy can still read as
   AI-generated because the sentence-level technique wasn't chosen on purpose.

The fix isn't "be more careful." It's making grounding a required step *before* the
words get typed, not a cleanup that happens after someone points out the problem —
and that applies to the persuasion technique itself, not just the facts inside it.

## The gate — run both checks before delivering copy

**1. Precedent/policy check.**
Find the project's voice/brand reference material — a Voice Lock section, a style
guide, a CLAUDE.md, or a capsule/decision log describing confirmed rules. Then check
the draft against it:

- Does it repeat a claim or angle a prior touch in the *same* sequence already made?
  Don't compare from memory — open the actual prior touches and read them verbatim.
- Does it use language the project has explicitly banned, or contradict a policy
  that's already confirmed as final (not merely proposed or "pending")?

If either check fails, fix it before moving on. Don't deliver copy with a defect you
already know about.

**2. Grounding check.**
Every concrete claim in the copy — an objection, a mechanism, an industry-specific
detail — needs one of two things behind it:

- A citation to the project's own validated material (an already-approved touch, a
  confirmed policy, a verified figure), or
- A real check against the world the copy describes — a targeted web search on how
  the actual audience/industry operates — if the claim depends on something not
  already known for certain.

Don't invent industry jargon, objections, or mechanisms from a guess dressed up as
insight. If a claim can't clear either bar, that's the finding: research it, or flag
it plainly as an unconfirmed assumption that needs sign-off — don't ship it quietly.

**3. Persuasion-technique check.**
Before writing, decide on purpose which real technique the copy is using — don't let
one emerge by accident from pattern-matching. For B2B cold-outbound sequences, two
frameworks cover almost everything:

- **SPIN (Rackham)** for the shape of a touch: Situation, Problem, Implication,
  Need-payoff. The Problem step should usually be a genuine question the *reader*
  answers about themselves, not a statement telling them what their situation is.
  "How much old stock do you have sitting in the warehouse right now?" respects the
  reader's own read of their situation; "your stock is a problem, not an asset" tells
  them what to think, and reads as manufactured insight rather than a real question.
- **Cialdini's principles** for which specific lever a claim is pulling: authority
  (verified numbers, track record), scarcity (a real time or market constraint, never
  invented urgency), social proof (category-level, never naming a real customer
  unless the project has explicitly cleared that), commitment (a small first ask
  like a pilot, not the full ask up front), reciprocity (something free/low-cost
  offered before asking for the sale).

Name which technique and which lever each touch is using as part of grounding it —
if you can't name one, that's a sign the copy is running on autopilot, not a chosen
approach.

**Ban the false-contrast tell specifically.** Sentences shaped like "no es X, es Y" /
"it's not X, it's Y" are the single most recognizable LLM tell in sales copy — they
manufacture the feeling of a reframe without giving the reader a real reason to
believe it. If a draft leans on this shape, that alone is a signal to rewrite the
sentence as a direct statement, a real question, or a concrete implication instead.

## How to run the checks efficiently

- Read prior touches/emails in the sequence verbatim before writing the next one.
  A paraphrased summary hides exactly the kind of repetition this gate exists to
  catch.
- One or two targeted web searches are usually enough to ground an industry claim —
  search for how the real audience operates, not generic copywriting advice.
- If two candidate angles resolve the same underlying point (e.g., an operational-
  continuity mechanism and an objection that the same mechanism already answers),
  that's a signal to differentiate them explicitly or merge them. Don't let a
  sequence carry the same message three times under different wording.

## What passing the gate looks like

Before or alongside the copy, state briefly which rule, precedent, or research
grounds each new claim, and which persuasion technique/lever each touch is using.
If nothing grounds it, say that plainly — that's a real finding, not a gap to paper
over.

## Example (generalized from a real case)

A sequence's Touch 1 for a given persona already said "you keep operating for 180
days after selling." Touch 2 was drafted as "the friction of coordinating a sale
without stopping operations" — which is the *same claim* as Touch 1, not a new one.
The gate catches this by reading Touch 1 verbatim before drafting Touch 2, and forces
a genuinely new angle instead (in this case, a two-search web bench on how the
target industry actually disposes of used equipment surfaced a sharper, grounded
angle: public marketplaces expose the seller's restructuring to competitors, while
informal brokers set price without competition — both problems a private-auction
mechanism solves, which is also a claim the project's own voice lock already
supported).

## Example 2 — the craft check catching what the fact check missed

A rewritten touch was fully grounded (a real regulation, a real depreciation rate)
and didn't repeat any prior touch — checks 1 and 2 both passed — but it opened with
"that old stock is a space-and-inventory problem — not an asset," and used the same
"public channel vs. single middleman" contrast shape across four different verticals
with only the noun swapped. Both are autopilot tells: the false-contrast sentence,
and a structure reused across unrelated products without asking whether each one
actually needed its own reasoning. The fix wasn't more research — the facts were
already fine — it was picking an actual technique (a SPIN-style question the reader
answers about their own situation, e.g. "how much old stock do you have sitting in
the warehouse right now?") and letting each vertical's real implication (regulatory
traceability, seasonal market flooding, project-closeout accounting, depreciation
while idle) drive a distinct shape instead of one recycled skeleton.

## When not to over-apply this

This gate is for claims and factual/structural content, not for stylistic word
choice with no factual weight (e.g., picking between two near-synonyms). Don't turn
every sentence into a research project — the check exists to catch redundancy and
unverified claims, not to demand perfection on phrasing.
