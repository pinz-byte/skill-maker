---
name: council-call
description: >
  Convene the APEX MASTERS Council into session for ONE ticker, on demand, from
  ANY surface  phone, Claude.ai Chat, or any Cowork machine. This is the
  portable front door to a live single-ticker audit. Trigger on "call the
  council on <ticker>", "convene the council for <ticker>", "council session on
  X", "summon the council on X", "/call-council NVDA", "request a council audit
  of X", "get me the council read on <ticker>", or any request to start a fresh
  single-asset Council verdict from wherever the user is. If a local apex-ultra
  pipeline is reachable (M1) it runs the audit immediately; otherwise it queues
  the request in the Notion Council Requests database and the M1 watcher produces
  the verdict, which the user then reads back from Notion. NOT a cached-tier
  display (use council / council-global) and NOT files-free reasoning (use
  apex-ultra-council). This skill triggers real work and consumes its result.
---

# Council Call  convene a live session on one ticker, from anywhere

The portable trigger. The user names a ticker; this skill gets a fresh 7-voice
Council verdict back to them no matter what surface they are on. The heavy work
runs where it can (the M1 executor); this skill is the front door and the
consumer.

## Contract  the Council Requests queue

- Database: `Council Requests`  https://www.notion.so/263984f0649f4b5e91b2e07a30855bf7
- Data source (use for create/query): `c36b164a-f594-4a3c-bb77-6f3aa1f33876`
- Properties: `Ticker` (title), `Status` (QUEUED/RUNNING/DONE/ERROR), `Mode`
  (LIVE/OUTLOOK/AUTO), `Requested By` (text), `Requested At` (created time),
  `Completed At` (date), `Result` (text  verdict summary), `Notes` (text),
  `Req ID` (auto id, prefix CR).
- The executor writes the verdict SUMMARY into `Result` and the FULL debate
  transcript into the request page's BODY (Result property is length-limited).

## Step 1  Get the ticker

Parse the ticker symbol from the request. If none was given, ask for it. Never
convene the council on nothing.

## Step 2  Branch on environment

**If you have shell access AND the apex-ultra pipeline is present locally** (this
is M1  verify with `ls /Users/usuario/Documents/Claude/Projects/apex-ultra` and
`/opt/homebrew/bin/python3.13 --version`):

Run the audit now and present the output verbatim  the user gets it instantly,
no queue needed:

```
cd /Users/usuario/Documents/Claude/Projects/apex-ultra
/opt/homebrew/bin/python3.13 council.py <TICKER>
```

(Market closed -> the pipeline returns an OUTLOOK; label it NON-EXECUTABLE.)
Optionally also log a DONE row to the queue for the record. Then stop.

**Otherwise** (phone, Claude.ai Chat, M2/M3  no local pipeline): you cannot run
the audit here. Queue it instead. Create a row in the Council Requests data
source:

- `Ticker` = the symbol (uppercase)
- `Status` = `QUEUED`
- `Mode` = `AUTO` (let the executor pick LIVE vs OUTLOOK by market hours)
- `Requested By` = the surface/machine you are on (e.g. "APEX chat / iPhone")

Then tell the user: request CR-NN is queued; the council will run on the M1
executor; check back shortly and say "read the council result for <TICKER>" (or
re-call this skill) to consume it.

## Step 3  Consume a result

When the user asks to read a result (or after queuing), query the data source
for the matching `Ticker` (newest, or by `Req ID`):

- `Status` = `DONE` -> present the `Result` summary, then open the request page
  body for the full 7-voice transcript and present it.
- `Status` = `QUEUED` or `RUNNING` -> tell the user it is still in flight; the
  executor has not finished. Do not fabricate a verdict.
- `Status` = `ERROR` -> show the `Notes` field (what failed) and offer to requeue.

## Hard truths (do not paper over)

- **The executor must be awake.** Queued requests only get answered when the M1
  watcher is running and M1 is online. A phone cannot wake a sleeping Mac. If a
  request sits in QUEUED with no movement, the executor is down  say so plainly
  rather than waiting silently.
- **This skill never invents a verdict.** Off-M1 it only queues and reads. The
  only place a real verdict is produced is the executor running `council_decide`.
- **A printed GO is a recommendation, not an order.** Nothing here files a trade.

## Relationship to the other council skills

- `council-call` (this)  convene one ticker from anywhere; runs local on M1, else queues.
- `council-global`  read today's cached tiers for all tickers (read-only).
- `apex-ultra-council`  files-free 7-voice reasoning when no pipeline is reachable; label as non-live.
- `council-debate`  the local M1 invocation; superseded as a user-facing trigger by this skill (its invocation logic is reused here and by the watcher).
