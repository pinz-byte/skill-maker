---
name: coworker-enroll
description: >-
  Enrolls a new coworker (Cowork project / agent) into the LFP mesh in one pass: creates or adopts
  its Notion inbox, registers it in the Coworker Registry, writes the row into the local
  inbox-registry.md so agent-bridge can route to it, introduces it to Symbios, and adopts the Agent
  Messaging Protocol. Idempotent: detects and completes, never duplicates. Use when the user says
  "enroll", "enroll me", "enrolate", "registrate al ecosistema", "nuevo coworker", "onboarding",
  "unete al mesh", "date de alta", or on the first session of a new Cowork project that will talk to
  other agents via agent-bridge. Also use to RE-enroll an existing coworker whose record is
  incomplete (inbox undocumented, no Registry row, stale Lifecycle, missing from inbox-registry.md).
  NOT agent-bridge (sends and receives mail): this births the coworker once so mail can reach it.
metadata:
  intent: relay
---

# Coworker Enroll -- mesh birth in one pass

Executes the birth protocol (AGENT MESSAGING PROTOCOL v1, Onboarding section).
Rule: an unregistered coworker is invisible to the PM and to agent-bridge = it does not exist.
Pattern this kills: VMC's manual onboarding took 5 days and the Registry never got it.

Hardcoded UUIDs below are permanent workspace infrastructure. Never invent a UUID.

## Step 0 -- Identity

Derive from project context: Name, Machine (M1/M2/M3/cloud), Family
(APEX/CarMatch/VMC/Subascars/Subastop/AVT/Standalone/Sensei), Function (ONE line).
If Machine or Family are ambiguous: ask POPs ONCE, all questions together.

## Step 1 -- Inbox (UUID first, name search second, never duplicate)

Notion name search is semantic and fails across environments; it has produced duplicate inboxes.
Resolution order is mandatory:

1. **UUID lookup.** Read the canonical table in `.claude/rules/inbox-registry.md` of the SKILL MAKER
   repo (or, if this project is not SKILL MAKER, the copy of that table shipped inside the installed
   `agent-bridge/SKILL.md`). If a row for this Name exists, `fetch` that UUID directly. Page loads ->
   ADOPT it; record the UUID. Page fails to load -> the row is stale; continue to 2 and flag it.
2. **Name search.** Search Notion for `[Name] -- Inbox` (with and without the mailbox emoji).
   Exact-title match found -> ADOPT, record UUID.
3. **Create.** Only if 1 and 2 both came up empty: new page at workspace root, exact title
   `[mailbox emoji] [Name] -- Inbox`, pinned header: project, machine, processing trigger
   ("tell this agent: you've got mail").

Name collision at any step = adopt and complete the existing page. Never a second inbox.

## Step 2 -- Coworker Registry (UUID first, never duplicate)

Data source: `collection://6efa025e-ab0c-462a-89dd-1db7f476f1b1`.
Query by Coworker name AND by the Inbox UUID from Step 1 (the UUID match is authoritative; names
drift). Row exists -> UPDATE: complete Inbox "name (UUID)", Machine, Function; Lifecycle=Live.
No row -> CREATE: Coworker, Machine, Family, Function, Inbox "name (UUID)", Lifecycle=Live,
Since=today, Surface=Cowork, Audit Note="enrolled via coworker-enroll <date>".

## Step 2.5 -- Local inbox registry (REQUIRED; skipping this makes the coworker invisible to the bridge)

agent-bridge routes by the table in `.claude/rules/inbox-registry.md` (SKILL MAKER repo, canonical).
`agent-bridge/SKILL.md`'s table is GENERATED from it by `gen-inbox-registry.py` -- never hand-edit that.

- **If SKILL MAKER is mounted in this session:** append the row
  `| [Name] | [Host] | [UUID] |` to the table in `.claude/rules/inbox-registry.md`, then run
  `python3 gen-inbox-registry.py` (or leave it to `./publish.sh`, which runs it). Commit.
- **If SKILL MAKER is NOT mounted (normal case for a new project):** you cannot write the canonical
  file. Do NOT write a local shadow copy -- two registries is the split-brain this step exists to
  prevent. Instead send an ASK to SKILL MAKER -- Inbox (`360da327-abb1-8196-b98d-cfc86bbe0ec6`)
  with the exact row, header `ASK . [Name] -> SKILL MAKER . YYYY-MM-DD . STATUS: UNREAD . RE: registry row`,
  and report in Step 5 that the bridge row is PENDING on SKILL MAKER. Until that row ships via
  `./publish.sh`, other agents must route to this coworker by the UUID you report, not by name.

## Step 3 -- Introduction

FYI <= 500 chars to Symbios. Symbios is a DB-mode inbox: create a ROW in data source
`fad1c35d-0143-473b-b119-439aa643640a` (Name = "FYI . enrollment . [Name]", From, Host, Status=UNREAD,
Expects Response unchecked, Reply To UUID = your inbox UUID); body: who I am, what I build, what I
depend on. If the DB write fails, fall back to prepending to the flat Symbios inbox
(`360da327-abb1-8115-bf58-fcaec470ec53`) with canonical first-line header
`FYI . [Name] -> Symbios . YYYY-MM-DD . STATUS: UNREAD . RE: enrollment` and flag the fallback.

## Step 4 -- Protocol adoption

Read "AGENT MESSAGING PROTOCOL v1" (`3a5da327-abb1-8175-98ac-fe366d3aa539`). From now on: typed
messages (ASK/FYI/REPORT/DECISION-REQ/CHASER/ACK) with hard caps and canonical first-line header;
tasks with an owner go to Focus Queue (`collection://b5c3c737-1219-4888-a081-bbfde500e180`), not to
inbox prose.

## Step 5 -- Confirmation (5 lines to POPs)

1. Inbox: created/adopted + UUID
2. Registry row: created/updated
3. Local bridge row: written+committed / PENDING on SKILL MAKER (ASK sent)
4. FYI to Symbios: sent (DB row / flat fallback)
5. Protocol adopted. Dispatcher welcome pack arrives on its next cycle (07:00/12:00/17:00 Lima).

## Failures

No Notion access -> STOP and ask POPs to connect the connector. Never invent UUIDs.
Name collision -> adopt and complete what exists; never a second row or inbox.
UUID in registry points to a missing page -> report the stale row to SKILL MAKER in the same ASK.
