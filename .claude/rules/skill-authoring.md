# Rule: Skill Authoring

## Canonical location is this repo, not wherever it was written

A skill is only "shipped" once it lives in `pinz-byte/skill-maker` (this repo)
and has gone through `./publish.sh`. If a skill gets authored inside a
different project's repo (e.g. a domain project builds its own skill inline
and copies the `SKILL.md` straight into the local plugin cache under
`~/.claude`/`var/folders/.../skills/`), that copy is a dead end: it isn't
distributable to M1/M2/M3, isn't tracked by `build-marketplace.py`'s GROUPS
guard, and gets silently swept on the next marketplace auto-update (observed
2026-06-02: `pre-deliver` was built and committed inside `AVT_CarMatch_meta`,
manually deployed to a local cache, and only discovered to be orphaned when
the user checked the Cowork plugin UI and it wasn't there).

If you're an agent authoring a skill outside this project: after the skill
works, its `SKILL.md` must be moved into this repo, assigned a GROUP in
`build-marketplace.py`, and shipped via `./publish.sh` — flag this to the user
explicitly rather than treating a local copy as done.

## SKILL.md structure is strict

Every skill file must have valid YAML frontmatter followed by Markdown body.

Correct:
```markdown
---
name: my-skill
description: >
  Trigger conditions and what this skill does.
  Keep under 1024 characters total.
---

# My Skill — Title

Body content here.
```

## Description field rules

- Max 1024 characters (Cowork hard limit — validator rejects silently if exceeded)
- Must include trigger conditions — what phrases or situations activate the skill
- No emoji characters anywhere in the file
- Use `>` block scalar for multi-line descriptions

## Trigger language patterns that work

Lead with action phrases the user will actually say:
- "Use this skill whenever the user says X, Y, or Z"
- "Trigger on: 'commit this', 'clean the log', 'squash these commits'"
- "Also trigger when the user says..." (for edge case triggers)
- "Fire even on casual variations like..."

Weak trigger language to avoid:
- Vague: "Use for git operations" 
- Too narrow: "Only trigger on exact phrase 'git-ops'"
- Missing edge cases: never list only one trigger phrase

## Body structure

Lead with what the skill IS, then HOW it works, then PRINCIPLES.
- Use ## headers for major sections
- Keep individual sections scannable — bullet lists over dense paragraphs
- End with a Principles section for non-obvious behavior rules
- Include Edge Cases section for anything that breaks the happy path
