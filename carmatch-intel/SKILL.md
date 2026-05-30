---
name: carmatch-intel
description: >
  On-demand operator intel for the CarMatch / AVT Extractor pipeline. Pulls a live
  RED/AMBER/GREEN snapshot of pipeline freshness, extraction health, comparables
  coverage, anomalies, and ingestion volume from the getIntel Cloud Function, and
  renders it ranked by what an intraday operator must act on first. Use this skill
  whenever the user says "intel", "pull intel", "pipeline status", "extractor status",
  "carmatch status", "how's the pipeline", "are the scrapers running", "is the data
  fresh", "what's stale", "coverage report", "any anomalies", "ops snapshot", "what's
  broken", or asks what the comparables data looks like right now. Also trigger on
  "is anything dead", "did the scrape run", "show me the numbers", or any request to
  surface the current operational state of the extractor/comparables pipeline. This
  is a READ-ONLY status pull - it never writes or deploys.
---

# CarMatch Intel - On-Demand Pipeline Snapshot

Surfaces the operational state of the CarMatch / AVT Extractor pipeline in one call,
ranked by decision-value. Built for an intraday operator whose first question is always
"what do I need to act on right now?" Answers that in a single RED/AMBER/GREEN read.

This skill is a THIN CLIENT. It carries no data and computes no colors - it calls the
`getIntel` Cloud Function, which does the aggregation server-side, and renders the result.
The exact JSON shape and every threshold live in `references/intel-contract.md`. Read that
file if anything about the payload is unclear; never invent fields or recompute statuses.

## What it returns, ranked

1. **Pipeline freshness, per source** - last successful run, age, stale flag. Top of the
   list because a silently dead source poisons every downstream price and is invisible
   otherwise. `scrapeRetailers` runs daily 04:00 UTC; neoauto/vmc are event-driven.
2. **Extraction health, last run per source** - listings fetched, parse rate, errors.
3. **Comparables coverage** - total keys, thin keys (count < 3, statistically unreliable),
   stale keys. Read from the precomputed `ops_snapshot` doc.
4. **Anomaly flags** - price jumps/drops, count collapses (a source died mid-pipeline),
   implausible spreads. From the same snapshot.
5. **Volume** - ingested today vs trailing average.

## How to run it

### Step 1 - get the endpoint + key

The function URL and the `X-Intel-Key` secret are configured per environment. Resolve them
in this order:
1. Environment variables `CARMATCH_INTEL_URL` and `CARMATCH_INTEL_KEY` if set in the session.
2. Otherwise ask the user once and offer to save them as a data-capsule for next time.

Never hardcode the key in any committed file.

### Step 2 - call the endpoint

```bash
curl -sS -H "X-Intel-Key: $CARMATCH_INTEL_KEY" "$CARMATCH_INTEL_URL/getIntel"
```

- `200` -> parse and render (Step 3).
- `401` -> the key is wrong or missing. Say so plainly; do not retry blindly.
- `503` or `meta.degraded == true` -> live sections are valid but coverage/anomaly are
  stale or unavailable. Render what is live and state explicitly that coverage is degraded
  and how old the snapshot is. NEVER present a stale snapshot as current.
- Network failure / unreachable -> report it as unreachable. Do not fall back to guessing
  numbers or scraping Firestore by other means.

### Step 3 - render the snapshot

Lead with the overall `status` and a one-line headline naming the single most urgent item.
Then a compact table per section. Use the colors exactly as returned - do not recompute.

```
PIPELINE INTEL - <generatedAt>     OVERALL: <status>
Headline: <the worst thing, in one line>

FRESHNESS
  source        last run      age      state
  neoauto       09:00 UTC     5.1h     GREEN
  scrapeRetail  yesterday     27.4h    RED   <- overdue, expected every 24h

EXTRACTION (last run)
  source        fetched  parsed  rate    state
  neoauto       1240     1198    96.6%   GREEN

COVERAGE (as of <asOf>, snapshot age <snapshotAgeHours>h)
  total keys 5821 | thin (<3) 412 (7.1%) | stale 230 (4.0%)   GREEN

ANOMALIES
  TOYOTA_COROLLA_2020   price_jump   +18.3%   AMBER
  (or: none)

VOLUME
  today 3140 vs trailing avg 3620   -13.3%   AMBER
```

Keep it dense. The operator is scanning, not reading. If `status` is GREEN across the
board, say so in one line and stop - do not pad.

## Principles

- **Read-only, always.** This skill never writes Firestore, never deploys, never mutates.
  If the user wants to fix something it surfaced, that is a separate action they trigger.
- **Honesty about staleness beats completeness.** A degraded coverage section flagged as
  degraded is useful. A stale one presented as live is a trap. Always state snapshot age.
- **Never recompute colors client-side.** The rubric lives server-side so the skill and a
  future dashboard agree. If a color looks wrong, the fix is in getIntel.js, not here.
- **One call per pull.** Do not poll in a loop. The operator invokes; the skill answers once.
- **No silent fallbacks.** If the endpoint is unreachable, say so. Reaching Firestore by
  CLI/creds in the sandbox is exactly the fragile path this design rejected.

## Edge cases

- **A source has never run:** `lastRunAt` is null, freshness is RED, render "never ran".
- **Empty anomalies array:** render "none" - do not omit the section (its absence is signal).
- **New source not in SOURCE_INTERVALS:** getIntel defaults its interval to 24h; if freshness
  looks wrong for a fast source, the fix is to add it to the map in getIntel.js.
- **Key not configured:** ask for it, offer to capsule it; do not proceed with a blank header.
