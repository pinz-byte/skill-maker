---
name: inpositive-language
description: >
  Enforces the InPositive Language System -- Subastop's positive-language framework --
  on all copywriting: landing pages, ads, emails, product copy. Core rule: copy should
  read as affirmative and possibility-oriented, never negated or deficit-framed. Runs
  a 3-step edit pass: (1) flag negation and limiting words (no, not, don't, can't,
  never, impossible, problem, fail, lack, difficult, worry, struggle); (2) reframe
  each flag into an affirmative statement with the same factual meaning; (3) polish
  for tone (ambitious, resilient, optimistic). Use whenever the user asks to write,
  edit, review, or QA copy for Subastop or a brand deliverable, or says apply
  InPositive, check the language, positive language pass, is this copy InPositive,
  reframe this negative copy, no negative words, or run the InPositive check. Also
  trigger before finalizing marketing copy, landing pages, ad creative, or email in a
  Subastop project. Preserves negation required for legal, safety, or factual accuracy
  -- flags those instead of rewriting.
metadata:
  intent: write
---

# InPositive Language Enforcer

Source: Subastop's "InPositive Challenge" framework. Stripped of its philosophical
scaffolding (psycholinguistics, neuroplasticity, quantum-mechanics metaphors), the
framework reduces to one operational rule that copy can actually be checked against:

**Language patterns reshape mindset. Copy that leads with negation or deficit framing
produces a weaker read than copy that leads with affirmative, possibility-oriented
framing carrying the same information.** This skill enforces that rule mechanically --
it does not require believing the neuroscience framing, only applying the resulting
style rule consistently.

## The 3-Step Method

Apply this pass to any copy before it ships. Do not skip to Step 2 -- flagging first
prevents rewriting sentences that didn't need it.

### Step 1 -- Flag

Scan the draft and mark every instance of:

- **Explicit negation:** no, not, don't/doesn't/didn't, can't/cannot, won't/wouldn't,
  never, isn't/aren't, without
- **Deficit/limiting nouns:** problem, issue, failure/fail, lack, shortage, risk,
  difficulty, struggle, worry, impossible, limitation, obstacle, hesitate/hesitation

List each hit with its exact location (line, section, or button/label name) -- don't
paraphrase the flag, quote it verbatim so the next step has something concrete to work
from.

### Step 2 -- Reframe

For every flag, rewrite the sentence to carry the identical factual meaning stated as
capability, outcome, or possibility -- not as the absence of something. The bar is: the
new sentence must say the same thing, just never through the negative frame.

| Negative frame | InPositive reframe |
|---|---|
| "Don't miss out" | "Claim your spot" |
| "No hidden fees" | "Every fee, upfront" |
| "We won't let you fail" | "We back you until you win" |
| "There's no problem we can't solve" | "Every challenge here has a path through it" |
| "Don't worry about the paperwork" | "We handle the paperwork" |
| "You can't lose" | "Every outcome moves you forward" |
| "It's not that hard" | "It's simpler than it looks" |
| "No risk" | "Fully protected" |

A single word swap is often enough -- per the source material's "Power of One Word":
prefer the smallest edit that removes the negation over a full rewrite.

### Step 3 -- Polish

Re-read the reframed copy as a whole. Check it reads as ambitious, resilient,
optimistic, curious, courageous, self-confident, original -- the InPositive trait
register -- rather than merely negation-free. A sentence can be technically free of
"no"/"not" and still read flat or hedging ("might possibly maybe help"); tighten those
too. Do not let the polish pass introduce hype or unverifiable claims -- see Edge Cases.

## Output Format

When reviewing copy, report:

```
**InPositive Check**
Flagged: [n] instances

1. "[exact quote]" -- [location]
   -> "[reframed replacement]"
2. ...

**Clean copy:**
[full reframed text]
```

If nothing was flagged, say so in one line and still confirm the Step 3 tone check was
run.

## Principles

- **Same meaning, different frame.** A reframe that changes what's actually being
  promised is not a reframe, it's a different claim. Verify the reframed sentence is
  still factually equivalent before accepting it.
- **Smallest sufficient edit.** One word swapped beats a rewritten sentence; a rewritten
  sentence beats a rewritten paragraph.
- **This is a style rule, not a censorship rule.** The goal is affirmative framing, not
  the literal elimination of every "no" at all costs -- see Edge Cases for where
  negation stays.

## Edge Cases

- **Legal, safety, or compliance text** (disclaimers, terms, warnings, "this is not
  financial advice," "do not use if...") -- do not force-reframe. Flag it as exempt and
  leave it as-is; accuracy outranks tone here.
- **Verbatim quotes or testimonials** -- never alter third-party words. Flag if a quote
  reads negatively, but the fix is choosing a different quote, not editing the person's
  words.
- **Reframes that overpromise** -- "no risk" becoming "fully protected" is only valid if
  it's actually true. If the honest reframe would be a stronger claim than the source
  fact supports, keep the softer (even if negatively-framed) original and flag the
  tension for the user to resolve rather than silently inflating the claim.
- **Idiomatic negatives that are already the strongest version** ("no questions asked,"
  "won't be beaten on price" as an established brand line) -- flag but ask before
  replacing an established tagline.
