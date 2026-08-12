---
name: herald-config-doctor
description: >-
  Remediation skill for HERALD config drift. This skill closes the loop: reads the latest
  monitor report, applies the known mechanical fixes (decommissioned Cloud Run URL, rotated
  API key, unmounted output path), self-heals the monitor's SKILL.md, re-runs to confirm
  clean. Use on "fix herald config", "herald is noisy again", "silence the herald findings",
  "herald config drift", "patch the monitor", "herald keeps reporting the same thing", or "why
  does the health monitor keep flagging that". Also trigger after any herald-health-monitor or
  herald-accuracy-audit run reporting repeat/pending findings, and whenever the report shows a
  403 (dead URL), 401 (rotated key), or unmounted-path write error. Fire on "herald's
  complaining again" or "make the herald noise stop". NOT machine-bridge (sandbox-to-machine
  handoff) or gcp-iam-resolver (cloud IAM).
metadata:
  intent: diagnose
---

# Herald Config Doctor

The herald-health-monitor runs on a schedule and only DETECTS problems. It has reported
the same three mechanical config issues for multiple consecutive runs with no fix applied.
Every repeat run wastes a cycle and, worse, the known noise can mask a genuine regression
(e.g. a webhook delivery drop) sitting underneath. This skill is the remediation half the
monitor never had: detect-then-fix, then confirm clean.

## The Three Known Findings (the recurring noise)

These are the items the monitor re-reports every run. Each has a one-time mechanical fix.

1. **Decommissioned Cloud Run URL (403 IAM-blocked).** The monitor's SKILL.md / config
   still points at an old Cloud Run service URL that has been decommissioned and now
   returns 403. The live endpoint is the custom domain `https://feed.vmcsubastas.com`.
   Fix: replace the dead URL with the current endpoint everywhere it appears.

2. **Rotated API key (401).** The stored registration key / token has been rotated; the
   old value returns 401. Fix: re-point config at the current key source (Secret Manager
   or the project `.env`), never paste a literal key into SKILL.md.

3. **Unmounted output path.** The monitor writes its report to a path that is not mounted
   in the current environment. Fix: write to the project's actual Scheduled report path
   (`~/Documents/Claude/Projects/herald vmc feed/Scheduled/herald-health-monitor/`), or a
   path that resolves in both sandbox and machine — see [[machine-bridge]] for the
   path-divergence rules.

## Procedure

### Step 1 — Read the live report, do not assume values

Open the latest monitor report and confirm which of the three findings are currently
firing and what the current correct values are. Never hardcode a URL or key from memory;
pull the live value.

```bash
cat "$HOME/Documents/Claude/Projects/herald vmc feed/Scheduled/herald-health-monitor/latest-report.md"
```

Verify the live endpoint actually answers before writing it into config:

```bash
curl -s -o /dev/null -w "%{http_code}" https://feed.vmcsubastas.com/herald/v1/health
```

### Step 2 — Separate noise from signal

The monitor report mixes the three known mechanical findings with potentially real
regressions (webhook freshness, `last_ingest_at` drift, `consecutive_failures`, delivery
queue depth). Before silencing anything, list which findings are the known three and which
are NOT. The known three get fixed mechanically. Anything else is a genuine finding and
must be surfaced to the user, never suppressed.

### Step 3 — Apply the three mechanical fixes

Edit the monitor's SKILL.md / config to replace the dead URL, re-point the key source, and
correct the output path. Show the diff. Do not invent values — use only what Step 1
verified live.

### Step 4 — Self-heal and re-run

Re-run the monitor (or its check commands) and confirm the three findings no longer fire
and the report is clean except for any genuine regression identified in Step 2.

### Step 5 — Report

State plainly: which of the three were fixed, what the genuine remaining findings are (if
any), and whether the webhook/ingest channel is actually healthy. If a real regression is
present, that is the headline — not the config cleanup.

## Principles

- **Fix the cause, not the symptom.** Editing the report to hide a finding is failure.
  The finding stops recurring because the config is corrected, not because it was muted.
- **Never suppress a genuine regression.** The whole danger is known noise masking a real
  webhook/ingest drop. If anything outside the three known findings is firing, that is the
  load-bearing output of the session.
- **No fabricated secrets.** URLs and keys come from the live report and Secret Manager,
  never from this file or from memory. Pair with [[gcp-iam-resolver]] when a 401/403 is
  actually a missing IAM permission rather than a stale value.
- **Confirm clean.** A run is not done until the monitor re-runs and the three findings are
  gone. Detect-fix-confirm, every time.

## Edge Cases

- **Report path itself is unmounted (finding 3 blocks Step 1):** resolve the path against
  `$HOME` at runtime; if still unreachable, you are in a sandbox without the herald mount —
  surface that and hand the commands to the user's machine per [[machine-bridge]].
- **403 persists after URL fix:** it is not a stale URL, it is a missing IAM role on the
  runtime service account. Switch to [[gcp-iam-resolver]].
- **A "finding" is actually new:** if the monitor reports something not in the known three,
  do not touch it mechanically — escalate it as a real regression.
