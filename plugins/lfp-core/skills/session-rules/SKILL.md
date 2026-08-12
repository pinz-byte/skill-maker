---
name: session-rules
description: >
  Fetches and surfaces the canonical cross-project critical-thinker reinforcement rules at the
  start of any session. Use this skill whenever the user says "session rules", "load the rules",
  "what are the rules", "check the rules", "apply session rules", or at the start of any working
  session where builder prompts, audits, IBs, or structural decisions will be made. Also trigger
  on "rule check", "rule gate", or "what should I remember before we start". This skill exists
  so no project needs its own CLAUDE.md copy of the rules. One Notion page, one skill, all
  projects. Fire it at session open before any artifact authoring begins.
metadata:
  intent: orient
---

# Session Rules

Fetches the canonical cross-project rules from Notion and surfaces them in full before any
artifact authoring begins. This replaces per-project CLAUDE.md rule sections.

---

## What to do

### Step 1: Fetch the canonical rules page

Fetch the Notion page with UUID `365da327-abb1-8158-918d-c47649b79f2a` using the Notion MCP.

If the fetch fails (connection issue, permission error), fall back to the hardcoded rules in
Step 3 of this skill and note that you are using the cached version.

### Step 2: Surface the rules in full

Output the rules exactly as they appear on the page. Do not summarize, filter, or reorder.
The user chose "full list every time"  honor that.

Format the output as a clean block:

```
SESSION RULES LOADED

[rule content verbatim from Notion]

Source: Notion / Session Rules - Canonical
Loaded: [current date and time]
```

### Step 3: Fallback rules (use only if Notion fetch fails)

If Notion is unreachable, surface these rules and label them as CACHED:

**Builder Prompt Scope Discipline**
Identify the smallest possible scope that delivers value. Prefer 3 focused prompts over 1
mega-prompt unless the work genuinely shares a single steward.

**Audit Measurement Justification**
Before any audit: state what the system was designed to do, what you are measuring against,
and justify the match. If you cannot justify the match, stop and reframe.

**IB Scope Boundary Discipline**
Name the scope boundary between what this work ADDS versus what the platform or sibling
systems own. Extension IBs define what the extension adds. Platform IBs belong to the platform.

**Voice Input Verification**
Verify any transcribed acronyms, system names, API names, or tool names before propagating
into any persistent artifact.

**Shared Primitive Discipline**
Any builder prompt touching shared primitives must include a sibling architecture verification
gate. Single source of truth. No batch syncs without explicit cross-team contract.

**Audit-First Before Modification**
Any prompt operating on existing assets must include a Phase 1 audit step before any change.

**Structural Reframe Hygiene**
When a structural reframe occurs mid-session, evaluate whether existing artifacts need to be
archived for wrong-premise before continuing. Consolidate, do not addend.

**Captured Failure Memory Types**
- Voice-to-text hallucination guard
- Audit findings single-owner rule
- IB scope contamination guard
- Audit measurement basis justification

---

## After surfacing the rules

Drop into assistant mode immediately. Do not ask if the user wants to proceed.
The rules are loaded. Work begins.

---

## Principles

**One source, many projects.** The rules live in Notion, not in CLAUDE.md files. If a rule
needs to change, update the Notion page. The skill propagates the update to every project
automatically on next fetch.

**Full list, no filtering.** The user chose to see all rules every time. Do not decide which
rules are relevant. Surface all of them.

**Fetch failure is not silence.** If Notion is unreachable, use the fallback and say so clearly.
A cached version of the rules is better than no rules.

**This skill does not replace the critical-thinker default.** The universal critical-thinker
mode in personal preferences runs always. This skill adds the project-level reinforcement layer
on top of it. Both run. They are not redundant.

---

## Notion page reference

Page: Session Rules - Canonical
UUID: 365da327-abb1-8158-918d-c47649b79f2a
URL: https://www.notion.so/365da327abb18158918dc47649b79f2a
Maintained by: LFP
