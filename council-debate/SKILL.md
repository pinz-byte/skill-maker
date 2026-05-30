---
name: council-debate
description: >
  Fire the APEX MASTERS Council on ONE ticker, on demand, on M1 — the center
  evaluator. Trigger on "/debate <ticker>", "debate NVDA", "council on
  <ticker>", "fire the council on X", "evaluate <ticker>", "council verdict on
  X", "run the council for <ticker>", or any request for a fresh single-asset
  verdict produced locally. Runs the real 7-voice council (Elliott, Hannah,
  Marco, Theodore, Iris, Felix, Gideon) via apex-ultra's council_oneshot runner:
  fetches a live Schwab quote, calls council_decide, scores asymmetry, and
  classifies GO / NEAR-MISS / PASS with the 2:1 R:R floor and Gideon override.
  Market open + fresh quote -> LIVE verdict; closed or no quote -> OUTLOOK
  (non-executable). NOT a cached-tier display (use council / council-global).
  Requires the apex-ultra repo + secrets .env + python3.13 on local disk: M1
  only. One Anthropic call per run. Prints a verdict; never places an order.
---

# Council Debate — on-demand single-ticker evaluator (M1)

The center. Convenes the real 7-voice APEX MASTERS Council on one ticker and
prints a full verdict. This is the executor the `council-call` front door and
the queue watcher both ultimately invoke.

## How to run

One command — present its output verbatim (it is already formatted):

```
cd /Users/usuario/Documents/Claude/Projects/apex-ultra
/opt/homebrew/bin/python3.13 tools/council_oneshot.py <TICKER>
```

Flags:
- `--outlook` — force OUTLOOK mode (non-executable; use when the user wants a
  read off-hours and accepts no live price anchor).
- `--json` — machine-readable output (for the watcher / queue result, not for humans).

## What it does (reuses existing code, rebuilds nothing)

`council_oneshot.py` wires together the pieces already in the repo:
- live Schwab quote + freshness check (`council_loop._schwab_quote_fn` / `_fetch_live_quote`)
- market status (`council_loop.market_status`)
- the 7-voice council (`council_decide.council_decide`)
- scoring + tiering (`council_decide.asymmetry_score` / `classify_tier`)

It prints: VERDICT tier (GO / NEAR-MISS / PASS), the 0-100 asymmetry score,
ACTION / QTY / ENTRY / STOP / targets / confidence, R:R to Target 1 against the
hard 2.0:1 GO floor, the Gideon-override flag, the per-voice votes, the score
components, and the full debate transcript.

## LIVE vs OUTLOOK

- Market open AND a fresh Schwab quote -> `strict=True` -> LIVE executable verdict.
- Market closed, no fresh quote, or `--outlook` -> `strict=False` -> OUTLOOK:
  directional thinking with NO live price anchor. Label it NON-EXECUTABLE; it is
  never an order. (On-demand deviation from the loop: the loop SKIPS a ticker
  with no live quote on an open day; this runner instead produces a labeled
  OUTLOOK so an explicit user request is never silently dropped.)

## Safety boundary (hard)

Prints a verdict. Does not place, file, queue, or size an order into the broker.
A printed GO is a recommendation for the human, not an instruction to any
trading process. Never wire this output into an auto-filing path.

## Hard requirements and limits

- **python3.13** (`/opt/homebrew/bin/python3.13`). Apple 3.9 fails on PEP 604.
- **apex-ultra repo + `~/secrets/apex-desk-v3/.env` (Anthropic + Schwab) on local disk.**
  M1 only. Not M2/M3 (no secrets), not Chat (no shell/python/filesystem).
- **One Anthropic call per invocation** (~$0.10 Sonnet). On-demand only; never loop it.
- Full transcript is also saved by council_decide to `logs/council_transcripts/<TICKER>_*.txt`.

## Relationship to the other council skills

- `council-debate` (this) — fire the council on one ticker, live, on M1.
- `council-call` — portable front door: runs this on M1, else queues to Notion for the watcher.
- `council-global` — read today's cached tiers for all tickers (read-only).
- `apex-ultra-council` — files-free 7-voice reasoning when no pipeline is reachable (Chat); label non-live.
