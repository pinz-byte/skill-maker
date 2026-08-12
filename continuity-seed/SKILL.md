---
name: continuity-seed
description: >-
  | Generates a structured handoff document for cross-session continuity -- designed to be
  loaded into a fresh Claude session to resume work at full speed with zero re-discovery. Use
  this skill whenever the user says "seed", "continuity seed", "save state", "generate a
  seed", "handoff", "session handoff", "save my progress", "I'm about to run out of context",
  "before we lose this", "wrap this up for next session", "create a checkpoint", "checkpoint
  this", or any request to preserve workflow state for a future session. Also trigger when the
  user says "I need to start a new chat" or "context is getting heavy". This is NOT the same
  as /compact -- compact compresses context within a session to free space. Continuity-seed
  creates a loadable briefing for a NEW session. Use continuity-seed at session boundaries.
  Use compact mid-session. If unsure which one the user wants, ask. NOT reentry, which
  reconstructs state from the machines: this one writes the briefing.
metadata:
  intent: orient
---

# Continuity Seed -- Cross-Session State Transfer

Generates a structured document that lets a fresh Claude session resume exactly where this one
left off. The output is not a summary -- it's an executable briefing optimized for Claude to
consume, with enough context to skip all re-discovery.

## Why This Exists

Long sessions degrade. After ~3,000 events, Claude starts losing track of decisions, repeating
work, and making errors it wouldn't make fresh. The fix isn't to fight the context ceiling -- it's
to make session transitions seamless. A good seed means the next session starts at 95% of where
this one ended, not at 0%.

The difference from `/compact`:
- **Compact** = lossy compression for the current session (free up space, keep working)
- **Continuity Seed** = lossless state serialization for the next session (preserve everything that matters, start fresh)

## The Mount Problem (read this -- it is the #1 seed failure)

In Cowork, a fresh session only sees the folders the user has selected in the folder picker.
A seed generated in a session with three folders mounted, loaded into a session with one folder
mounted, produces the recurring error: **"X source isn't mounted this session."** The next
Claude then either stalls or silently works against partial state.

Two root causes, both fixed by this skill:

1. **No mount record.** The old seed captured a single "Working directory" and never listed the
   *other* folders the work depended on. The next session had no way to know what to mount.
2. **Rotating session paths.** Absolute paths like `/sessions/<name>/mnt/...` change every
   session. A seed that hardcodes one is dead on arrival. **Always record folders by their
   stable, user-facing picker name** (e.g. `AVT CarMatch meta`, `extractor`, `SKILL MAKER`) --
   never by the session-scoped absolute path.

The seed therefore carries a **Mount Manifest**: the exact list of folders the next session must
have selected before any work begins, and a load-time gate that checks them first.

## When to Trigger

Trigger this skill when:
- The user explicitly asks for a seed/handoff/checkpoint
- Context usage is above ~70% and there's still work to do
- The user says they need to start a new chat
- A natural breakpoint is reached (feature complete, deploy done, blocked on external)

If context is heavy and the user hasn't asked, suggest it:
> "We're getting deep into context. Want me to generate a continuity seed before we lose fidelity?"

## Step 1 -- Gather State

Before generating the seed, collect this information from the conversation and the environment.
Use tools to fill gaps -- don't rely on memory alone.

### From the conversation:
- What task(s) were being worked on
- What decisions were made (and why)
- What was completed
- What's still in progress or blocked
- What errors/gotchas were discovered
- Any user preferences or corrections expressed during the session

### From the environment (run these commands):

```bash
# Project identity
basename "$(pwd)"
git remote get-url origin 2>/dev/null || echo "no git remote"

# Current branch and status
git branch --show-current 2>/dev/null
git status --short 2>/dev/null

# Recent commits from this session (last 5)
git log --oneline -5 2>/dev/null

# Any uncommitted work
git diff --stat 2>/dev/null
```

## Step 1.5 -- Capture the Mount Manifest (REQUIRED for Cowork)

This is the section that prevents the "source isn't mounted" failure. Do it for every seed.

### Detect what is mounted right now

```bash
# List the stable, user-facing names of every mounted Cowork folder
# (excludes the session-scratch folders outputs/ and uploads/)
ls -1 /sessions/*/mnt/ 2>/dev/null | grep -vE '^(outputs|uploads)$' | sort -u
```

Each name printed is exactly what the user selected in the folder picker, and exactly what they
must re-select next session. Record those names verbatim.

### Decide REQUIRED vs OPTIONAL

For each mounted folder, judge from the session whether the work actually depends on it:
- **REQUIRED** -- the next steps read or write files here. Missing it = hard stop.
- **OPTIONAL** -- referenced for context but not on the critical path.

Also flag any folder the work needs that was **NOT** mounted this session but should be next time
(e.g. a sibling repo you had to ask the user about). The AVT case -- "extractor repo not mounted,
only the meta workspace" -- belongs here so the next session knows to request it up front.

### For each REQUIRED folder, anchor by content, not path

Record one or two stable landmark files that live inside the folder (e.g.
`catalog_versioned_normalized.json`, `scripts/`, `build-marketplace.py`). This lets the next
session confirm the right folder is mounted even if the user renamed it in their picker.

## Step 2 -- Generate the Seed

Follow the exact section structure and a fully worked example in
`references/seed-template.md` — every section earns its place, omit only if genuinely empty,
and the **Mount Manifest** is never omitted in a Cowork session. Read that file before writing
the seed if you don't already have the structure memorized.

## Step 3 -- Save and Deliver

### 3a -- Save to project directory

Save the seed to the primary folder's root so it persists across sessions. Use the mounted path
that resolves this session; the next session will find it by the stable folder name, not this path:

```bash
cp seed.md "$(ls -d /sessions/*/mnt/[PRIMARY_FOLDER] | head -1)/CONTINUITY_SEED.md"
```

If there's already a `CONTINUITY_SEED.md`, rename the old one first:

```bash
mv CONTINUITY_SEED.md "CONTINUITY_SEED_$(date +%Y-%m-%d).md"
```

Keep at most 3 old seeds. Delete the oldest if there are more:

```bash
ls -t CONTINUITY_SEED_*.md 2>/dev/null | tail -n +4 | xargs rm -f 2>/dev/null
```

### 3b -- Save to the outputs folder (for Cowork)

Also save a copy to the session outputs folder so the user can grab it from chat:

```bash
cp seed.md "$(ls -d /sessions/*/mnt/outputs | head -1)/continuity_seed_[project]_[YYYY-MM-DD].md"
```

### 3c -- Display inline

Show the full seed in chat so the user can copy-paste it into a new session directly. Frame it:

```
---
Continuity Seed Generated -- [project name]
Paste this at the start of your next session to resume where you left off.
FIRST, in the new session, select these folders in the picker: [REQUIRED picker names].
Also saved to: [file path]
---

[seed content here]
```

Listing the REQUIRED folder names in the delivery message means the user mounts them before they
even paste the seed -- the failure is prevented at the source.

## Step 4 -- Loading a Seed (Next Session)

When a user pastes a continuity seed at the start of a conversation, or says "load my seed"
or "resume from seed", the receiving Claude MUST run the mount gate before anything else:

1. **Run the Mount Check.** Execute the command in the seed's "Mount Check" section and compare
   the output against the Mount Manifest.
2. **If any REQUIRED folder is missing, STOP.** Tell the user the exact picker name(s) to add, in
   one clear line: "Before I continue, add these folders in the Cowork picker: A, B." Do not
   attempt the work on partial mounts.
3. **Verify landmarks.** For each REQUIRED folder, confirm its landmark file/dir exists -- this
   catches a folder that was renamed or the wrong folder mounted.
4. Acknowledge what was accomplished and what's next.
5. Start from the **Resume Instructions** -- not from scratch.
6. Check git status against the seed's "Uncommitted Changes" to detect drift.
7. Proceed with **Next Steps** item #1.

Do NOT re-read the entire codebase or re-discover the architecture if the seed provides
sufficient context. Trust the seed unless something contradicts what you see in the environment.

## Compression Principles

- **Mounts before work** -- a perfect plan against unmounted folders is zero plan. Gate first.
- **Stable names over session paths** -- record the picker name; the absolute path rotates and dies.
- **State over story** -- what matters is where things are, not how they got there
- **Decisions are sacred** -- re-debating settled decisions is the worst time sink
- **Errors are gold** -- gotchas discovered this session save the next session hours
- **Actionable over comprehensive** -- the next session needs to know what to DO
- **Trust but verify** -- spot-check the seed against the actual environment

## Relation to Other Skills

- **compact** -- Use compact mid-session when context is filling up but you want to keep working. Use continuity-seed when you're ending the session or transitioning to a new one.
- **reentry** -- reentry reconstructs state at session start from the environment; continuity-seed serializes it at session end. A seed loaded by reentry is the cleanest handoff.
- **machine-bridge** -- machine-bridge documents the rotating-session-path / sandbox-mount hazard in depth. The Mount Manifest here is the seed-level countermeasure to that same hazard.
- **phased-deploy / carmatch-deploy** -- If a deploy is in progress when the seed is generated, capture the exact phase and what's left. The next session can invoke the deploy skill and skip completed phases.
- **CLAUDE.md** -- The seed is NOT a replacement for project documentation. It captures session-specific state. Project-level context belongs in CLAUDE.md.
