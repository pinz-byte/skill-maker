---
name: ultrathink
description: >-
  Activates extended reasoning in Claude Code by appending "Ultrathink" as the last line of
  any prompt. Use for multi-phase audits, ingestion scripts, architecture decisions, and any
  task where wrong moves have downstream consequences. NOT critical-thinker (attacks the idea
  itself): this only escalates reasoning depth on the current prompt.
version: 1.0
created: 2026-03-19
metadata:
  intent: reason
---

# SKILL  Ultrathink

*Portable activation protocol for extended reasoning in Claude Code*
*Version: 1.0 | Created: 2026-03-19*

---

## What It Is

`Ultrathink` is a single-word trigger that activates Claude Code's extended
thinking mode  maximum compute, deeper reasoning, longer internal deliberation
before acting.

It tells Claude Code: "Do not jump to the first solution. Think the problem
through completely before touching anything."

---

## When To Use

Add `Ultrathink` as the **last line** of any Claude Code prompt.

### HIGH  Always use Ultrathink:
- Multi-section audits (security, database, code quality)
- Architecture decisions with downstream consequences
- Debugging complex pipelines where wrong moves cascade
- Any prompt with 3+ sequential phases
- Data ingestion scripts (silent failure risk is high)
- Schema changes touching multiple databases
- Anything where "undo" is difficult or impossible

### LOW  Skip Ultrathink:
- Single-file fixes with obvious solutions
- Adding a log line or renaming a variable
- Simple schema patches
- Any task under ~10 lines of change

**Rule of thumb:** If you'd want a senior engineer to read the whole spec
before writing a single line  use Ultrathink.

---

## How To Use

Place `Ultrathink` on its own line at the very end of the prompt:

```
[your full prompt here]

...all instructions...

Final commit message: 'fix: description of what was fixed'

Ultrathink
```

Nothing else needed. One word. Last line.

---

## What It Does

Claude Code (Opus 4.6 on Claude Max) allocates more compute tokens to
internal reasoning before producing any output or taking any action.

Practical effect:
- Reads the entire prompt before deciding approach
- Identifies edge cases before they cause failures
- Plans the full execution sequence before step 1
- Surfaces conflicts between instructions proactively
- Less likely to silently skip a step or misread a field name

The reasoning happens internally  you don't see it. You just get
better output.

---

## Real-World Example

**Without Ultrathink:**
Scripts/ingest_business_transcripts.py used `page_id[:12]` for vector IDs.
All Notion page IDs in the workspace share a common prefix.
Result: 120 vectors silently overwrote each other  2 vectors remaining.
No error thrown. Data loss without warning.

**With Ultrathink on the ingestion prompt:**
Extended reasoning would have caught: "All IDs share a prefix 
truncation will cause collisions." Fix applied before first upsert.

---

## Applying This Skill

When loading this skill file, add `Ultrathink` to the end of the prompt
before submitting to Claude Code. No other changes needed.

For the Life Archive / Symbios system, Ultrathink is **standard** on:
- All audit prompts
- All ingestion scripts
- All multi-phase cleanup sequences
- All security scans
- All phased-deploy sequences touching production

---

## Portability

This skill works in any Claude Code session, any project, any channel.
No setup required. No configuration. No dependencies.

Copy this file to `/mnt/skills/user/ultrathink/SKILL.md` in any project
to make it available as a loadable skill.

Or simply remember: **last line, one word.**

---

*This skill was formalized from observed usage on the Symbios /
Second Self infrastructure project  2026-03-19.*
*The vector ID collision bug was the case study that made it standard.*
