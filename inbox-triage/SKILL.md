---
name: inbox-triage
description: >
  Surfaces what is waiting in this project's Notion inbox WITHOUT processing it -- the
  read-only counterpart to agent-bridge RECEIVE. Extracts only FROM + DATE + subject +
  EXPECTS RESPONSE per unread message, collapses repetitive automated dispatches into a
  single count, prints a compact triage under 10 lines, then STOPS and waits. Use when the
  user wants to see the inbox before acting: "triage my inbox", "what's in my inbox", "any
  mail waiting", "scan the inbox", "what's waiting", "inbox status", "summarize my inbox".
  Also fires as a sub-step of arise on cold session open, emitting one line. Does NOT act --
  to read, act, and respond the user invokes agent-bridge ("process [sender]", "process
  all", "you've got mail"). Never fires mid-session on a task continuation; only on explicit
  triage intent or cold-open. Pairs with agent-bridge: that skill acts, this one surfaces --
  same inbox, partitioned triggers so no phrase means both.
metadata:
  type: comms
---

# Inbox Triage -- surface, don't act

## What this is
The read-only front door to your project inbox. agent-bridge RECEIVE reads every unread
message, goes into your domain, acts, and responds -- valuable but expensive (a 37-message
inbox is a 20-minute detour). inbox-triage answers a smaller question: *what is waiting?*
It surfaces a compact list and stops. You decide what, if anything, to process.

## How it works
1. Fetch the project inbox (same Notion page agent-bridge uses; UUID from
   `.claude/rules/inbox-registry.md`).
2. For each `STATUS: UNREAD` block, extract ONLY: FROM, DATE, subject/RE, EXPECTS RESPONSE.
   Do not read message bodies -- that is the expensive step this skill exists to defer.
3. Collapse repetitive automated dispatches (apex-ultra council posts, scheduled pushes)
   into a single `[N automated dispatches]` line.
4. Print a compact triage, newest first, in under 10 lines.
5. STOP. Do not act, do not respond, do not mark read. Wait for an explicit instruction.

## Output shape
```
INBOX -- [N] unread ([M] need response)
- [DATE] FROM -- subject  [needs response]
- [DATE] FROM -- subject
- [N automated dispatches -- apex-ultra]
Say "process [sender]" or "process all" to act (hands off to agent-bridge).
```

## Large inboxes
If the inbox exceeds ~200k chars, do NOT pull the whole page into the main context.
Offload to a subagent that greps for `UNREAD` markers and returns only the extracted
header fields. This is a FALLBACK at the size threshold -- not the default. For a normal
inbox the direct fetch is cheaper than spinning a subagent.

## Relationship to arise and agent-bridge
- `arise` calls this skill as a sub-step on cold session open and prints ONE line
  (`INBOX -- N unread, M need response`). It does not patch arise's logic; arise invokes
  it explicitly. inbox-triage ships standalone with its own trigger surface.
- agent-bridge owns the ACT verbs ("you've got mail", "got mail?", "process [sender]",
  "process all"). inbox-triage owns the SURFACE verbs ("triage", "what's waiting", "scan
  the inbox"). The trigger surfaces are partitioned on purpose -- no overlap, so the same
  phrase never means both "show me" and "do it".

## Principles
- Surface, never act. The moment this skill acts on a message it has become agent-bridge
  and defeated its own purpose.
- Headers only. Reading bodies is the cost this skill defers; never read a body to triage.
- Honest counts. If the inbox fetch fails, say so -- never report "inbox clear" on a failed
  read (same honesty band as the rest of the ecosystem).
- Never auto-fire mid-session. Only explicit triage intent or a cold-open arise call.

## Edge cases
- Zero unread -> one line: "INBOX -- clear." Don't elaborate.
- A message with no EXPECTS field -> surface it, default to "needs response" (safer than
  silently dropping it).
- Mixed automated + human mail -> collapse only the automated cluster; every human message
  gets its own line.
