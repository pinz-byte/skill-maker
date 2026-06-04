# Intel Contract - carmatch-intel <-> getIntel

The single source of truth for the JSON shape `getIntel` emits and `carmatch-intel`
parses. If you change a key or a threshold here, change it in BOTH the Cloud Function
(`deploy/getIntel.js`) and the skill body. Drift between the two is the #1 way this breaks.

## Endpoint

```
GET https://<region>-carmatch-ai-v0.cloudfunctions.net/getIntel
Header: X-Intel-Key: <shared secret>
```

Returns `200` with the JSON below, or `401` if the key is missing/wrong, or `503`
if the precomputed `ops_snapshot` doc is missing (coverage/anomaly unavailable, but
live sections still return).

## Response shape

```json
{
  "generatedAt": "2026-05-29T14:03:00Z",
  "status": "AMBER",
  "sources": [
    {
      "id": "neoauto",
      "lastRunAt": "2026-05-29T09:00:00Z",
      "ageHours": 5.1,
      "expectedIntervalHours": 24,
      "freshness": "GREEN",
      "lastRun": {
        "listingsFetched": 1240,
        "parsed": 1198,
        "parseRate": 0.966,
        "errors": 3,
        "health": "GREEN"
      }
    }
  ],
  "coverage": {
    "asOf": "2026-05-29T04:10:00Z",
    "totalKeys": 5821,
    "thinKeys": 412,
    "thinPct": 0.071,
    "staleKeys": 230,
    "stalePct": 0.040,
    "status": "GREEN"
  },
  "anomalies": [
    {
      "key": "TOYOTA_COROLLA_2020",
      "type": "price_jump",
      "detail": "avgPrice +18.3% vs prior snapshot",
      "severity": "AMBER"
    }
  ],
  "volume": {
    "ingestedToday": 3140,
    "trailingAvg": 3620,
    "deltaPct": -0.133,
    "status": "AMBER"
  },
  "meta": {
    "snapshotAgeHours": 9.9,
    "endpointVersion": "1.0.0",
    "degraded": false
  }
}
```

## Threshold rules (the rubric - tunable defaults, calibrate against real data)

These are DEFAULTS, not gospel. They are first-pass guesses; recalibrate once you see
real distributions. Every color in the payload is computed server-side from these so
the skill never recomputes - it only renders.

| Section | GREEN | AMBER | RED |
|---|---|---|---|
| freshness | age <= interval | age <= 1.5x interval | age > 1.5x interval, or never ran |
| extraction health | parseRate >= 0.95 | 0.80 <= parseRate < 0.95 | parseRate < 0.80, run failed, or 0 fetched |
| coverage | stalePct < 0.10 AND thinPct < 0.15 | either threshold crossed | stalePct > 0.30 |
| volume | within +/-20% of trailingAvg | +/-20% to +/-40% | beyond +/-40% (esp. negative) |

Anomaly severity (per row, computed in the snapshot writer):
- price_jump / price_drop: |delta| > 15% => AMBER, > 30% => RED
- count_collapse: count dropped > 50% vs prior snapshot => RED
- spread_implausible: maxPrice / minPrice > 5 => AMBER

## Overall status rollup

`status` (top level) = worst of: every source freshness, every source health,
coverage.status, volume.status, and the highest anomaly severity present.
Worst-of ordering: RED > AMBER > GREEN. This is the single value the operator reads first.

## Source interval expectations

- `scrapeRetailers`: scheduled daily 04:00 UTC -> expectedIntervalHours = 24
- `neoauto`, `vmc` (Pub/Sub -> onExtractorData): event-driven. Default expectedIntervalHours = 24;
  override per source in the `SOURCE_INTERVALS` map in getIntel.js if a source is meant to fire more often.

## Live vs precomputed (read-cost discipline)

- LIVE on every call (cheap, bounded `scrape_runs` queries): `sources[]`, `volume`.
- PRECOMPUTED, read from `ops_snapshot/current` doc: `coverage`, `anomalies`.
  Recomputing coverage/anomaly means scanning the whole `comparables` collection;
  doing that on every operator pull is a read-cost and latency trap. The snapshot
  writer runs after each `scrapeRetailers` cycle and writes one doc. getIntel reads it O(1).
- If `ops_snapshot/current` is missing or older than 26h, `meta.degraded = true` and the
  skill must say so out loud - never present stale coverage as live.
