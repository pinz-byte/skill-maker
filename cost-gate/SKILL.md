---
name: cost-gate
description: >-
  Blocking harness that runs BEFORE any work which creates, scales or pays for infrastructure
  -- a fixed five-stage sequence ending in PASS or BLOCK that halts the session until cleared.
  Fires on "gcloud run deploy", "firebase deploy", "add a service", "levantar un servicio",
  "create a function", "add a scheduler", "spin up", "new API key", "raise min-instances",
  "bump the memory", "vamos a usar X", "cost gate", "corre el gate", "run the gate", and
  proactively on the first turn of ANY session that will provision, resize or wire a paid
  endpoint -- even when nobody asked for a gate. Exits in one step when the work touches no
  billable resource, so it never gates ordinary coding. Orchestrates dependency-audit (the
  increment) and infra-audit (the baseline) instead of duplicating them, and writes an
  approved-spend ledger so the next audit is a diff. NOT factory-gate or apex-builder-gate
  (stage readiness on one production line): this gates money, in every project.
metadata:
  intent: audit
---

# Cost Gate -- Blocking Harness for Infrastructure Spend

## Contract

This skill does not advise. It returns exactly one of two verdicts:

- **PASS** -- proceed, and a ledger line is written.
- **BLOCK** -- the session does not write provisioning code, does not run a deploy command,
  and does not create a resource until the named stage is cleared.

A BLOCK names the stage, the failing condition, and the one action that clears it. It never
lists five things to think about.

## S0 -- Applicability (fast exit, always first)

Answer one question: **does the pending work create, resize, schedule or bill a resource?**

| Pending work | Gate |
|---|---|
| New Cloud Run service / function / job / bucket / database | RUN |
| Raising min-instances, memory, CPU, timeout, schedule frequency | RUN |
| First call to a paid or rate-limited API from a new surface | RUN |
| New API key, new billing-account resource, new external service | RUN |
| Editing code in an existing service, refactor, tests, docs, copy | **EXIT -- do not gate** |
| Reading, auditing, debugging without provisioning | **EXIT -- do not gate** |

Say "cost-gate: not applicable" and continue. A gate that fires on everything gets bypassed,
and a bypassed gate is worse than no gate because it manufactures the belief that something
was checked. S0 exists to protect the gate's own credibility.

## S1 -- Envelope

Read `.claude/rules/cost-envelope.md` in the current project.

- **Absent or stale (>90 days)** -> **BLOCK**. Clear it by asking one question: *what is the
  acceptable monthly run rate for this project at expected scale?* Write the answer to that
  file with a date. Do not propose a number for the user to accept; an envelope the user did
  not choose is not a constraint, it is a decoration.
- Present -> record `ENVELOPE: $X/mo` and continue.

## S2 -- Baseline

Read `.claude/rules/cost-ledger.md` for the last `INFRA AUDIT` line.

- **Never audited, or audit older than 90 days** -> **BLOCK**. Clear it by running
  `infra-audit` on this project. You cannot approve an increment against an unknown base.
- Present -> record `BASELINE: $Y/mo as of [date]` and continue.

## S3 -- Increment

Run `dependency-audit` against the pending change only. Produce the delta:

```
INCREMENT: [resource] -- [frequency] -- $Z/mo projected
PROJECTED TOTAL: $Y + $Z = $T/mo   vs ENVELOPE $X/mo
```

- `$T > $X` -> **BLOCK**. Clear it by one of: a REPLACE verdict from dependency-audit that
  brings `$T` under `$X`, a DEFER, or an explicit envelope raise recorded in S1's file.
- `$T <= $X` -> continue.
- Delta cannot be projected because volume is unknown -> **BLOCK**. Unmeasurable is not cheap.

## S4 -- Guardrail

The new resource does not pass without its own ceiling. Check each that applies:

| Resource | Required ceiling |
|---|---|
| Cloud Run service | `--min-instances=0` unless justified in writing, and `--max-instances` set |
| Cloud Function | memory sized to the workload, `--max-instances` set |
| Scheduler job | cadence matched to how often the source actually changes |
| Any retrying caller of a paid endpoint | max retry count + dead-letter, never infinite |
| New paid API key | hard spend cap set at the provider, not just an alert |
| Billing account | budget + threshold alerts exist at all |

Any required ceiling absent -> **BLOCK**, and emit the exact command or console step.

## S5 -- Verdict and Ledger

On PASS, append to `.claude/rules/cost-ledger.md`:

```
[date] APPROVED  [resource]  +$Z/mo  -> projected $T/mo  (envelope $X/mo)  by: [who]
```

The ledger is the point. It turns the next `infra-audit` into a diff against approved spend
instead of a rediscovery from zero, and it makes drift visible: when measured spend exceeds
the sum of approved increments, something was provisioned outside the gate.

## Override

An un-overridable gate gets deleted the first time it is wrong. This one can be overridden by
the user saying so explicitly -- never by the agent deciding the check is unnecessary. Every
override writes:

```
[date] OVERRIDE  [stage]  [resource]  reason: [stated reason]  by: [who]
```

Overrides are reviewed at the next `infra-audit`. A stage overridden three times is a design
flaw in this skill, not a discipline problem in the user.

## Precedence

Multiple gates must never block the same session twice.

| Gate | Owns | Order |
|---|---|---|
| `cost-gate` | money: does this spend fit the envelope | FIRST, whenever money is touched |
| `factory-gate` | stage readiness on the Pagebuilder line | after cost-gate, in pagebuilder |
| `apex-builder-gate` | build readiness on the APEX line | after cost-gate, in APEX |
| `pre-deliver` | strategic artifact quality before shipping a document | unrelated axis, any time |

If another gate has already blocked, do not emit a second BLOCK. Report cost-gate's findings
into the existing block so the user clears one thing, once.

## Boundaries

- `dependency-audit` -- prices one increment. Called by S3; not a substitute for this harness.
- `infra-audit` -- prices the running baseline. Called by S2.
- `phased-deploy` / `carmatch-deploy` -- run the deploy. They execute after this gate passes.
- `auditor-general` -- checks whether a build delivered what was promised. Ignores spend.
