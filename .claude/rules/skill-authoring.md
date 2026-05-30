# Rule: Skill Authoring

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
