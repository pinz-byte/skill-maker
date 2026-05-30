---
name: apex-builder-gate
description: >
  Mandatory pre-execution gate for every APEX Desk builder session. Loads the
  10 failure patterns from memory, runs grep audits against files the builder
  is about to touch, and blocks execution until all checks pass. Use this skill
  whenever starting any APEX builder session, executing an APEX brief, touching
  APEX code, or any session in the apex-desk project. Trigger on: "apex builder",
  "execute apex", "run apex brief", "start apex session", "apex gate", "APEX_",
  or any time a builder brief like APEX_27, APEX_50 etc. is about to be executed.
  Also trigger when the user says "load the gate", "run the audit", "pre-flight
  apex", or starts a session in the apex-desk-v2 working directory. This gate
  exists because prior builder sessions shipped 10 known failure patterns
  repeatedly. It fires every time, no exceptions.
---

# APEX Builder Gate

A mandatory pre-execution audit that runs before any APEX builder session touches
code. It exists because fresh builder sessions have no memory of failures already
paid for  and the same 10 patterns keep recurring. This gate closes that loop.

**Non-negotiable: run this before Phase A of any APEX brief.**

## Step 0  Identify Scope

Before auditing, establish what this session will touch:

1. Read the active builder brief (e.g., `APEX_50`, `APEX_27`)  specifically its
   "Files to modify" or "Phase A" section
2. List the files explicitly  these are the targets for the grep checks below
3. If no brief exists for this work: STOP. Write the brief first. No brief = no
   execution.

State the file list before proceeding: "Audit scope: [file1, file2, file3]"

## Step 1  Load Failure Memory

Read these memory files. Each encodes a real failure that cost debugging time.
They are the foundation of this audit  do not skip.

```bash
MEMORY_DIR=~/Library/Application\ Support/Claude/local-agent-mode-sessions/*/spaces/*/memory
ls $MEMORY_DIR/feedback_*.md 2>/dev/null
```

If memory files exist, read each one. The patterns are:

**Pattern 1  pg.connect() discipline**
Every `PostgresStore` or `ApexMemory` instantiation must call `pg.connect()` before
the first query. No exceptions. Sessions that skip this fail silently on the first
database call.

**Pattern 2  save_signal_plan() is INSERT only**
`save_signal_plan()` creates new records. It is never called on an existing plan.
Updates to existing plans require a direct SQL UPDATE with the plan ID.

**Pattern 3  Quote is a dataclass, not a dict**
`qdata.last`, `qdata.bid`, `qdata.ask`  not `qdata.get("last")`. The `.get()`
pattern raises AttributeError silently in some paths and returns None in others.
Always use direct attribute access with `float()`.

**Pattern 4  os.environ is frozen at startup**
Flask routes and request handlers that read rotating credentials (tokens, expiry
timestamps) must read the live `.env` file at request time. `os.environ` captures
the value at process start and will be stale after any OAuth renewal.

**Pattern 5  Schwab open orders: cancelable=True, not status=WORKING**
Resting stop orders sit in `AWAITING_STOP_CONDITION`. Filtering by
`status=WORKING` misses them. Always use `cancelable=True` for open order queries.

**Pattern 6  Option position inference is forbidden**
Option state (held, closed, expired) must be queried from Schwab live. Never infer
option position facts from the substrate alone. The substrate can be stale.

**Pattern 7  No jail entry on option close**
`_mark_local_closed()` must be called with `write_jail=False` for option positions.
Options are not subject to the 5-day trading jail. Writing a jail entry for an
option close blocks future trades incorrectly.

**Pattern 8  LaunchAgent: verify after load**
`launchctl load` or `launchctl bootstrap` is not sufficient proof of deployment.
Always follow with `launchctl list <label>` and confirm the process ID is present.
"Load command issued" is not "service running".

**Pattern 9  Data integrity: no inference-based output**
Dashboard cells and substrate records must be populated from direct queries, not
constructed from inference. If a value is unknown, the output is "PENDING"  not
a calculated estimate.

**Pattern 10  exec_server.py is Trust Tier 2: hands off**
`exec_server.py` (port 7701) is locked. No APEX brief in Tier 1 scope touches it.
If the work requires exec_server changes, stop and escalate to POPs.

## Step 2  Run Grep Audit

For each file in scope, run these checks. Copy the commands, substitute file names.

```bash
# Pattern 1  pg.connect()
grep -n "PostgresStore\|ApexMemory\|pg = " <files>
# For every hit: is pg.connect() called before the first query?

# Pattern 2  save_signal_plan() misuse
grep -n "save_signal_plan" <files>
# Any call on an existing plan ID? -> FAIL

# Pattern 3  Quote dict access
grep -n "qdata\.get\|\.get(\"mark\"\|\.get(\"last\"\|\.get(\"bid\"\|\.get(\"ask\"" <files>
# Any hit -> FAIL

# Pattern 4  os.environ for rotating credentials
grep -n "os\.environ.*TOKEN\|os\.environ.*EXPIR" <files>
# Any hit in Flask route or request handler -> FAIL

# Pattern 5  Schwab order filter
grep -n "status=.WORKING\|\"status\": \"WORKING\"" <files>
# Any hit -> FAIL

# Pattern 6  Option inference
grep -n "OPTION\|assetType\|asset_type" <files>
# Any logic constructing option state without a live Schwab query -> FAIL

# Pattern 7  Jail on option close
grep -n "write_jail\|_mark_local_closed" <files>
# Called without write_jail=False for options -> FAIL

# Pattern 8  LaunchAgent verification
grep -n "launchctl load\|launchctl bootstrap" <files>
# No following launchctl list verification -> FAIL

# Pattern 9  Inference-based output
grep -n "PENDING\|source_of_truth" <files>
# Any output cell populated by calculation instead of query -> FAIL

# Pattern 10  exec_server boundary
grep -rn "exec_server\|port 7701\|localhost:7701" <files>
# Any hit in Tier 1 scope -> FAIL
```

## Step 3  Produce Audit Table

Output this table. Every row must have a result before proceeding.

| Pattern | Files Checked | Result | Finding |
|---|---|---|---|
| 1. pg.connect() | ... | PASS / FAIL / N/A | ... |
| 2. save_signal_plan() | ... | PASS / FAIL / N/A | ... |
| 3. Quote dataclass | ... | PASS / FAIL / N/A | ... |
| 4. os.environ creds | ... | PASS / FAIL / N/A | ... |
| 5. Schwab order filter | ... | PASS / FAIL / N/A | ... |
| 6. Option inference | ... | PASS / FAIL / N/A | ... |
| 7. Jail on option close | ... | PASS / FAIL / N/A | ... |
| 8. LaunchAgent verify | ... | PASS / FAIL / N/A | ... |
| 9. Data integrity | ... | PASS / FAIL / N/A | ... |
| 10. exec_server boundary | ... | PASS / FAIL / N/A | ... |

## Step 4  Fix All FAILs

For every FAIL row: fix the existing violation before writing any new code.
Do not layer new features on top of known bugs.

If a fix requires scope expansion beyond the current brief: stop and escalate to
POPs. Do not improvise solutions that touch untested paths.

## Step 5  Run Brief Pre-Flight

After the gate is clean, run the specific pre-flight checklist from the active
brief (the brief's own "PRE-FLIGHT" or "PRECONDITIONS" section). The gate checks
cross-cutting patterns; the brief checks brief-specific preconditions. Both must
pass.

## Step 6  Declare All-Clear

State explicitly before starting execution:

"Gate complete. [N] FAILs found and fixed. [M] N/A. All clear  proceeding to
[Brief ID] Phase A."

If any FAIL could not be fixed within scope: state what blocked you and wait for
POPs before proceeding.

## Principles

**The gate runs every time.** Experience does not exempt a session from the audit.
The patterns recur precisely because fresh sessions feel like they already know
this. They don't.

**Fix before build.** A session that starts on top of a known bug compounds the
debt. The gate's job is to clear the floor before construction begins.

**N/A is not a skip.** Mark N/A only when a pattern genuinely cannot apply to
the files in scope. "I didn't check" is not N/A.

**Escalate, don't improvise.** If a FAIL requires changes outside the brief's
scope, stop. Improvised fixes in fresh context create new patterns for the next
gate to catch.

## When a New Failure Pattern Emerges

If a post-session retrospective or user report identifies a new failure pattern:

1. Add it as Pattern 11 (or next number) to this skill
2. Add the grep check to Step 2
3. Add the row to the Step 3 table
4. Rebuild and redeploy the skill

The gate grows with the project. New failures become permanent checks.
