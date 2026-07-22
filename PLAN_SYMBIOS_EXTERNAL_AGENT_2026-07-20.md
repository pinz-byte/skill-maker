# PLAN — Symbios Inbox × Notion Claude External Agent
**Created:** 2026-07-20 · **Project:** SKILL MAKER (agent-bridge owner) · **Status:** DRAFT — pending POPs approval
**Verified state:** Plan tier OK · "Manage external agents = All external agents" ON · Zero agents created · Notion credits available (dashboard in sidebar)

## Objective

A message arriving in the Symbios Inbox gets picked up and acted on by a Claude External Agent
inside Notion — no human saying "you've got mail," no Chat session polling. This closes the
last carrier dependency for the Symbios node specifically.

## The structural problem this plan must solve (not skip)

The current Symbios Inbox is a **flat page** — agent-bridge prepends message *blocks*.
Notion automations are **database** automations: they fire on "page added" to a database,
not on blocks appended to a page. Custom Agent triggers are likewise database/comment-shaped.

**Consequence: the inbox format itself must change for Symbios** — messages must become
rows (pages) in a database, not blocks in a page. That is a protocol change to agent-bridge
SEND for one recipient, which is why this plan lives in SKILL MAKER.

## Phases

### Phase 0 — Feasibility gate (BLOCKS everything; ~15 min, throwaway assets)
Test on a scratch database, not the real inbox:
1. Create throwaway DB `AGENT-GATE-TEST` with a Status property.
2. Create a minimal Claude agent (blank template), grant it access to that DB only.
3. **Test A:** database automation "page added → create comment @-mentioning the agent."
   Open question this resolves: can an automation comment programmatically *mention an agent*
   and does that mention fire the agent's comment trigger? (Docs confirm comment-mention as a
   trigger; they do NOT confirm automations can author such a mention. Unverified link.)
4. **Test B (fallback):** skip the automation entirely — configure the agent's OWN trigger
   on "page added" to the DB (Custom Agent triggers/schedules panel). If agents can trigger
   directly on database events, the automation layer is unnecessary — simpler chain wins.
5. **Gate verdict:** A works → chain design. B works → direct-trigger design (prefer: fewer
   moving parts). Neither → STOP; revert to plain automation + AI-prompt (degraded mode) and
   re-plan.
6. Record verdict + screenshots in this file under "Phase 0 result." Delete throwaway assets.

**Owner:** POPs in Notion UI (or a Cowork computer-use session driving Chrome).
I cannot do this via MCP — agent config and automation editors are not API surfaces.

### Phase 1 — Symbios Inbox DB (only after Phase 0 passes)
1. Create database `Symbios Inbox DB` (child of the existing Symbios Inbox page, so the
   old flat log remains as archive/history directly above it).
2. Schema mirrors the bridge message format: `From` (text), `Host` (select: Cowork M1/M2/M3,
   Claude.ai Chat, ChatGPT, M-DigitalEdge), `Date` (created time), `Status` (select:
   UNREAD / IN PROGRESS / READ), `Expects Response` (checkbox), `Reply To UUID` (text).
   Message body = page content.
3. Register the DB's data-source UUID in `.claude/rules/inbox-registry.md` as a new column
   or row note (`Symbios — DB mode`), keeping the legacy page UUID until cutover completes.

**Owner:** I can do this via Notion MCP (create_database) — no UI needed.

### Phase 2 — The agent itself
1. `Agents → + New Agent → Claude → blank` (not the coding template; no GitHub needed).
2. Name: `Symbios Courier`. Access: Symbios Inbox DB (full), Symbios Inbox legacy page
   (read), and — decision needed — which OTHER inboxes it may write responses to.
   **v1 scope: NONE.** It processes, acts within what it can see, writes its response as a
   comment/status on the message row, and sets Status=READ. Cross-inbox responses stay with
   the existing mesh until we trust it. Expanding write scope is a v2 decision, not a default.
3. Instructions: condensed RECEIVE protocol — read row body, act only within granted access,
   write outcome on the row, set Status, never touch other rows, surface unseen constraints
   in its outcome comment. I draft this text (see Appendix A placeholder); POPs pastes it.
4. Trigger: whichever design Phase 0 selected.

**Owner:** POPs pastes config in UI; I author every text block.

### Phase 3 — agent-bridge skill update (SKILL MAKER work, my domain)
1. Update `agent-bridge/SKILL.md` SEND path: recipient = Symbios → create page in
   Symbios Inbox DB with schema properties, instead of prepending a block to the page.
   All other recipients unchanged.
2. Update inbox-registry rule file; run `gen-inbox-registry.py` via `./publish.sh`.
3. Publish natively on M2 (sandbox cannot run publish — known limit). Version bump: minor
   (new capability in message routing).

### Phase 4 — E2E test + cutover criteria
1. Send a real bridge message from SKILL MAKER to Symbios via the new path.
2. Verify: agent fired without human trigger · acted · wrote outcome · set READ ·
   run visible in Agent Activity · credit cost of the run recorded here.
3. **Cutover rule:** 3 consecutive real messages processed correctly → new path is canonical
   for Symbios; announce via bridge to all active projects. Any failure → diagnose before
   sending message 4; two consecutive failures → freeze, revert SEND path, keep DB as
   passive log.
4. **Credit watch:** if per-run cost × expected monthly volume is material, decide explicitly
   whether the autonomy is worth it vs. the free automation+AI-prompt degraded mode.

## Explicitly out of scope (v1)
- Migrating ANY other project inbox to DB mode (one node first).
- Cross-inbox write access for the agent.
- Retiring "you've got mail" for Symbios — keep it as manual fallback until cutover rule met.
- The 2026-06-04→06-23 backlog (~23 UNREAD) — separate dedicated session, unrelated workflow.

## Rollback
Delete/disable agent + automation; agent-bridge SEND reverts to block-prepend (one-line
skill revert + publish). Legacy flat page never stopped existing. Cost of full rollback: <30 min.

## Phase 0 result
**VERDICT: PASS — Test B (direct agent trigger). Executed 2026-07-20 ~12:30 Lima, driven from Cowork via Chrome.**

- Claude External Agent created (blank template) in LFP's Workspace (Business Plan confirmed
  via workspace switcher). Agent id/settings: app.notion.com/agent/3a3da327abb180b680e4009293f63992
- Native agent trigger types confirmed in UI: On a schedule; Slack (message posted, emoji
  reaction, agent mentioned); Notion (comment added to page, **page added to database**,
  property updated in database, page removed from database). Automation-comment chain (Test A)
  NOT needed — never tested, unnecessary.
- Trigger config: "Page added" on AGENT-GATE-TEST, view=Entire database, condition="Any page
  added", "Wait for edits to finish"=ON. Gotcha: the Add trigger button stays disabled until a
  property/condition is selected — "Any page added" is a required explicit choice, not a default.
- Access: DB auto-added to agent's access list as "No access" — had to manually set
  "Can edit content". This will matter for the real inbox: trigger != access, set both.
- Live fire: page "GATE TEST 001" created via **Notion MCP** (not UI) at ~12:26 →
  agent showed "Claude is working" ~5 min later → comment "GATE TEST OK - processed by Claude
  agent..." + Status flipped UNREAD→READ, "Claude finished". MCP/API-created pages DO fire the
  trigger. End-to-end latency ~5-7 min with wait-for-edits on.
- Notion MCP fetch returned a stale cached read during verification — verify agent runs via UI
  or delayed re-fetch, don't trust an immediate MCP fetch after a write.
- Throwaway assets still live (AGENT-GATE-TEST DB + test row + agent in TEST MODE):
  keep until Phase 1-2 repoint the same agent at the real inbox DB, then delete the test DB.

**Cleared to proceed to Phase 1 (Symbios Inbox DB) and Phase 2 (repoint + real instructions).**

## Execution log (2026-07-20, same session)

- **Phase 1 DONE:** Symbios Inbox DB created as child of the legacy flat inbox page.
  DB page: 1ed6e797-bcd8-4d99-8de0-51e82b0f2983 · data source: fad1c35d-0143-473b-b119-439aa643640a.
- **Phase 2 DONE:** trigger "Page added in Symbios Inbox DB" ON; AGENT-GATE-TEST trigger
  toggled OFF; TEST MODE instructions replaced with Symbios Courier RECEIVE protocol
  (IN PROGRESS -> act -> one outcome comment, RESPONSE: prefix when expected -> READ);
  access "Can edit content"; saved ("Agent saved successfully"). Agent model: Sonnet 4.6.
  NOTE: one save was silently reverted to "Unsaved edits" after an Escape keypress —
  always re-verify the header says saved, the toast alone is not proof.
- **Phase 3 DONE (files):** inbox-registry.md gained a DB-mode section (Symbios row);
  agent-bridge/SKILL.md gained Step 3b (DB-mode SEND: create row with properties, check
  row comments for responses, 1-hour fallback to flat page). **Publish pending — must run
  ./publish.sh natively on M2 (sandbox cannot).**
- **Phase 4: E2E 1 of 3 PASS.** Real message row created via MCP 16:27 local; agent set
  IN PROGRESS, processed, commented with What-I-did + RESPONSE: (including a self-audit
  of its access envelope), set READ by ~16:35. Latency ~6-8 min. Two more clean
  processings required before cutover is canonical.
- **Cleanup pending:** AGENT-GATE-TEST DB still exists (trigger off, inert) — delete
  manually whenever; also remove its row from the agent's access list at that time.

## Appendix A — Agent instruction draft
_(I write this once Phase 0 verdict picks the trigger design — the instructions differ
slightly between comment-triggered and page-added-triggered modes.)_
