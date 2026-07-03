# Continuity Seed  Structure Template and Worked Example

## The exact structure

Use this exact structure. Every section earns its place  omit sections only if genuinely empty.
The **Mount Manifest** is never omitted in a Cowork session.

```markdown
# Continuity Seed -- [Project Name]
> Generated: [YYYY-MM-DD HH:MM]
> Session: [brief 1-line description of what this session accomplished]

## Mount Check (READ AND ACT ON THIS FIRST)
Before doing anything else, confirm these folders are selected in the Cowork folder picker.
Run: ls -1 /sessions/*/mnt/ 2>/dev/null | grep -vE '^(outputs|uploads)$'
If any REQUIRED folder below is missing, STOP and tell the user the exact picker name(s) to add.
Do NOT proceed on partial mounts -- that is what produces silent "source isn't mounted" errors.

## Mount Manifest
REQUIRED folders (next session cannot work without these):
- [Picker name] -- [role] -- landmark: [file/dir that proves it is the right folder]
- [Picker name] -- [role] -- landmark: [file/dir]

OPTIONAL folders (context only):
- [Picker name] -- [why it was referenced]

NOT mounted this session but needed next time:
- [Picker name or repo] -- [what it is, why it was missing]

## Resume Instructions
[2-3 sentences telling the next Claude instance exactly what to do first, AFTER the mount check
passes. Be specific: "Continue implementing X in file Y" or "Debug the Z error in function W".]

## Project Context
- **Repo:** [name or URL -- stable, not a session path]
- **Branch:** [current branch]
- **Primary folder (picker name):** [e.g. "AVT CarMatch meta"]
- **Key files:** [3-5 files most relevant to current work, as repo-relative paths]

## Current State

### Completed This Session
[Bullet list of what got done -- concrete items, not vague descriptions]

### In Progress
[What's partially done -- include file names, line numbers, function names]

### Blocked / Deferred
[What couldn't be completed and why -- include error messages if relevant]

## Decisions Made
[Bullet list of decisions with brief rationale. These are critical because the next session will
otherwise re-debate them. Format: "Decision: [what] -- Reason: [why]"]

## Gotchas Discovered
[Things that tripped us up or would trip up a fresh session.
Format: "Gotcha: [what] -- Fix: [how we handled it]"]

## Uncommitted Changes
[Output of git status --short and git diff --stat, if any]

## Next Steps (Ordered)
1. [First thing to do in the next session]
2. [Second thing]
3. [Third thing]
[Keep to 3-5 items. Actionable, not aspirational.]

## Key Code / Config
[Only critical snippets the next session absolutely needs -- a schema, a config block, an API
signature. Do not dump entire files. Omit if nothing is critical.]
```

## Worked example (a complete, filled seed)

This is what a good seed looks like fully populated  including the Mount Manifest that prevents
the "source isn't mounted" failure. Use it as the quality bar.

```markdown
# Continuity Seed -- AVT CarMatch (meta)
> Generated: 2026-06-23 14:10
> Session: scoped the B-branch normalization work; chose branch B over A.

## Mount Check (READ AND ACT ON THIS FIRST)
Run: ls -1 /sessions/*/mnt/ 2>/dev/null | grep -vE '^(outputs|uploads)$'
Required below: "AVT CarMatch meta". If missing, STOP and ask the user to add it in the picker.

## Mount Manifest
REQUIRED:
- AVT CarMatch meta -- primary workspace; holds the catalog, picker, and scripts
  -- landmark: catalog_versioned_normalized.json, scripts/
OPTIONAL:
- (none this session)
NOT mounted this session but needed next time:
- extractor repo -- source of the raw listings the normalizer consumes; had to reason about it
  blind. Ask the user to mount it before touching the ingest path.

## Resume Instructions
Mount "AVT CarMatch meta" (and ask for the extractor repo if the next step is ingest). Then continue
the B-scope normalization: implement the mapping in scripts/normalize_b.py against
catalog_versioned_normalized.json.

## Project Context
- **Repo:** avt-carmatch-meta
- **Branch:** feat/normalize-b
- **Primary folder (picker name):** AVT CarMatch meta
- **Key files:** scripts/normalize_b.py, catalog_versioned_normalized.json, docs/B_SCOPE.md

## Current State
### Completed This Session
- Compared A vs B scope; documented the call in docs/B_SCOPE.md
### In Progress
- scripts/normalize_b.py -- field mapping ~40% done; stub at line 88
### Blocked / Deferred
- Ingest validation deferred: extractor repo was not mounted

## Decisions Made
- Decision: take branch B (catalog-side normalization) -- Reason: A required extractor changes we
  can't make without that repo mounted; B ships value with only the meta workspace.

## Gotchas Discovered
- Gotcha: "extractor not mounted" stalled ingest -- Fix: scoped to catalog-side only this session.

## Uncommitted Changes
 M scripts/normalize_b.py
 A docs/B_SCOPE.md

## Next Steps (Ordered)
1. Mount "AVT CarMatch meta"; finish the mapping in normalize_b.py from line 88.
2. Ask the user to mount the extractor repo, then wire ingest validation.
3. Commit on feat/normalize-b.
```
