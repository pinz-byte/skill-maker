---
name: builder-handoff
description: >
  Converts work Cowork's sandbox can't or shouldn't execute (prod secrets, real-machine deploys,
  gcloud/firebase CLI against live infra, anything blocked by sandbox/security doctrine) into a
  BUILDER_PROMPT file plus a short paste-ready kickoff message for a builder session (Claude Code
  or similar) to run autonomously  instead of handing the user a manual runbook to type
  themselves. Use whenever Cowork is about to present a multi-step terminal sequence for the USER
  to run because of a sandbox limitation, or the user says "make the builder do this," "hand this
  off," "prompt for him/it," "don't make me do this by hand," "automate the handoff," or
  "delegate this." Fires proactively too: if Claude is about to write "here's what you run in
  your terminal" as a list aimed at the human, that's the trigger  stop, check if a builder
  session could run it instead.
  NOT live-builder-bridge (live PTY supervision of a running builder): this packages work the sandbox cannot execute into an async handoff for a real machine.
metadata:
  intent: manage
---

# Builder Handoff

## The moment this fires

Cowork sandboxes exist for a reason  they keep prod secrets, write-capable credentials, and
irreversible infra actions away from an AI session that can't be fully audited in real time.
That constraint is correct and this skill does not weaken it.

But the constraint has a side effect worth catching: when Claude hits something it can't do
itself, the easy failure mode is to just *hand the human the commands*  "run this in your
terminal, then this, then this." That solves Claude's access problem by creating a new one:
now a human is doing mechanical labor that an agent could do, just not this particular sandboxed
one. The fix isn't for Claude to do the forbidden thing anyway  it's to write the work as an
**executable spec for a different, appropriately-privileged agent** (a Claude Code session
running on the real machine, in this ecosystem usually called "the builder"), and hand the human
a one-line trigger instead of a multi-step checklist.

The tell that this should fire: you're about to write a response structured like "1. run X,
2. run Y, 3. run Z" where X/Y/Z are commands *for the user* to execute because *you* can't. That
structure is the trigger. Stop, and ask: could a builder session run this whole thing instead?

## When NOT to do this

Not everything that looks like a runbook should become a builder handoff:

- **Genuinely trivial actions**  a single harmless command, a 10-second lookup. Writing a whole
  BUILDER_PROMPT file for `ls ~/Downloads` is more overhead than the task. If it's one line and
  low-stakes, just tell the user directly.
- **Decisions, not mechanics.** If the next step requires a judgment call only the human can make
  (which of three architecture options, whether to accept a tradeoff, who to talk to), that's not
  delegable  get the decision first, *then* the resulting mechanical work can become a handoff.
- **Things no agent can do**  calling a vendor, physically checking something, anything outside
  any agent's reach regardless of privilege level.

If the task is mechanical, well-specified once the "how" is known, and blocked purely by *where*
it needs to run rather than *who* needs to decide something  that's the signal to delegate.

## What to produce

Two things, every time:

### 1. A `BUILDER_PROMPT_<slug>_<date>.md` file

Save it in the same repo/directory as the work it concerns, so it's discoverable in context next
to everything else. Before writing a new one, check whether the project already has
`BUILDER_PROMPT_*.md` files elsewhere  if so, match their existing structure and tone rather
than inventing a new convention; consistency across a project's builder prompts matters more than
any single file being individually elegant.

If there's no existing convention to match, use this shape:

```markdown
# BUILDER PROMPT  <what this accomplishes>
> <date>  **EJECUCIN: <where this runs and why>**  Tipo: <one line, what kind of operation>

## Por qu
<the context a builder needs to not need to ask "why am I doing this" mid-task  what problem
this solves, what it unblocks, what happens if it's skipped>

## <Hard rule section  only if secrets/credentials are involved>
State plainly what must never happen: printed, logged, committed, or reported back to chat.
Explain *why* rather than just capitalizing NEVER  a builder that understands the reasoning
handles edge cases the letter of the rule didn't anticipate; one that's just following a rule
doesn't.

## Tareas / Tasks
Numbered, in execution order, with **exact copy-paste commands**  not descriptions of commands.
A builder should never have to reconstruct a gcloud invocation from prose. Include the expected
output at each verification point, and what a *wrong* output looks like, so the builder can tell
the difference between "this worked" and "this silently didn't."

Build in explicit stop conditions: if the same check fails twice with the same error, that's a
signal to escalate, not to retry a third time with a guess. Say so directly in the file.

## Aceptacin / Acceptance
Concrete and checkable  not "looks good," but a specific observable state (a URL returns real
data instead of a placeholder, a count matches an expected range, a file exists with the right
shape). If the acceptance criteria can't be checked without human judgment, that's worth noting
explicitly rather than pretending it's automatable.

## Guardrails
Explicit scope boundaries. What this builder should NOT touch, even if it seems related or
convenient mid-task. This is what prevents a builder from quietly expanding scope into adjacent
work nobody reviewed.
```

### 2. A short kickoff message, given directly in your response

Not the whole file restated  a pointer plus the one or two guardrails that matter most if
someone forgets them. Something the user can literally copy into a fresh builder session with no
editing. Example shape:

> Read `BUILDER_PROMPT_<slug>_<date>.md` in this directory and execute it end to end. Follow its
> guardrails exactly: [restate the one or two highest-stakes rules  usually the secret-handling
> one]. Stop and report if [the specific failure condition] happens  don't retry blindly.

Keep this short. The file carries the detail; the kickoff message just has to get the builder to
open it and start.

## A worked example

From this ecosystem (VMC/DashLord project): Cowork identified that deploying a Cloud Function
required a real API key sitting in a local, gitignored `config.js` that must never enter a
sandbox session. Instead of telling the user "run `cat config.js`, copy the key, then run these
five gcloud commands yourself," the handoff was:

- `BUILDER_PROMPT_avt_proxy_deploy_2026-07-08.md`  full sequence (read key locally  Secret
  Manager  deploy  smoke test  wire into config  build + deploy hosting), with a standalone
  "the key value never leaves this terminal" rule stated once, up front, with the reasoning
  (routing it through any AI session  including the one writing the prompt  defeats the point
  of keeping it out of sandboxes at all).
- A three-sentence kickoff message restating that one rule plus the stop condition, ready to
  paste into a fresh Claude Code session on the real machine.

The user's role shrank from "execute an 8-step runbook" to "paste one message." The actual
mechanical work still happened somewhere appropriately privileged  it just didn't require the
human to be the one typing it in.

## Naming and scope discipline

`BUILDER_PROMPT_<slug>_<date>.md`  slug describes the task, not the tool ("avt_proxy_deploy",
not "gcloud_stuff"). Date it. If a project already has a `BUILDER_PROMPT_*` for closely related
work, consider whether this is really a new prompt or an update to the existing one  proliferating
near-duplicate builder prompts for the same underlying task creates the same "which one is current"
confusion that stale docs cause everywhere else.
