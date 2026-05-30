/**
 * opsSnapshot — precomputes the expensive parts of the intel snapshot (coverage + anomalies)
 * by scanning `comparables` ONCE per cycle and writing a single ops_snapshot/current doc.
 *
 * Add to the functions-sync codebase alongside getIntel.js.
 * getIntel reads the doc it writes in O(1), so an operator pull never scans comparables.
 *
 * Schedule: run it just after scrapeRetailers (daily 04:00 UTC) so coverage reflects the
 * latest ingestion. 04:30 UTC is a safe default. Adjust if scrapeRetailers runs longer.
 *
 * It also diffs against the PREVIOUS snapshot to detect price jumps/drops and count
 * collapses — which is why it keeps the prior avgPrice/count per key in `ops_snapshot/prev`.
 *
 * SCHEMA — comparables doc (from source-scout, confirmed):
 *   { avgPrice, minPrice, maxPrice, count, sources[], updatedAt }
 *   key = {BRAND}_{MODEL}_{YEAR}
 */

const { onSchedule } = require("firebase-functions/v2/scheduler");
const admin = require("firebase-admin");

if (!admin.apps.length) admin.initializeApp();
const db = admin.firestore();

const T = {
  thinCount: 3,                // count < 3 = statistically thin
  staleHours: 24 * 7,          // updatedAt older than 7 days = stale
  covStaleAmber: 0.10,
  covThinAmber: 0.15,
  covStaleRed: 0.30,
  priceMoveAmber: 0.15,
  priceMoveRed: 0.30,
  countCollapseRed: 0.50,      // count dropped > 50% vs prior
  spreadAmber: 5,              // maxPrice/minPrice > 5
  maxAnomalies: 50,            // cap the array; rank worst first
};

function coverageStatus(stalePct, thinPct) {
  if (stalePct > T.covStaleRed) return "RED";
  if (stalePct > T.covStaleAmber || thinPct > T.covThinAmber) return "AMBER";
  return "GREEN";
}

const SEV_RANK = { AMBER: 1, RED: 2 };

exports.opsSnapshot = onSchedule(
  { schedule: "30 4 * * *", timeZone: "UTC", memory: "512MiB", timeoutSeconds: 540 },
  async () => {
    const prevDoc = await db.collection("ops_snapshot").doc("prev").get();
    const prev = prevDoc.exists ? prevDoc.data().keyStats || {} : {};

    const now = Date.now();
    const staleCutoff = now - T.staleHours * 36e5;

    let totalKeys = 0, thinKeys = 0, staleKeys = 0;
    const anomalies = [];
    const keyStats = {}; // key -> { avgPrice, count } for next cycle's diff

    // Single full scan, streamed. This is the ONE expensive read, amortized once per day.
    const snap = await db.collection("comparables").get();
    snap.forEach((doc) => {
      const c = doc.data();
      const key = doc.id;
      totalKeys++;

      const count = c.count || 0;
      if (count < T.thinCount) thinKeys++;

      const updatedMs = c.updatedAt && c.updatedAt.toDate ? c.updatedAt.toDate().getTime() : 0;
      if (updatedMs < staleCutoff) staleKeys++;

      keyStats[key] = { avgPrice: c.avgPrice || 0, count };

      // Anomaly diffing vs prior snapshot
      const p = prev[key];
      if (p) {
        if (p.avgPrice > 0 && c.avgPrice > 0) {
          const move = (c.avgPrice - p.avgPrice) / p.avgPrice;
          const mag = Math.abs(move);
          if (mag > T.priceMoveAmber) {
            anomalies.push({
              key,
              type: move > 0 ? "price_jump" : "price_drop",
              detail: `avgPrice ${move > 0 ? "+" : ""}${(move * 100).toFixed(1)}% vs prior snapshot`,
              severity: mag > T.priceMoveRed ? "RED" : "AMBER",
            });
          }
        }
        if (p.count > 0 && (p.count - count) / p.count > T.countCollapseRed) {
          anomalies.push({
            key, type: "count_collapse",
            detail: `count ${p.count} -> ${count} (source may have died)`,
            severity: "RED",
          });
        }
      }
      if (c.minPrice > 0 && c.maxPrice / c.minPrice > T.spreadAmber) {
        anomalies.push({
          key, type: "spread_implausible",
          detail: `max/min = ${(c.maxPrice / c.minPrice).toFixed(1)}x`,
          severity: "AMBER",
        });
      }
    });

    anomalies.sort((a, b) => (SEV_RANK[b.severity] || 0) - (SEV_RANK[a.severity] || 0));
    const topAnomalies = anomalies.slice(0, T.maxAnomalies);

    const thinPct = totalKeys ? +(thinKeys / totalKeys).toFixed(3) : 0;
    const stalePct = totalKeys ? +(staleKeys / totalKeys).toFixed(3) : 0;

    const asOf = admin.firestore.Timestamp.now();
    const coverage = {
      asOf: asOf.toDate().toISOString(),
      totalKeys, thinKeys, thinPct, staleKeys, stalePct,
      status: coverageStatus(stalePct, thinPct),
    };

    // Roll prev <- current keyStats for next cycle, then write current.
    await db.collection("ops_snapshot").doc("prev").set({ keyStats, asOf });
    await db.collection("ops_snapshot").doc("current").set({
      asOf,
      coverage,
      anomalies: topAnomalies,
    });

    console.log(`opsSnapshot: ${totalKeys} keys, ${topAnomalies.length} anomalies, coverage ${coverage.status}`);
  }
);
