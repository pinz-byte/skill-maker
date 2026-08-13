---
name: council-run
description: Run an on-demand APEX 4-voice live-money Council deliberation on a ticker  from the book, a watchlist, or brand new  RIGHT NOW, intraday. Pulls the live Schwab book + quote FIRST (Book-Reconciliation Gate), then deliberates and returns a full verdict. Trigger on "run the council", "council this", "ask the council about X", "council review TICKER", "what does the council think about TICKER", "deliberate on TICKER", "convene the council", "council my book", "run council on my positions", or any request for a fresh Council opinion on a specific ticker intraday. This is NOT the read-only board  for "show me the current verdicts" use /council. This skill DELIBERATES anew; /council DISPLAYS the premarket board. If the user wants a fresh take on a live ticker, this is the one.
metadata:
  intent: decide
---

# Council Run  on-demand 4-voice live deliberation

Runs the APEX **4-voice live-money Council** (Wave Analyst / Risk Officer / Execution Desk / Desk Lead) on demand, intraday, against a freshly reconciled book. This is the live-money path  distinct from the 7-voice MASTERS engine (paper, premarket-automatic) that `/council` displays.

Authority: ratified Council On-Demand Amendment (2026-05-29). Governing rule: every on-demand run reconciles the live book + quote BEFORE deliberating  no run off a stale snapshot, ever.

## When to use which

- **This skill (`council-run`)**  "deliberate now" on a specific ticker or the whole book. Makes live API calls. Produces a fresh verdict.
- **`/council`**  read-only display of the premarket MASTERS tier board. No deliberation, no cost.

## The protocol (do not skip steps)

### Step 1  Resolve the target
- One ticker (e.g. "council this NVDA")  single deliberation.
- "my book" / "my positions"  full-book mode (loop over held positions).
- A ticker not in the book/watchlist  still valid; it deliberates as a NEW-ENTRY candidate.

### Step 2  RECONCILE FIRST (the gate  mandatory, non-negotiable)
Before any deliberation, pull live data. Preferred path is the CLI once APEX_12 Slice 1 ships:

```
cd <apex-ultra repo>
python council.py TICKER --live          # single ticker, live-reconciled
python council.py --book --yes           # full book, one pull, N deliberations
```

If the `--live` flag is not yet built (APEX_12 unshipped), run the reconciliation inline using the existing Schwab client, then deliberate in-chat with the SAME 4-voice contract below:
- Pull `SchwabClient().get_positions()` and `get_quote(TICKER)`.
  - **Held**  reconcile real qty, avg cost, current mark, (option strike/expiry).
  - **Not held**  mark `NOT HELD / size 0`, still pull the live quote, deliberate as new-entry.
- **If the book or quote pull fails  ABORT.** Say so plainly. Do NOT fall back to /tmp/apex-ultra-snapshot.json or any reference doc. (This is the whole point of the gate.)

Sandbox note: the Schwab client reads `~/secrets/apex-desk-v3/.env`; in the Linux sandbox symlink the mounted `.env` into `$HOME/secrets/apex-desk-v3/.env` first, and import `apex_memory.brokers.schwab` directly (stub the package roots) to avoid the psycopg2/pinecone import chain. See memory [[tos-position-primitive]].

### Step 3  Lead with the time-state line
```
Lima HH:MM | ET HH:MM | Market state | book pulled @ <ISO ts>
```

### Step 4  Deliberate with the EXACT 4-voice contract
Use council.py's system prompt verbatim so chat and CLI never diverge. Voices and output:

```
[A - WAVE ANALYST]    Elliott Wave / technical structure, levels
[B - RISK OFFICER]    sizing, stop discipline, concentration, drawdown
[C - EXECUTION DESK]  entry timing, order type, urgency, slippage
[D - DESK LEAD]       synthesis + final call

RECOMMENDATION: BUY / ADD / HOLD / REDUCE / AVOID / WAIT
CONVICTION: HIGH / MEDIUM / LOW
ACTION: <one specific actionable sentence>
```
Rules: never fabricate prices  use only the reconciled live data. If a field is unavailable, say so rather than infer. Be direct.

### Step 5  Cost discipline (full-book mode)
Before a `--book` run, state the position count and that each is a live API call; on a large book (>8 names) confirm before proceeding. This skill is deliberate-invocation only  never wire it to auto-fire from a loop.

## Hard boundaries
- Trust Tier 1 (read) only. Never place, modify, or cancel an order. POPs pulls every trigger.
- This does NOT change the premarket primitive (MASTERS 7-voice) or auto-fire intraday.
- No order placement, no Schwab writes, anywhere in this path.

## Related
- Rule: `APEX_OPERATING_PRIMITIVE_council_on_demand_2026-05-29.md`
- Gate: `APEX_OPERATING_PRIMITIVE_book_reconciliation_gate_2026-05-29.md`
- Build: `APEX_12_COUNCIL_ON_DEMAND_BUILDER_BRIEF_2026-05-29.md`
- Display sibling: the `council` skill (`/council`)
