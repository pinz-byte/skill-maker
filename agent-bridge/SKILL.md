---
name: agent-bridge
description: >
  Project-to-project messaging system for Claude agents across M1, M2, and M3. Every project
  has a permanent Notion inbox. Agents send messages directly to another project's inbox and
  respond to messages in their own. The only trigger the user ever needs is "you've got mail"
  or "check your inbox" — the agent reads, acts, and responds automatically. Use this skill
  whenever the user says "you've got mail", "check your inbox", "send this to [project]",
  "message [project] about", "tell [project] that", "forward this to", "does [project] have
  mail", or any request to pass information or a question from one project to another. Also
  trigger when the user says "got mail?" or just "mail". This is the connective tissue of the
  ecosystem — every cross-project communication routes through inboxes, not through the user.
---

# Agent Bridge — Project Mail System

Every project in the ecosystem has a permanent inbox in Notion. Agents send mail. Agents read
mail. Agents respond to mail. The user's only job is to say "you've got mail" — everything
else is autonomous.

**The user routes. Agents execute. No IDs. No copy-paste. No relay.**

This system connects agents across ALL environments — Cowork (M1, M2, M3) and Claude.ai Chat
projects. The transport layer is Notion, which both environments can read and write. Host
context travels with every message so replies always know where to go.

---

## The two things you'll ever do

**SEND** — You have something another project needs to know or act on.
Trigger: *"Send this to Herald"* / *"Message Push Notifier about X"* / *"Tell Subastop that..."*

**RECEIVE** — You have a message waiting.
Trigger: *"You've got mail"* / *"Check your inbox"* / *"Got mail?"*

---

## Inbox structure

Every project has one permanent Notion page named exactly:
```
 [Project Name] — Inbox
```

Examples:
- ` Herald — Inbox`
- ` Push Notifier — Inbox`
- ` Subastop — Inbox`
- ` CarMatch — Inbox`
- ` Sensei — Inbox`
- ` Symbios — Inbox`

The page lives at Notion workspace root. Create it if it doesn't exist — it should be permanent
and bookmarkable. Its structure is a running log of messages, newest at the top.

---

## Inbox Registry

Every inbox in the ecosystem has a permanent UUID. Always use the UUID in REPLY TO — name
strings are not reliably searchable across environments. If you don't know a project's UUID,
look it up in this registry before sending.

<!-- INBOX_REGISTRY:START (generated from .claude/rules/inbox-registry.md -- run gen-inbox-registry.py; do not edit by hand) -->
| Project | Host | Notion Inbox UUID |
|---|---|---|
| SKILL MAKER | Cowork M2 | `360da327-abb1-8196-b98d-cfc86bbe0ec6` |
| Herald | Cowork M3 | `360da327-abb1-819d-850b-e86dc3293e94` |
| Push Notifier | Cowork M3 | `360da327-abb1-81ab-96a9-f83bdb93acc0` |
| Subastop | Cowork M1 | `360da327-abb1-81a1-825b-ddf7555604ee` |
| CarMatch | Cowork M2 | `360da327-abb1-815c-8975-d044371bf23c` |
| Sensei | Cowork M1/M2 | `360da327-abb1-81a8-8df0-f1321e578d4d` |
| Symbios | Claude.ai Chat | `360da327-abb1-8115-bf58-fcaec470ec53` |
| APEX DESK | Claude.ai Chat | `360da327-abb1-816c-8df5-e02f45e3bbde` |
| Life Archive | Claude.ai Chat | `360da327-abb1-8180-8894-e65c44b1ad83` |
| Second Self | Claude.ai Chat | `360da327-abb1-81a7-b342-c1f2f4f35495` |
| AVT CarMatch | Cowork M2 | `360da327-abb1-81a8-828f-db2745d30667` |
| Extractor | Cowork M2 | `360da327-abb1-8139-9b22-f98155a3b600` |
| VMC | Cowork M3 | `360da327-abb1-81bf-80d5-d910c59b9476` |
| Agency | Cowork M3 | `360da327-abb1-8169-9ca2-cb6ef0d0d04d` |
| Echo Chamber | Cowork M3 | `360da327-abb1-8131-b1df-d35f9d395a91` |
| Carta Natal OS | Cowork M3 | `360da327-abb1-81f5-a0ed-e5fd571f01f1` |
| Tenant Farm | Cowork M3 | `360da327-abb1-819a-9206-ce785d2d6547` |
| Subascars | Cowork M3 | `360da327-abb1-81f1-82ac-ca47d195312f` |
| apex-ultra | Cowork M1 | `368da327-abb1-817e-9d0c-ce184ee0a69b` |
<!-- INBOX_REGISTRY:END -->

**Rule:** when sending, always include your own UUID in `REPLY TO`. When receiving, use the
UUID directly to fetch the sender's inbox — never rely on name search alone.

---

## SEND mode

### Step 0 — Check your own inbox first (concurrency gate)

If your message asks a question, fetch YOUR own inbox before composing — the answer may
already be sitting there UNREAD, crossed in flight or answered preemptively. A fetch costs
seconds; a duplicated question costs a full round-trip between machines. Pure notifications
(no question asked) can skip this step.

### Step 1 — Compose the message

A good message is short and precise. Three parts:

- **FROM** — who you are and what machine you're on
- **WHAT** — the information, question, decision, or task — include full payload if needed
  (prompts, specs, code snippets, anything the recipient needs to act without asking follow-ups)
- **WHAT YOU NEED BACK** — what action or response you expect, if any. If none, say so.

### Step 2 — Find or create the recipient's inbox

Search Notion for `[Project Name] — Inbox`. If it doesn't exist, create it as a standalone
page at workspace root with the title ` [Project Name] — Inbox`.

### Step 3 — Write the message to the inbox

Prepend a new message block at the top of the inbox page (newest first):

```
---
 NEW MESSAGE
FROM: [Your project]
HOST: [Cowork M1 / Cowork M2 / Cowork M3 / Claude.ai Chat]
TO: [Recipient project]
DATE: [YYYY-MM-DD HH:MM]
STATUS:  UNREAD

[Full message content — include everything the recipient needs to act autonomously.
No follow-up questions should be necessary after reading this.]

ATTACH: [optional — see ATTACH format below. Omit if no assets.]

EXPECTS RESPONSE: [Yes — [what you need back] / No]
REPLY TO: [Your project] — Inbox (UUID: [page-uuid])
---
```

### Step 4 — Notify via Slack (optional — never block if unavailable)

If `#agent-bridge` exists on this workspace, post:
```
 [Recipient project] — you've got mail from [Your project]
```
One line. That's all. The content lives in Notion.

### Step 5 — Tell the user

```
Message sent to [Project]'s inbox.
Tell them: "you've got mail"
```

That's the only thing the user needs to carry — three words.

---

## RECEIVE mode

Triggered by: *"you've got mail"* / *"check your inbox"* / *"got mail?"*

### Step 1 — Find your inbox

Search Notion for `[Your Project Name] — Inbox`. Fetch the page.

### Step 2 — Read all unread messages

Find every message block with `STATUS:  UNREAD`. Read them all. Process newest first.

### Step 3 — Act autonomously on each message

This is the core of your job. For each unread message:

- Read the full content
- **If ATTACH is present** — fetch each asset before acting. Images: describe and interpret.
  Documents: read and extract relevant content. Design files: pull design context. Act on
  the asset as part of the message — don't treat it as optional.
- Go into your domain — codebase, config, knowledge — and do the work
- **Surface what the sender didn't know to ask.** Check for constraints, edge cases, failure
  modes, or dependencies they couldn't see from their side. This is the most valuable thing
  you can add. A response that only answers the question asked is half a response.
- Execute whatever falls within your authority

### Step 4 — Mark each message as read (immediately, never batch)

Update the STATUS field **immediately after acting on each message — not in a batch at the
end of the run**:
```
STATUS:  READ — [YYYY-MM-DD HH:MM]
```

Why: a session that dies mid-run with batch marking leaves already-processed messages
looking UNREAD. They get re-processed on the next run and surface as stale unmarked copies
(observed in production 2026-07-02).

### Step 5 — Send a response (if expected)

If `EXPECTS RESPONSE: Yes` — find the sender's inbox (search for `[Sender Project] — Inbox`)
and write a response message following the same format:

```
---
 RESPONSE
FROM: [Your project]
HOST: [Cowork M1 / Cowork M2 / Cowork M3 / Claude.ai Chat]
TO: [Sender project]
DATE: [YYYY-MM-DD HH:MM]
RE: [One-line summary of what you're responding to]
STATUS:  UNREAD

[Your response — decisions made, actions taken, constraints surfaced, open items if any]

ATTACH: [optional]

EXPECTS RESPONSE: [Yes / No]
REPLY TO: [Your project] — Inbox (UUID: [page-uuid])
---
```

### Step 6 — Re-fetch before you report (concurrency gate)

Before writing the session summary, fetch your own inbox ONE more time:

- New mail may have arrived while you were working.
- Anything you were about to report as "pending" may already be answered.

Never declare "still pending" based on the Step 1 fetch. Verified failure (2026-07-02): an
agent reported its question as still pending in the other project's inbox while the complete
answer was already sitting UNREAD in its own inbox — the two messages crossed in flight by
minutes, and the user carried a false pending item between machines. That false relay is
exactly what this system exists to eliminate.

### Step 7 — Tell the user

Deliver a direct summary in the current session:

```
 [N] message(s) read from [Sender(s)].

[For each message:]
From: [Project]
Topic: [one line]
Action taken: [what you did in your domain]
Sent response: [Yes/No — summary of response if yes]
Unseen constraints surfaced: [if any — this is important]

[If you sent responses:]
Tell [Sender]: "you've got mail"
```

The last line is what the user carries to the next machine. Three words.

---

## Inbox maintenance

**Read messages** stay in the inbox permanently — they're the conversation history.
Don't delete them. The inbox is also an audit trail.

**Thread replies** — if a conversation spans multiple exchanges, each response references
the previous with `RE:` so the thread is readable in sequence.

**Stale unread messages** — if a message has been UNREAD for more than a session, the reentry
hutch will surface it as a pending item. Nothing gets lost.

---

## Setting up inboxes for the first time

The first time any project uses this skill, create its inbox page in Notion:

1. Search for `[Project] — Inbox` — if not found, create it
2. Add a pinned header at the top of the page:

```
#  [Project Name] — Inbox
This is the permanent inbox for [Project] on [Machine].
Messages from other projects arrive here.
Trigger: tell this agent "you've got mail" to process new messages.
```

3. That's it. The inbox is ready.

**Ecosystem inboxes to create on first use:**
-  Herald — Inbox
-  Push Notifier — Inbox
-  Subastop — Inbox
-  CarMatch — Inbox
-  Sensei — Inbox
-  Symbios — Inbox

Add more as new projects join the ecosystem.

---

## Cross-environment messaging — Cowork ↔ Claude.ai Chat

The bridge works across both agent environments. Notion is the shared layer — both Cowork
and Claude.ai Chat projects can read and write to it.

### Host types

| Host value | Where the agent lives |
|---|---|
| `Cowork M1` | Cowork desktop app, machine 1 |
| `Cowork M2` | Cowork desktop app, machine 2 |
| `Cowork M3` | Cowork desktop app, machine 3 |
| `Claude.ai Chat` | Claude.ai browser, any Chat project |

### How a Chat agent sends to a Cowork agent

A Chat project (e.g. Symbios, APEX DESK, Optimizer) can send to any Cowork inbox:

1. The Chat agent searches Notion for `[Cowork Project] — Inbox`
2. Writes a message with `HOST: Claude.ai Chat`
3. Tells the user: *"Tell [Cowork project]: you've got mail"*
4. The user opens Cowork, switches to that project, says "you've got mail"
5. The Cowork agent reads, acts, and responds to the Chat inbox

### How a Cowork agent sends to a Chat agent

A Cowork project (e.g. CarMatch, Herald) can send to any Chat project inbox:

1. The Cowork agent searches Notion for `[Chat Project] — Inbox`
2. Writes a message with `HOST: Cowork M[n]`
3. Tells the user: *"Tell [Chat project]: you've got mail"*
4. The user opens Claude.ai Chat, switches to that project, says "you've got mail"
5. The Chat agent reads the Notion inbox, acts, and responds

### What the Chat agent needs

Chat projects don't have the agent-bridge skill installed (skills are Cowork-only). But
any Claude.ai Chat agent can still participate in the bridge if you tell it:

> "Check my Notion inbox — search for '[Your Project] — Inbox' and read any unread messages,
> then respond following the same message format."

For Chat projects that regularly use the bridge, add this instruction to their project
system prompt so they're always bridge-aware without being told each time.

### The user's job in cross-environment sends

Identical to same-environment sends: carry three words between environments.
`"you've got mail"` works in Cowork and in Chat. The agent figures out the rest from the
HOST field in the message.

---

## ATTACH — sending assets with messages

The `ATTACH:` field is optional. Include it when your message references an asset the
recipient needs to act on — an image, a document, a design, a spec, a dataset.

### Format

One asset per line, each with a label and a pointer:

```
ATTACH: [label] → [URL or Notion page ID or file path]
```

Multiple assets:
```
ATTACH:
  - [Screen mockup] → https://figma.com/file/...
  - [API spec] → https://notion.so/...
  - [Reference image] → https://drive.google.com/...
```

### Asset types and how the recipient handles them

| Type | Pointer format | Recipient action |
|---|---|---|
| Image (public URL) | `https://...` | Fetch and visually interpret |
| Figma design | Figma share URL | Use Figma MCP to pull design context |
| Notion page | Notion URL or page ID | Fetch and read full content |
| Google Drive file | Drive share URL | Fetch via browser or Drive MCP |
| Local file (same machine) | Absolute file path | Read directly |
| GitHub file | Raw GitHub URL | Fetch content |

### Screen briefings — sending screenshots without a URL

If the asset is a screenshot or image that exists only in the sending session (uploaded
directly to chat, captured from screen), do NOT try to host it externally. Instead, the
sending agent interprets the image and encodes it as a SCREEN BRIEFING block in the message
body. The recipient gets full visual fidelity as structured text.

Format:

```
SCREEN BRIEFING (interpreted by [Your project] agent from live screenshot):
- Environment: [app, URL, or context]
- [UI element]: [state and content]
- [UI element]: [state and content]
- [Key data visible]: [values]
- [Any anomalies or notable states]: [description]
- Note: [anything NOT visible that the recipient should know is absent]
```

Rules for screen briefings:
- Be exhaustive — describe every visible element, value, and state the recipient needs
- Explicitly note what is NOT visible if absence is meaningful (e.g. "only 4 of 9 files shown")
- The recipient treats the briefing as equivalent to seeing the screen directly
- Set ATTACH to "none (screenshot interpreted inline above)" when using this pattern

### Rules

**Sender:** include only assets the recipient genuinely needs. One focused asset beats
five tangential ones. Label every asset so the recipient knows what it is before fetching.

**Recipient:** if an ATTACH is present, fetching it is not optional — it is part of the
message. An unfetched attachment is an unread message. If a fetch fails, surface it in
your response: `ATTACH FAILED: [label] — [reason]` and continue with what you have.

**Responses can also carry attachments.** Use the same ATTACH format in response messages
when the reply includes assets the sender needs (a revised mockup, an updated spec, etc.).

---

## Reentry integration

The `reentry` skill checks your inbox at every session start. If there are unread messages,
they surface in the hutch under OVERNIGHT SIGNALS:

```
 INBOX — [N] unread message(s)
  • From [Project]: [topic] — say "you've got mail" to process
```

So even if you forget to check, the hutch reminds you.

---

## Principles

**Three words is the interface.** "You've got mail." That's all the user carries between
machines. The content, the context, the response — all of it lives in Notion.

**Full payload, no follow-ups.** When you send a message, include everything the recipient
needs to act without asking you anything. Incomplete messages create the same relay problem
we're trying to eliminate.

**Autonomous on receipt.** When you get mail, you don't summarize and ask — you read, act,
and respond. The user said "you've got mail," not "tell me what the mail says."

**Surface the unseen.** The most valuable thing a receiving agent can do is flag what the
sender didn't know to ask. Always look for constraints, edge cases, and dependencies from
your domain that the other side couldn't see.

**Notion is permanent. Slack is optional.** The inbox lives in Notion forever. Slack is a
convenience ping. Never let a missing Slack channel block a message from being sent or received.

**Assume concurrency, not turns.** Multiple agents run the same day and messages cross in
flight. Session memory expires the moment another agent writes to Notion. Any "pending" or
"no response yet" you report must be verified against a fresh fetch of your own inbox —
never against what you saw at the start of the session.
