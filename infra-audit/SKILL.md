---
name: infra-audit
description: >-
  Audits infrastructure and resource consumption that is ALREADY RUNNING -- inventories every
  live service, job, store and paid API in a project, prices each one, and returns a KILL /
  RESIZE / CAP list with the exact commands. Built for the failure where builders provision
  services without a cost model and the bill compounds silently. Use on "audit the infra",
  "auditoria de infraestructura", "why is the bill so high", "que esta consumiendo", "what is
  actually running", "cloud costs", "we are overspending", "sobreconsumo", "kill what we are
  not using", "resource audit", "quota check", "revisar el gasto", or after ANY cost spike,
  credit exhaustion, quota block or rate-limit incident. Also fire proactively before adding a
  service to a project never audited, and before any deploy that raises min-instances, memory
  or schedule frequency. NOT dependency-audit (prices a dependency BEFORE code ships): this
  audits what is already deployed and burning.
metadata:
  intent: audit
---

# Infra Audit -- Running-Cost and Resource Audit

## Why This Exists

`dependency-audit` prices a dependency before code ships. Nothing priced what was already
deployed. Builders provision Cloud Run services, schedulers, functions and API keys to make a
feature work, then move on. Each one is individually cheap and collectively unbounded. The bill
is the only feedback signal, and it arrives a month late, aggregated, with no attribution.

This skill makes the running system legible: what exists, what it costs, what is waste.

## Hard Rules

1. **Read-only by default.** The audit NEVER deletes, scales down or disables anything on its
   own. It produces the commands; a human runs them.
2. **Every finding carries evidence.** A resource is not waste because it looks idle -- quote
   the metric (requests/day, invocations, last-deploy date, bytes read).
3. **Price everything, including zero.** A resource costing $0 today with no cap is a finding,
   not a pass. Unbounded is the risk, not the current number.
4. **Attribution before verdict.** If you cannot say which feature a resource serves, that is
   itself the top finding -- orphaned infrastructure is the cheapest thing to kill and the most
   likely to be missed.

## Phase 1 -- Inventory (what exists)

Enumerate before pricing. Run per project; record the project id in the report.

```bash
PROJECT=<project-id>

# Compute surfaces
gcloud run services list --project "$PROJECT" \
  --format='table(metadata.name,status.url,spec.template.metadata.annotations."autoscaling.knative.dev/minScale",spec.template.spec.containers[0].resources.limits.memory)'
gcloud functions list --project "$PROJECT" --format='table(name,status,availableMemoryMb,runtime,updateTime)'

# Scheduled burn
gcloud scheduler jobs list --project "$PROJECT" --format='table(name,schedule,state,lastAttemptTime)'

# Stores
gcloud storage buckets list --project "$PROJECT" --format='table(name,location,storageClass)'
gcloud firestore databases list --project "$PROJECT"

# Orphan candidates
gcloud run revisions list --project "$PROJECT" --format='table(metadata.name,status.conditions[0].status,spec.containers[0].image)'
gcloud artifacts repositories list --project "$PROJECT"
gcloud iam service-accounts list --project "$PROJECT" --format='table(email,disabled)'

# Guardrails present or absent
gcloud billing budgets list --billing-account=<BILLING_ACCT> 2>/dev/null || echo "NO BUDGET CONFIGURED"
```

Then enumerate the non-GCP burn, which the console never shows:

- LLM APIs (Anthropic, OpenAI): which keys exist, which surfaces hold them, is there a spend cap
- Credit-metered services (Apollo, enrichment, scraping proxies): current balance, burn rate
- Anything hitting a third-party endpoint on a schedule

## Phase 2 -- Pricing (what each costs)

For every inventoried resource, fill: `unit cost x volume x frequency = monthly run rate`.
Where volume is unknown, pull it -- do not estimate:

```bash
# Cloud Run request volume, last 30d
gcloud monitoring time-series list --project "$PROJECT" \
  --filter='metric.type="run.googleapis.com/request_count"' --interval-end-time=now

# Firestore read volume (the silent killer)
gcloud monitoring time-series list --project "$PROJECT" \
  --filter='metric.type="firestore.googleapis.com/document/read_count"'
```

A resource whose volume cannot be measured is reported as UNMEASURED, never as cheap.

## Phase 3 -- Waste Signature Library

Check every signature. Each is a recurring, concrete pattern -- not a heuristic.

| # | Signature | Detection | Typical fix |
|---|---|---|---|
| W1 | Cloud Run `min-instances >= 1` on low-traffic service | minScale annotation set, requests/day under ~1000 | `--min-instances=0` |
| W2 | CPU always-allocated instead of request-based | `--cpu-throttling` absent | enable throttling |
| W3 | Oversized function memory | 512MB+ for JSON transform / webhook | drop to 128-256MB |
| W4 | Scheduler firing faster than the source changes | hourly job on a daily-updating source | match cadence to source |
| W5 | Per-record LLM call inside a full-table loop | LLM call in a loop body over a collection | batch, cache, or replace per `dependency-audit` |
| W6 | Unbounded retry on a paid call | retry policy with no max, each retry billable | cap retries, dead-letter |
| W7 | Firestore full-collection read per page load | read_count scales with users, not with writes | index + paginate + cache |
| W8 | Orphaned revisions / images / buckets / service accounts | traffic 0, no recent access, no owner | delete after owner confirms |
| W9 | Duplicate pipelines on one source | two jobs, same target domain | consolidate |
| W10 | DEBUG logging in prod | Cloud Logging ingestion volume | raise log level |
| W11 | Dev/staging left running | non-prod project or `-dev` suffix, still billing | schedule down or delete |
| W12 | No budget alert on the billing account | budgets list empty | create budget + alert |
| W13 | No spend/quota cap on a paid API key | provider console shows unlimited | set hard cap at provider |
| W14 | Unattributed resource | no owner, no feature mapping | kill candidate, highest priority |

W12, W13 and W14 are reported even when current spend is low. They are the reason a spike is
possible at all.

## Phase 4 -- Report

```
INFRA AUDIT -- [project]
Date: [date]   Billing account: [acct]   Measured window: [30d]

RUN RATE
| Resource | Type | Volume (30d) | Monthly cost | Owner/feature | Verdict |
|----------|------|--------------|--------------|---------------|---------|

TOTAL MEASURED: $X/mo    UNMEASURED RESOURCES: N

FINDINGS (ranked by monthly saving, then by unbounded risk)
1. [W#] resource -- evidence -- saving $X/mo -- fix: `command`

UNBOUNDED EXPOSURE (no cap, any current spend)
- [resource] -- theoretical ceiling if [failure mode] -- fix: `command`

ORPHANS (no owner identified)
- [resource] -- last activity [date] -- CONFIRM BEFORE DELETING

GUARDRAILS
- Budget alert: PRESENT / ABSENT -> `command`
- Per-API spend cap: PRESENT / ABSENT -> [provider console step]
- min-instances policy: [state]
```

## Phase 5 -- Install the Guardrail

An audit that does not leave a tripwire behind will be needed again identically next quarter.
Before closing, ensure at minimum:

```bash
# Budget + alert at 50/90/100 percent
gcloud billing budgets create --billing-account=<ACCT> \
  --display-name="<project> monthly" --budget-amount=<USD> \
  --threshold-rule=percent=0.5 --threshold-rule=percent=0.9 --threshold-rule=percent=1.0
```

And record the audited run rate as the baseline, so the next audit is a diff, not a rebuild.

## Boundaries

- `dependency-audit` -- prices a dependency BEFORE it ships. Upstream of this skill.
- `apex-health` / `carmatch-intel` / `herald-config-doctor` -- is-it-up probes for one named
  runtime. This skill asks what-does-it-cost across all of them.
- `disk-doctor` -- local Mac disk. This is cloud and paid-API spend.
- `auditor-general` -- did the build deliver what was promised. This ignores promises and reads
  the bill.
