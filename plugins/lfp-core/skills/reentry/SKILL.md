---
name: reentry
description: >
  Re-entry protocol for multi-machine, multi-initiative builds. Reconstructs full operational
  context at the start of any session  what was built, what broke, what's blocked, and where
  to start. Use this skill whenever the user says "reentry", "/reentry", "hutch", "where were we",
  "reconnect", "morning session", "session start", "what's the state", "catch me up", "where are
  we", "what did we do last", "what's left", "bring me up to speed", "I'm back", or any variation
  of starting a new work session after a gap. Also trigger when the user mentions a machine by name
  (M1, M2, M3) alongside any state or status question. Fire even on casual openers like "ok let's
  get back to it" or "what were we building"  the re-entry need is almost always implicit at
  session start, not explicit.
metadata:
  intent: orient
---

# Reentry  Session Re-Entry Protocol

You are reconstructing operational reality for a builder who runs three parallel machines (M1, M2,
M3) across multiple initiatives. They have been away. Time has passed. State has drifted. Your job
is to close that gap in the shortest possible time with the highest possible accuracy.

This is not a summary. It is a launch pad.

---

## What to do

### Step 0: Mount check (run FIRST, before anything else)

In Cowork, a fresh session only sees the folders the user selected in the picker. If a required
folder isn't mounted, every downstream signal is partial and the briefing is built on sand. So gate
on mounts before gathering anything.

1. Detect what's mounted now:

```bash
ls -1 /sessions/*/mnt/ 2>/dev/null | grep -vE '^(outputs|uploads)$' | sort -u
```

2. Read the most recent continuity seed (from the memory directory or the project root
   `CONTINUITY_SEED.md`) and find its **Mount Manifest**. Compare the REQUIRED folders there
   against what's mounted now.
3. If any REQUIRED folder is missing, do NOT proceed to the full reconstruction. Lead the hutch with
   a MOUNTS block naming the exact picker folders to add, and stop there until the user mounts them:

```
MOUNTS    ACTION NEEDED

Missing required folders this session: [picker name], [picker name]
Add them in the Cowork folder picker, then say "reentry" again.
(Mounted now: [list]. Needed per last seed: [list].)
```

If there's no seed Manifest to compare against, just report what's mounted and continue -- you
can't gate on a requirement you don't have. If all REQUIRED folders are present, emit a one-line
`MOUNTS  OK` in the hutch and proceed.

### Step 1: Gather signals in parallel

Pull from every available source simultaneously. Don't wait for one before starting another.

**Memory layer** (highest fidelity  saved explicitly):
- Read all continuity seeds and data capsules from the memory directory
- Look for files tagged with machine identifiers (M1, M2, M3) or initiative names
- Note the timestamp on each  recency matters

**Project Inbox** (unread messages from other agents):
- Search Notion for "[This Project]  Inbox"
- Look for any message blocks with STATUS: UNREAD
- Surface these in the hutch under OVERNIGHT SIGNALS  another agent sent mail while you
  were away
- Format: "[N] unread from [Sender]  say 'you've got mail' to process"

**Notion** (project state):
- Search for pages related to active initiatives (Subastop, CarMatch, Symbios, and any others present)
- Look for task boards, build logs, open items, or status pages
- Flag any items marked blocked, in-progress, or overdue

**Slack** (overnight signals):
- Read recent messages in relevant channels since the user's last activity
- Surface: decisions made, blockers raised, questions asked, deployments or failures mentioned
- Focus on signal, not volume  one blocker mention beats ten status updates

**Calendar** (today's constraints):
- Check today's events
- Note anything that creates a hard deadline or time constraint on the build session

**Workspace files** (last-touched state):
- Check recently modified files in the workspace folder
- File timestamps are a proxy for what was actively being built last

### Step 2: Synthesize by machine thread

Organize everything you found into the three machine threads. Each thread gets:

- **Last known state**  what was being built or what happened last
- **Blocker**  what's stopping forward progress (if anything)
- **Next action**  the single most useful thing to do on this thread

If a thread has no recent signal, say so explicitly. "No recent signal on M2" is better than silence or fabrication.

### Step 3: Surface overnight signals

Anything that happened while the user was away goes here  Slack messages, Notion updates, calendar changes, or any external signal that affects today's work. Keep it tight: only things that change what the user should do.

### Step 4: Identify open decisions

Decisions that are blocking one or more threads. These are things that cannot be resolved by
building  they require a call, a choice, or a confirmation. Surface them clearly.

### Step 5: Deliver the hutch

Output the re-entry briefing in this exact format:

---

```

  REENTRY    [DATE]    [TIME SINCE LAST SESSION]   


MOUNTS    [OK  or  ACTION NEEDED: add (picker names)]

[One line. If OK, just "OK  [folder, folder] mounted". If action needed, name the
 missing picker folders and stop the briefing here until they are added.]

ACTIVE THREADS

M1  [Initiative/Context]
   State:   [What was being built or last known state]
   Blocker: [What's stopping progress  or "None"]
   Next:    [Single most useful action]

M2  [Initiative/Context]
   State:   [What was being built or last known state]
   Blocker: [What's stopping progress  or "None"]
   Next:    [Single most useful action]

M3  [Initiative/Context]
   State:   [What was being built or last known state]
   Blocker: [What's stopping progress  or "None"]
   Next:    [Single most useful action]

OVERNIGHT SIGNALS

[Bullet list of things that happened while the user was away.
 Only include if actionable or context-changing. Skip if nothing.]

OPEN DECISIONS

[Numbered list of decisions blocking build progress.
 Each one should name the initiative it's blocking and what the options are.
 Skip section if none.]

START HERE 
[One sentence. The single highest-momentum action available right now.
 Pick the thread with the clearest path forward and name the exact first step.]
```

---

## Principles

**Reconstruct, don't hallucinate.** If a source has no signal for a thread, say "no recent signal"
rather than inferring. The user knows their machines  they will catch a wrong reconstruction
immediately, and a false briefing is worse than an honest gap.

**Recency wins.** A continuity seed from last night beats a Notion page from last week. Weight
your synthesis by how recently the signal was produced.

**Blockers are first-class citizens.** A thread with a blocker shouldn't get a "next action" that
ignores the blocker. If it's blocked, the next action is either "resolve the blocker" or "switch
to a different thread."

**The START HERE line is the whole point.** After everything else, there should be one undeniably
clear thing to do first. If you genuinely can't determine it, say why  don't leave the user in
the same fog they came in with.

**Machine context is not always symmetric.** M1, M2, and M3 may be running completely different
initiatives or different layers of the same initiative. Don't force symmetry. Reflect what's
actually there.

**Mounts gate everything.** A briefing built while a required folder is unmounted is worse than no
briefing -- it looks authoritative but reads partial state. The mount check is Step 0 for a reason:
if it fails, the only correct next action is "mount these folders," not a thread reconstruction.

---

## Edge cases

**User specifies a machine:** "What's the state of M2?"  Run the full protocol but lead with that
machine. Still surface the others, collapsed if needed.

**User specifies an initiative:** "Where are we on CarMatch?"  Pull everything relevant to that
initiative across all machines. Format as a single-initiative deep dive instead of the three-thread
view.

**No memory found / first session:** If there are no capsules, seeds, or Notion pages for a
thread, say so. Ask the user what was last being worked on rather than fabricating state.

**User is on a fresh machine:** They may not have local files or memory on this instance. Lean
harder on Notion and Slack as the source of truth.

---

## Data source priority

When sources conflict, use this hierarchy:

1. Continuity seed (explicitly saved by the user  highest intent)
2. Data capsule (explicitly saved fact)
3. Slack message (real-time signal)
4. Notion page (structured but may lag)
5. Calendar (constraint, not state)
6. Workspace file timestamps (proxy signal  lowest confidence)

---

## After the hutch

Once the briefing is delivered, drop into assistant mode immediately. Don't ask what they want to
do  the briefing tells them. Let them respond and pick up the thread they choose. The skill's job
ends when the hutch is delivered.
