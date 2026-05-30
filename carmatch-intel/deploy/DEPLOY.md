# Deploy notes — getIntel + opsSnapshot

These two functions are the data pipe for the `carmatch-intel` skill. They ship from the
`carmatch-ai` repo (functions-sync codebase), NOT from SKILL MAKER. This session can write
the code but cannot deploy it.

## 0. Before you deploy — VERIFY THE scrape_runs SCHEMA

`getIntel.js` assumes scrape_runs docs look like:
`{ source, finishedAt (Timestamp), status: "ok"|"error", fetched, parsed, errors }`.

Open one real scrape_runs doc and confirm the field names. If they differ, fix the read
paths marked `// ASSUMPTION` in getIntel.js and the `parsed` sum in loadVolume(). Do not
deploy on the assumed schema — wrong field names return zeros that look like a dead pipeline.

## 1. Drop the files in

Copy `getIntel.js` and `opsSnapshot.js` into the `functions-sync/` directory and export them
from `functions-sync/index.js`:

```js
exports.getIntel = require("./getIntel").getIntel;
exports.opsSnapshot = require("./opsSnapshot").opsSnapshot;
```

Confirm `firebase-functions` v2 and `firebase-admin` are in functions-sync/package.json
(they should be — processSignal/signalCounter already use them).

## 2. Set the shared secret

```bash
firebase functions:secrets:set INTEL_KEY
# paste a long random string when prompted; this is the X-Intel-Key the skill sends
```

## 3. Deploy (functions-sync only — never all codebases casually)

```bash
cd functions-sync && npm install && cd .. && firebase deploy --only functions:sync
```

## 4. Seed the snapshot

`opsSnapshot` is scheduled daily 04:30 UTC. On first deploy there is no snapshot yet, so
getIntel returns `meta.degraded:true` until the first run. Either wait for 04:30 UTC or
trigger it once manually from the Functions console / `gcloud scheduler jobs run`.

## 5. Wire the skill

Give the skill its two values in the CarMatch session (env vars or a data-capsule):
- `CARMATCH_INTEL_URL` = the deployed function base URL
  (e.g. `https://us-central1-carmatch-ai-v0.cloudfunctions.net`)
- `CARMATCH_INTEL_KEY` = the INTEL_KEY secret value

Test:
```bash
curl -sS -H "X-Intel-Key: $CARMATCH_INTEL_KEY" "$CARMATCH_INTEL_URL/getIntel" | jq .
```

## Known limits / scaling caveats (read before this grows)

1. **prev-snapshot 1 MiB doc limit.** opsSnapshot stores per-key stats for anomaly diffing
   in a single `ops_snapshot/prev` doc. At ~5.8k keys (~175 KB) this is fine. Past ~25-30k
   keys you will hit Firestore's 1 MiB per-doc limit. Fix when you get there: shard keyStats
   across a subcollection, or move diffing to a BigQuery export.
2. **Full comparables scan cost.** opsSnapshot reads the entire comparables collection once
   per day. At 5.8k docs this is trivial. If it reaches hundreds of thousands, switch to a
   BigQuery scheduled query or incremental aggregation in onExtractorData.
3. **Auth is a shared static key.** Fine for an internal ops endpoint. If this ever fronts
   anything sensitive or public, move to a Firebase callable with App Check or IAM.
4. **Thresholds are first-pass guesses.** Every color in intel-contract.md is a default.
   Watch a week of real output and recalibrate before trusting RED/AMBER as alarms.
