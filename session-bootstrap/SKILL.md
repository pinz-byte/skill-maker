---
name: session-bootstrap
description: >-
  Brings a fresh, blank Cowork session up to full working state for ANY project or
  co-worker — verifies the project's mounted folders, live MCP connectors, loaded
  memory, and (when the project needs live data) mounts + verifies a read-only
  credential (service-account / API key) with a real connection check, then prints
  the project's data map and working rules. Cowork is stateless — every session
  boots blank — so this is how you reconstitute a workspace instead of re-deriving
  it. Use at the START of any session, and whenever the user says "bootstrap",
  "start session", "new session", "clone the workspace", "levanta/arranca la
  sesión", "reconnect", "reconecta", "connect the data", "mount the key", "start
  [project]", "get me set up", or asks how to bring a cold session up to speed.
  Project-agnostic: it reads each project's requirements from that project's own
  config, so one skill bootstraps every co-worker. Fire it even on casual cold
  openers ("ok, back to it", "continuemos").
metadata:
  intent: orient
---

# Session Bootstrap

A Cowork session boots **blank**. Nothing from prior work carries over on its own —
not files, not secrets, not months of context. Only three channels survive into a new
session, plus a live data connection when the work needs it:

1. **Mounted folders** — files on disk the user re-selects in the picker.
2. **Authorized MCP connectors** — persist once connected.
3. **Persistent memory files** — load automatically each session.
4. **(optional) Live data** — a read-only credential (service-account / scoped key) mounted per session for direct DB/API reads.

You never "clone" a session — you **reconstitute** it from those. This skill runs that
reconstitution as an ordered, verified startup so a cold session comes up ready,
without the user re-explaining anything.

**This skill is project-agnostic.** It doesn't hardcode any one project's folders or
keys — it reads what to verify from the **project's own config** (its `CLAUDE.md`, a
continuity seed, or a `bootstrap.yml` manifest at the project root) and checks those.
One skill bootstraps every co-worker; each project declares its own requirements.

**Relationship to other skills:** `reentry` reconstructs *what we were doing*;
`continuity-seed` serializes state for the next session; `machine-bridge` hardens the
sandbox↔machine boundary. This skill owns the **verify-and-connect startup** — mounts,
connectors, memory, and the live-data credential. Compose with them; don't
re-implement them.

## Where the per-project requirements come from

On first run for a project, discover its requirements in this order and cache them in
a data capsule so later sessions don't re-ask:
1. A **`bootstrap.yml`** (or `.bootstrap.md`) at the project root — the explicit manifest, if present.
2. The project's **`CLAUDE.md`** — required folders, stack, key paths.
3. The latest **continuity seed** / project memory.
4. Ask the user for anything still missing (once), then record it.

A minimal manifest looks like:
```yaml
project: {name}
mounts:        [{picker-folder}, ...]        # required folders
connectors:    [{mcp-name}, ...]             # MCP connectors that must be live
memory:        [{memory-slug}, ...]          # core memories to confirm loaded
data:                                        # optional — only if live reads are needed
  kind:        firestore | rest | sql | none
  credential:  {path to read-only key, e.g. ./svc-ro.json}
  verify:      {a cheap read that proves the connection}  # e.g. count a known collection
  boundary:    read-only                     # never mount write-capable creds in a sandbox
map_doc:       {path to the project's data map / consumption rules}
```

## Run the bootstrap in this order

Each step verifies, reports ✅/⚠, and on ⚠ states exactly what the user must do. Never
silently continue past a hard blocker — a missing mount or credential makes everything
downstream partial but *looks* authoritative, which is worse than stopping.

### 1 — Mounts
`ls -1 /sessions/*/mnt/ 2>/dev/null | grep -vE '^(outputs|uploads)$'`. Compare to the
manifest's `mounts`. If a required folder is missing, stop and name the exact picker
folder to add. A bootstrap on partial mounts is built on sand.

### 2 — Connectors
Confirm each connector in `connectors` is live — don't assume; a connector can be
deauthorized between sessions. If one is missing or a call returns an auth error,
surface it and point the user to reconnect rather than burning turns working around a
dead connector.

### 3 — Memory
Confirm the `memory` slugs loaded, and lean on them instead of re-deriving. If a core
one is missing, that's a signal to write it — the session is generating context worth
keeping.

### 4 — Live data credential (only if `data.kind != none`)
This is the piece the other startup skills don't cover.
- Verify the read-only credential is mounted at `data.credential`. Confirm the path
  with the user on first run; capsule it after.
- **Verify the connection is live — run `data.verify`, don't assume the key works.**
  For Firestore that's an Admin SDK `count()` on a known collection; for a REST/SQL
  source, a cheap read that returns a known shape. Report the result.
- **Hard safety boundary — abort if violated:** mount only a **read-only / read-scoped**
  credential. Never a write-capable key in a sandbox — an agent iterating with write
  access to the raw source is how you corrupt what you're reading. Read raw, write only
  to a clean target. The key is a **secret**: never commit it, never let it reach a
  deploy folder, never expose it publicly.
- If the credential doesn't exist yet, hand the user the exact mint/scope command for
  their platform (e.g. a `gcloud` service-account with a read-only role) so they can
  create a read-scoped one in minutes.

### 5 — Data map + working rules
If `map_doc` is set, load it and print the project's canonical map + consumption rules
(which source is authoritative for what, and the gotchas that produce wrong numbers).
Surfacing these at startup is what stops a session from confidently shipping bad data.

## Output — bootstrap status report

Emit one compact block so readiness is legible at a glance:

```
BOOTSTRAP · {project} · {date}
Mounts:      ✅ {folders}            (or ⚠ add: {folder})
Connectors:  ✅ {names}              (or ⚠ reconnect: {name})
Memory:      ✅ {n} core loaded
Data:        ✅ {verify result}      (or ⚠ credential not mounted — mint/mount)  · skipped if none
Map/rules:   printed                 · skipped if none
START HERE → {the single highest-value next action given what's ready}
```

Then drop into work. If a hard item is ⚠ (missing mount or credential), START HERE is
"resolve that blocker" — nothing downstream is trustworthy until it's green.

## Worked example — Subastop / VMC (Dash Lord)

A concrete manifest, to show the shape (not part of the skill's logic):
```yaml
project: dashlord
mounts:     [pagebuilder, vmc-core, dashlord]
connectors: [supermetrics, notion, google-drive]
memory:     [vmc-data-map, subastop-vmc-brand-architecture, dash-lord-initiative, vmc-social-analytics]
data:
  kind:       firestore
  credential: ./pagebuilder-ro.json      # project vmc-intelligence, role roles/datastore.viewer
  verify:     firestore count offers_clean   # expect ~19,618
  boundary:   read-only                   # NEVER the write SA (it has WRITE to offers_clean)
map_doc:    vmc-core/contracts/DATA_MAP_extracted_vmc.md
```
Its rules to print: seller intel → `offers_clean` (not bid_streams); GMV → `kpis`/`auctions`;
`users` = bidders not registered accounts; live events → Herald; `Pacífico` = 3 entities;
anchor seller cuts on sell-through + median, not compliance; REST API v3 is IP-locked
(sandbox can't call it — Firestore SA is the read path). Full detail lives in `map_doc`.
