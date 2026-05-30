/**
 * getIntel — read-only operator intel endpoint for the CarMatch / AVT Extractor pipeline.
 *
 * Add to the functions-sync codebase. Deploy: firebase deploy --only functions:sync
 *
 * Returns the RED/AMBER/GREEN snapshot defined in references/intel-contract.md.
 * Live sections (sources, volume) are computed from bounded scrape_runs queries.
 * Coverage + anomalies are read O(1) from the precomputed ops_snapshot/current doc
 * (written by opsSnapshot.js) so we never full-scan `comparables` on an operator pull.
 *
 * SCHEMA ASSUMPTIONS — VERIFY AGAINST THE REAL scrape_runs COLLECTION BEFORE DEPLOY.
 * This code assumes each scrape_runs doc looks like:
 *   {
 *     source: "neoauto",            // string id
 *     finishedAt: Timestamp,        // when the run completed
 *     status: "ok" | "error",       // run outcome
 *     fetched: 1240,                // listings fetched
 *     parsed: 1198,                 // successfully parsed
 *     errors: 3                     // parse/transport errors
 *   }
 * If the real field names differ (e.g. `ts`, `count`, `ok`), adjust the read paths
 * marked `// ASSUMPTION` below. Do not deploy until these match reality.
 */

const { onRequest } = require("firebase-functions/v2/https");
const { defineSecret } = require("firebase-functions/params");
const admin = require("firebase-admin");

if (!admin.apps.length) admin.initializeApp();
const db = admin.firestore();

// Shared secret. Set with: firebase functions:secrets:set INTEL_KEY
const INTEL_KEY = defineSecret("INTEL_KEY");

// Sources to report on, with how often each is expected to run (hours).
// Override here when a source is meant to fire more/less often than daily.
const SOURCE_INTERVALS = {
  neoauto: 24,
  vmc: 24,
  scrapeRetailers: 24,
};

// Thresholds — keep in lockstep with references/intel-contract.md.
const T = {
  freshnessAmberMult: 1.5,     // age <= interval*1.5 = AMBER, beyond = RED
  healthGreen: 0.95,
  healthAmber: 0.80,
  covStaleAmber: 0.10,
  covThinAmber: 0.15,
  covStaleRed: 0.30,
  volGreenBand: 0.20,          // within +/-20% = GREEN
  volAmberBand: 0.40,          // within +/-40% = AMBER, beyond = RED
  snapshotMaxAgeHours: 26,     // older snapshot => degraded
};

const RANK = { GREEN: 0, AMBER: 1, RED: 2 };
const worst = (a, b) => (RANK[b] > RANK[a] ? b : a);

function hoursSince(ts) {
  if (!ts) return null;
  const d = ts.toDate ? ts.toDate() : new Date(ts);
  return (Date.now() - d.getTime()) / 36e5;
}

function freshnessColor(ageHours, intervalHours) {
  if (ageHours == null) return "RED";                       // never ran
  if (ageHours <= intervalHours) return "GREEN";
  if (ageHours <= intervalHours * T.freshnessAmberMult) return "AMBER";
  return "RED";
}

function healthColor(run) {
  if (!run || run.status === "error" || !run.fetched) return "RED";
  const rate = run.parsed / run.fetched;
  if (rate >= T.healthGreen) return "GREEN";
  if (rate >= T.healthAmber) return "AMBER";
  return "RED";
}

function volumeColor(deltaPct) {
  const a = Math.abs(deltaPct);
  if (a <= T.volGreenBand) return "GREEN";
  if (a <= T.volAmberBand) return "AMBER";
  return "RED";
}

/** Last run per source: one ordered+limited query each (cheap, indexed on source+finishedAt). */
async function loadSources() {
  const out = [];
  let overall = "GREEN";
  for (const [id, intervalHours] of Object.entries(SOURCE_INTERVALS)) {
    // ASSUMPTION: collection "scrape_runs", fields "source" + "finishedAt".
    const snap = await db
      .collection("scrape_runs")
      .where("source", "==", id)
      .orderBy("finishedAt", "desc")
      .limit(1)
      .get();

    if (snap.empty) {
      out.push({
        id, lastRunAt: null, ageHours: null, expectedIntervalHours: intervalHours,
        freshness: "RED",
        lastRun: { listingsFetched: 0, parsed: 0, parseRate: 0, errors: 0, health: "RED" },
      });
      overall = worst(overall, "RED");
      continue;
    }

    const r = snap.docs[0].data();
    const ageHours = hoursSince(r.finishedAt);
    const freshness = freshnessColor(ageHours, intervalHours);
    const health = healthColor(r);
    const fetched = r.fetched || 0;
    const parsed = r.parsed || 0;

    out.push({
      id,
      lastRunAt: r.finishedAt ? r.finishedAt.toDate().toISOString() : null,
      ageHours: ageHours != null ? +ageHours.toFixed(1) : null,
      expectedIntervalHours: intervalHours,
      freshness,
      lastRun: {
        listingsFetched: fetched,
        parsed,
        parseRate: fetched ? +(parsed / fetched).toFixed(3) : 0,
        errors: r.errors || 0,
        health,
      },
    });
    overall = worst(overall, worst(freshness, health));
  }
  return { sources: out, overall };
}

/** Volume today vs trailing average, summed from scrape_runs over a bounded window. */
async function loadVolume() {
  const now = new Date();
  const startToday = new Date(now); startToday.setUTCHours(0, 0, 0, 0);
  const windowStart = new Date(startToday.getTime() - 7 * 864e5); // trailing 7 days

  // ASSUMPTION: "parsed" is the per-run ingested count; sum it per day.
  const snap = await db
    .collection("scrape_runs")
    .where("finishedAt", ">=", admin.firestore.Timestamp.fromDate(windowStart))
    .get();

  let today = 0;
  const perDay = {};
  snap.forEach((doc) => {
    const r = doc.data();
    const d = r.finishedAt.toDate();
    const key = d.toISOString().slice(0, 10);
    const n = r.parsed || 0;
    if (d >= startToday) today += n;
    else perDay[key] = (perDay[key] || 0) + n;
  });

  const days = Object.values(perDay);
  const trailingAvg = days.length ? Math.round(days.reduce((a, b) => a + b, 0) / days.length) : 0;
  const deltaPct = trailingAvg ? +((today - trailingAvg) / trailingAvg).toFixed(3) : 0;

  return {
    ingestedToday: today,
    trailingAvg,
    deltaPct,
    status: trailingAvg ? volumeColor(deltaPct) : "GREEN",
  };
}

/** Coverage + anomalies: read the precomputed snapshot. O(1). */
async function loadSnapshot() {
  const doc = await db.collection("ops_snapshot").doc("current").get();
  if (!doc.exists) {
    return { degraded: true, snapshotAgeHours: null, coverage: null, anomalies: [] };
  }
  const s = doc.data();
  const ageHours = hoursSince(s.asOf);
  const degraded = ageHours == null || ageHours > T.snapshotMaxAgeHours;
  return {
    degraded,
    snapshotAgeHours: ageHours != null ? +ageHours.toFixed(1) : null,
    coverage: s.coverage || null,   // { asOf, totalKeys, thinKeys, thinPct, staleKeys, stalePct, status }
    anomalies: s.anomalies || [],   // [{ key, type, detail, severity }]
  };
}

exports.getIntel = onRequest({ secrets: [INTEL_KEY], cors: false }, async (req, res) => {
  if (req.get("X-Intel-Key") !== INTEL_KEY.value()) {
    return res.status(401).json({ error: "unauthorized" });
  }
  try {
    const [{ sources, overall: liveOverall }, volume, snap] = await Promise.all([
      loadSources(), loadVolume(), loadSnapshot(),
    ]);

    let overall = liveOverall;
    overall = worst(overall, volume.status);
    if (snap.coverage) overall = worst(overall, snap.coverage.status);
    for (const a of snap.anomalies) overall = worst(overall, a.severity);

    const payload = {
      generatedAt: new Date().toISOString(),
      status: overall,
      sources,
      coverage: snap.coverage,
      anomalies: snap.anomalies,
      volume,
      meta: {
        snapshotAgeHours: snap.snapshotAgeHours,
        endpointVersion: "1.0.0",
        degraded: snap.degraded,
      },
    };

    const code = snap.degraded ? 503 : 200; // 503 still carries live sections; skill handles it
    return res.status(code).json(payload);
  } catch (err) {
    console.error("getIntel failed", err);
    return res.status(500).json({ error: "intel_compute_failed", detail: String(err) });
  }
});
