---
name: apex-ultra-council
description: >-
  Convene a LIVE APEX MASTERS Council pass under extended reasoning on a named ticker or setup
   the seven voices (Elliott, Hannah, Marco, Theodore, Iris, Felix, Gideon) each argue, then
  synthesize into a single verdict: GO / NEAR-MISS / PASS with a 0-100 asymmetry score,
  action, R:R against the hard 2:1 floor, entry, and the Gideon-override flag. This is the
  GENERATIVE counterpart to the read-only "council" skill: council SHOWS cached machine
  verdicts; apex-ultra-council DELIBERATES a fresh one. Trigger on "apex ultra", "ultra
  council", "/ultra", "convene the council", "deep council", "full council pass", "run the
  council on X", "what would the council say about X", "deliberate X", "ultra verdict", or any
  request to reason out a new Council verdict rather than display an existing one. Fire even
  on casual variants like "throw X at the council" or "give me the full seven-voice read on
  X". For cached tiers use council-global instead.
metadata:
  intent: decide
---

# APEX Ultra Council  Live Deliberative Verdict

A generative reasoning protocol. Where the `council` skill prints cached
verdicts the autonomous loop already wrote, this skill **convenes a fresh
debate** on whatever ticker, trade, or setup the user names, then collapses the
seven voices into one disciplined verdict using the same output grammar.

This skill depends on **no repo, no network, no scripts**  it is pure
deliberation. That is deliberate: it runs identically on M1/M2/M3 Cowork and on
Claude.ai Chat, anywhere the agent can think.

## When to run

Fire when the user wants a *new* read, not a display of an old one. If they say
"what does the council say" about today's saved tiers, that is the `council`
skill. If they hand you a ticker/setup and want it deliberated  that is this.

## Step 0  Extended reasoning is mandatory

This is a high-stakes, multi-voice synthesis. Before producing the verdict,
reason through every voice in full. Append `Ultrathink` as the final line of
your internal planning, or otherwise engage maximum reasoning depth. Do not
shortcut to a verdict.

## Step 1  Ground the inputs

Collect what you actually have before voices speak:

- **Ticker / instrument** and current structure (price, trend, key levels).
- **Proposed action** if the user gave one (long / short / wait), else derive it.
- **Live context**  if running inside the `apex-ultra` repo, load real voice
  mandates and current data from there. If on Chat or anywhere without the repo,
  state plainly that you are reasoning from the context the user provided plus
  general market knowledge, and flag any number you are inferring rather than
  reading. Never fabricate a price, level, or data point  mark it as assumed.

## Step 2  The seven voices each argue

Each voice gets a short, sharp paragraph  its lens, its read, and its vote
(GO / NEAR-MISS / PASS). Voices disagree; do not force consensus. If you do not
know a voice's exact mandate from the repo, use its archetype below and say so.

- **Elliott**  wave structure and technical pattern. Where are we in the count;
  is the move impulsive or corrective; what does the chart demand.
- **Hannah**  price action and momentum at the tape level. Is buying/selling
  pressure confirming the thesis right now, or fading.
- **Marco**  macro and cross-asset context. Rates, sector flows, regime. Does
  the broader tape support or fight this trade.
- **Theodore**  fundamentals and catalyst. Earnings, news, valuation, what
  changes the story and when.
- **Iris**  sentiment, positioning, crowding. Is the trade consensus or
  contrarian; where is the pain trade.
- **Felix**  execution and structure. Liquidity, spread, sizing, where the stop
  actually lives and whether the entry is clean.
- **Gideon**  risk veto. Gideon does not seek upside; Gideon hunts the way this
  loses. Gideon alone holds the **override**: a setup the other six love can be
  forced to PASS if the downside is unacceptable.

## Step 3  Score the asymmetry (0-100)

Synthesize a single asymmetry score: how lopsided is reward versus risk.

- 0-39: thin or negative edge.
- 40-64: real but unconvincing edge.
- 65-79: strong asymmetry.
- 80-100: rare, high-conviction lopsided setup.

State the one or two factors that set the score. The score ranks NEAR-MISSes
against each other; it does not by itself clear the trade.

## Step 4  The R:R gate (hard 2:1 floor)

Compute reward-to-risk from entry, target, and stop.

- **R:R >= 2:1** clears the floor.
- **R:R < 2:1** cannot be a GO no matter how high the asymmetry score  it caps
  at NEAR-MISS, and you must name the R:R that held it back.

If Gideon invokes the override, the verdict is PASS regardless of R:R or score 
say so explicitly and give Gideon's reason.

## Step 5  Emit the verdict (match council's grammar)

Produce exactly this shape so it reads consistently with the `council` skill:

```
TICKER  VERDICT (GO / NEAR-MISS / PASS)
Asymmetry: NN/100   Action: long|short|wait   R:R: X.X:1   Entry: <level>
Gideon override: yes|no
Votes: Elliott <v>  Hannah <v>  Marco <v>  Theodore <v>  Iris <v>  Felix <v>  Gideon <v>
Thesis: <one line  the single reason this is the verdict>
```

Tiers, same as council:

- **GO**  clears the 2:1 R:R floor and no Gideon override. The only auto-fileable tier.
- **NEAR-MISS**  strong asymmetry but blocked; always state what blocked it (usually R:R).
- **PASS**  collapse to one line. If Gideon vetoed, say so.

If asked for multiple tickers, rank GO first, then NEAR-MISS by descending
asymmetry score, then PASS one-per-line.

## Step 6  Close honestly

End with the single weakest part of the read  the assumption most likely to be
wrong, or the data point you had to infer. Not a disclaimer; an honest flag on
where the verdict is most fragile. If you are confident throughout, say so and
say why.

## Principles

- **Generative, not retrieval.** If the answer is "go look at the cached tiers,"
  you are in the wrong skill  hand off to `council`.
- **Gideon can always veto.** No score or R:R overrides a hard downside.
- **Never fabricate market data.** Inferred numbers are labeled inferred.
- **Disagreement is signal.** A 4-3 split is more honest than a manufactured 7-0.
- **The thesis is one line.** If it takes a paragraph, the trade isn't clear yet.

## Edge cases

- **No ticker given**  ask which instrument/setup before convening. Do not run
  the council on nothing.
- **No entry/stop/target**  you cannot compute R:R; cap the best possible
  verdict at NEAR-MISS and state that the gate could not be evaluated.
- **Inside apex-ultra repo with live tiers already written**  offer the cached
  `council` view first; only deliberate fresh if the user wants a new read.
- **Not a trade at all** (e.g. a strategy or product decision)  the seven
  voices still work as a structured adversarial panel, but say you are using the
  Council as a general decision framework, not a trade verdict.
