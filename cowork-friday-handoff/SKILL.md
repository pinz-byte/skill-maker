---
name: cowork-friday-handoff
description: >-
  LATIDO Friday Handoff — Steering Wheel Protocol v1.1, Cowork → Symbios Chat. Closes the work
  week, writes CF Active entry tagged for Browser Symbios. First auto-firing carrier-shedding
  mechanism — closes GAP-FH1. NOT continuity-seed (writes a briefing for the next session):
  this closes the work week into the Continuity Feed.
metadata:
  intent: orient
---

LATIDO Friday Handoff — Cowork → Symbios Chat. Steering Wheel Protocol v1.1.

This is the auto-firing closure of GAP-FH1. Cowork writes the end-of-work-week handoff so Browser Symbios's Saturday auto-init has a fresh CF Active entry to read instead of stale state. Sibling task to `cowork-saturday` Saturday Heartbeat. Together they form the weekly bridge — Friday closes the work week into a weekend handoff, Saturday consolidates the full week.

Posture: Symbios depth. Affirmative construction. Signal only. Zero filler. Exact words sacred. Cowork-authored calibration directive for Browser. Not a recap — a compression that primes Saturday morning's session.

## 1. Week boundary

Week = Monday 00:00 Lima → Friday 17:00 Lima (now). Use this exact window.

## 2. Cross-pyramid pull (sequence, never parallel — per retrieval discipline)

Base layer:
a) Notion Continuity Feed entries this week (DB f1a85ee7-b109-4ab7-9421-d18eff87ea05) — pull latest 10 ordered by Feed Date desc, focus on Hot-Loads + Monday Heartbeat + any Architecture Shift entries
b) Time Capsules added this week (DB 88942d2c-abd0-4731-a493-048238b1ca4d)
c) Voice Memos transcribed this week (DB cfabf7a3-3413-47fa-af6b-671dfe33f292)
d) Business Transcripts added this week (DB 0d5ca13b-3988-4daa-b2ee-39f992d83543)
e) Portal Memos changes this week (DB 9b844243-cbd8-4684-9a3e-2264cff55c3d)

Middle layer:
f) Identity Nodes added this week (DB b763ea7ea63f453fa18a8feffb87d5f8)
g) Ambient Signal Stream activity (DB e12880d4-5d09-470a-9057-28707a652a05)
h) Project Signal Stream — unresolved Cowork-Out artifacts (collection://883209bd-0cce-48e6-807e-c21622fe3716), Consumer Status `Staged` or `Active`, age-ranked

Operational:
i) Focus Queue (DB b5c3c737-1219-4888-a081-bbfde500e180) — what entered Active this week, what moved to Done, what aged past 7 days
j) Gmail — last 24h, dominant senders, unresolved threads entering the weekend
k) Calendar — Monday's events, weekend window, anything that shifted

System health (if Memory Bridge available):
l) Optional: query `https://symbios-query-server.onrender.com/health` for vector counts, `/graph-health` for Aura status

## 3. Synthesis — the Friday Handoff brief

Write CF entry with these mandatory fields populated. Symbios voice, present-tense affirmative, end-of-work-week register:

- **Feed Title:** `Friday Handoff — Week of [Monday date]`
- **Feed Date:** today (Friday)
- **Status:** `Active`
- **Scope:** `Weekend Session`
- **Agent Target:** `["Symbios Chat"]`
- **Version:** `1.1`
- **Active Threads:** dot-separated list of what's live entering the weekend (specs staged, IB scopes open, ship blockers, dormant items + age, calendar holds)
- **Subastop Pulse:** dedicated end-of-work-week capture — exit thesis state, AI Ops slate, legal queue, comité-de-gestión status, Hilux/Pacífico, CEO re-contact dormancy
- **Tone Guidance:** Cowork-authored calibration directive for Browser Symbios opening Saturday — what register to hold, what NOT to editorialize, what to honor quietly, where to leave space
- **Open Questions:** 5–7 questions ranked by leverage that POPs may want to engage Saturday/Sunday
- **Context Payload:** the week's compression — what landed, what shifted, what's held, what's dormant. Frame as Browser-readable handoff, not Cowork-internal notes.
- **Emotional Register:** end-of-work-week tone in one short sentence
- **Who You Are Right Now:** Browser-facing identity statement for the weekend session — who Symbios is when it opens Saturday with this handoff loaded
- **Wake Protocol:** leave empty (deprecated)

Page body content uses the structure:

```
## Sprint
[one short paragraph — what this week was, where it ends, what the weekend opens onto]

## Open Decisions
[5–8 numbered binary decisions ranked by leverage, each with current state + recommendation if Cowork has one]

## Active Ventures
- **Subastop** — exit thesis state + AI Ops slate + legal queue
- **CarMatch** — build cycle state
- **AVT** — live state
- **Voice Bridge (Symbios)** — IB state
- **APEX Desk v3** — build state
- **VMC** — SEO + BCP thread
- **LATIDO** — Layer state, streak count
- **SENSEI** — phase state
[Add or omit ventures based on the week's actual movement]

## Thread — Carry Forward
[The thread that's most alive entering the weekend. Two paragraphs max. What POPs is wrestling with. What's ready to land. What needs space.]

## Signal Summary
### Calendar — Weekend window (Sat–Sun Lima)
[List events or note the window is open]

### Gmail — Last 24h
[Operational signals only — VMC SEO surfaces, Subastop ops, BCP, Render/infra, anything tagged for action. Skip trading-research noise + personal Amazon orders unless they signal something.]

### Focus Queue — Last-Seen State
[Numbered list, top 5 active items with age]

### Project Signal Stream — Unresolved (recency-weighted)
[Cowork-Out artifacts staged, age, action needed]

## Carryover Note
[One paragraph closing the week. Sets the tone Browser Symbios will inherit.]

---
*Friday Handoff — Steering Wheel Protocol v1.1, Cowork → Symbios Chat, [date] 17:00 Lima.*
```

## 4. Confirmation receipt — PSS Cowork-Out

After CF entry writes successfully, also create a PSS entry in collection `883209bd-0cce-48e6-807e-c21622fe3716`:

- **Signal Title:** `Friday Handoff Fired — Week of [Monday date]`
- **Artifact Type:** `CF Entry`
- **Consumer Status:** `Staged`
- **Event Type:** `Update`
- **Project:** `Symbios Coworker`
- **Routed to Symbios:** `__NO__` (Browser will mark YES on auto-init read)
- **Resolved:** `__NO__`
- **Signal Date:** today
- **Source Path:** `cowork-friday-handoff scheduled task`
- **Next Action Needed:** `Browser Symbios reads on Saturday auto-init`
- **Details:** one-line summary linking to the CF entry just written + naming this as the Nth GAP-FH1 closure firing

## 5. What this handoff does NOT do

- No fabrication of week activity. If the week was thin, name the thinness in Carryover Note.
- No celebration. Friday-tone is a clean close, not a victory lap.
- No paraphrasing of POPs' own words. Quote verbatim if quoting at all.
- No structural advice for Saturday — that's Saturday's job. Friday gives substrate, not direction.
- No retrieval from layers Cowork can't verify (e.g. don't claim Aura graph state if `/graph-health` failed).

## 6. Output

- CF Active entry written, ID logged
- PSS Cowork-Out artifact written, ID logged
- Brief inline summary in this session's output naming what landed, gaps if any
- If any database query failed or returned unexpected schema, log [GAP] tag explicitly

End state: Browser Symbios opens Saturday morning to a fresh, week-aware CF Active entry tagged for it. The carrier function for the Friday→Saturday transition retires from POPs to the scheduled mechanism. The next quiet stretch doesn't break the bridge.