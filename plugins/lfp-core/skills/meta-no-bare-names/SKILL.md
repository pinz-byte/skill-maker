---
name: meta-no-bare-names
description: >
  Persistent context hygiene gate. Two jobs: (1) block bare skill-default file
  names from being committed to any repo; (2) enforce dated headers on all
  persistent context files (CLAUDE.md, memory files, capsules, seeds, IB
  artifacts) so stale content is never invisible. Universal scope -- every
  project, every repo. Trigger on: "git add", "git commit", "commit this",
  "stage files", "push", "hygiene sweep", "clean up files", "git status",
  "session close", "before we wrap", or any git operation. Also fire when the
  user mentions CLAUDE.md, CONTINUITY_SEED.md, IB.md, memory files, capsules,
  MEMORY.md, or any persistent context file. Fire on "is this stale?", "when
  was this last updated?", "check my context files", or "audit my project
  context". This gate is universal -- runs before any git operation and at
  session close, no exceptions.
---

# Persistent Context Hygiene Gate

Two failure modes, one gate.

**Failure mode 1  Bare skill-default names:** Raw skill output files with
generic placeholder names (CONTINUITY_SEED.md, IB.md) committed to version
control. They create orphan duplicates and silent drift.

**Failure mode 2  Undated persistent context:** Files that live permanently
in a project (CLAUDE.md, memory/, capsules/, seeds) with no date signal inside
them. A reader -- human or agent -- cannot tell if the content is from last
week or last year. Stale context is worse than no context: it's confidently
wrong.

Both failures share the same root cause: files that carry operational weight
but no temporal identity. This gate closes both loops.

---

## Part A -- Bare Skill-Default Names

### What is a "bare skill-default name"?

A file is bare if it matches a known skill output pattern AND has no date,
scope, or version in its filename.

| Skill | Bare default name | Canonical form |
|---|---|---|
| continuity-seed | CONTINUITY_SEED.md | CONTINUITY_SEED_YYYY-MM-DD.md |
| intention-builder | IB.md, INTENTION_MATRIX.md, PURPOSE_PYRAMID.md | IB_[project]_YYYY-MM-DD.md |
| memory capsule | MEMORY_CAPSULE.md | MEMORY_CAPSULE_[scope]_YYYY-MM-DD.md |
| builder prompts | BUILDER_PROMPT.md | BUILDER_PROMPT_[topic]_YYYY-MM-DD.md |
| any skill output | [SKILL_NAME].md (no scope/date) | [SKILL_NAME]_[scope]_YYYY-MM-DD.md |

### Step A1 -- Scan for Bare Names

```bash
cd <project-root>

# Known bare patterns
for BARE in CONTINUITY_SEED.md IB.md INTENTION_MATRIX.md PURPOSE_PYRAMID.md MEMORY_CAPSULE.md BUILDER_PROMPT.md; do
  [ -f "$BARE" ] && echo "BARE FOUND: $BARE"
done

# Any all-caps .md in git status that has no date/scope token
git status --short | awk '{print $2}' | grep -E '^[A-Z_]+\.md$' | while read f; do
  echo "CANDIDATE: $f -- check for bare default pattern"
done
```

### Step A2 -- Orphan-Duplicate Check

For each BARE found, check for a canonical timestamped sibling:

```bash
# Generalized pattern -- substitute CONTINUITY_SEED for each bare file prefix
PREFIX="CONTINUITY_SEED"
LATEST_TS=$(ls -t ${PREFIX}_*.md 2>/dev/null | head -1)
if [ -n "$LATEST_TS" ]; then
  diff -q ${PREFIX}.md "$LATEST_TS" > /dev/null 2>&1 \
    && echo "Case A: ORPHAN DUPLICATE (100% match) -- safe to delete bare" \
    || echo "Case C: DIVERGENT -- surface to user"
else
  echo "Case B: NO CANONICAL SIBLING -- rename required"
fi
```

### Step A3 -- Resolve

**Case A (orphan duplicate):** Delete the bare. Canonical sibling is source of truth.
```bash
rm BARE_FILE.md
```

**Case B (no sibling):** Rename to canonical before staging.
```bash
mv BARE_FILE.md BARE_FILE_$(date +%Y-%m-%d).md
git add BARE_FILE_$(date +%Y-%m-%d).md
```

**Case C (divergent):** HOLD. Surface to user. Never auto-resolve.
State: "BARE_FILE.md differs from BARE_FILE_YYYY-MM-DD.md. Which is current?
The other should be deleted or renamed before committing."

---

## Part B -- Persistent Context File Dating

### What files need dated headers?

Persistent context files live by their canonical name (no date suffix) but
must carry a date signal *inside* the file so readers can assess freshness.

Files in scope:

| File type | Location pattern | Required date signal |
|---|---|---|
| Project instructions | CLAUDE.md (repo root or .claude/) | `last_updated: YYYY-MM-DD` in frontmatter or first line |
| Memory index | MEMORY.md, memory/MEMORY.md | `last_updated: YYYY-MM-DD` in first 5 lines |
| Memory entries | memory/*.md | `last_updated: YYYY-MM-DD` in YAML frontmatter |
| Data capsules | capsules/*.md | `date: YYYY-MM-DD` in frontmatter |
| Continuity seeds | CONTINUITY_SEED_*.md | Date in filename is sufficient; optionally in header |
| IB artifacts | IB_*.md | Date in filename is sufficient |
| Agent configs | .claude/agents/*.md | `last_updated: YYYY-MM-DD` if it contains project-specific facts |

### Step B1 -- Scan for Missing Date Signals

```bash
cd <project-root>

# CLAUDE.md -- check for last_updated anywhere in first 10 lines
if [ -f "CLAUDE.md" ]; then
  head -10 CLAUDE.md | grep -qi "last.updated\|updated.*[0-9]\{4\}" \
    || echo "MISSING DATE: CLAUDE.md has no last_updated field"
fi
if [ -f ".claude/CLAUDE.md" ]; then
  head -10 .claude/CLAUDE.md | grep -qi "last.updated\|updated.*[0-9]\{4\}" \
    || echo "MISSING DATE: .claude/CLAUDE.md has no last_updated field"
fi

# Memory files
find . -path "*/memory/*.md" -not -name "MEMORY.md" 2>/dev/null | while read f; do
  head -5 "$f" | grep -qi "last.updated\|updated.*[0-9]\{4\}" \
    || echo "MISSING DATE: $f"
done

# Capsules
find . -path "*/capsules/*.md" 2>/dev/null | while read f; do
  head -5 "$f" | grep -qi "date\|updated.*[0-9]\{4\}" \
    || echo "MISSING DATE: $f"
done

# MEMORY.md index
for MEM in MEMORY.md memory/MEMORY.md .claude/memory/MEMORY.md; do
  if [ -f "$MEM" ]; then
    head -5 "$MEM" | grep -qi "last.updated\|updated.*[0-9]\{4\}" \
      || echo "MISSING DATE: $MEM"
  fi
done
```

### Step B2 -- Staleness Check

For any file that HAS a date signal, check whether it is stale. A file is
stale if its date is older than the staleness threshold for that file type:

| File type | Staleness threshold |
|---|---|
| CLAUDE.md | 60 days (project context drifts slowly) |
| Memory entries | 30 days (operational facts decay faster) |
| MEMORY.md index | 14 days (index should reflect recent memory writes) |
| Data capsules | 90 days (point-in-time facts, long shelf life) |
| Agent configs | 90 days |

```bash
TODAY=$(date +%Y-%m-%d)

# Extract date from a file and check staleness
check_staleness() {
  local file="$1"
  local threshold_days="$2"
  local file_date
  file_date=$(head -10 "$file" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1)
  if [ -n "$file_date" ]; then
    # Days since file_date (macOS/Linux compatible)
    days_old=$(( ($(date -d "$TODAY" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$TODAY" +%s) \
                - $(date -d "$file_date" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$file_date" +%s)) / 86400 ))
    [ "$days_old" -gt "$threshold_days" ] \
      && echo "STALE ($days_old days): $file -- threshold $threshold_days days"
  fi
}

[ -f "CLAUDE.md" ] && check_staleness "CLAUDE.md" 60
find . -path "*/memory/*.md" -not -name "MEMORY.md" 2>/dev/null | while read f; do
  check_staleness "$f" 30
done
find . -name "MEMORY.md" 2>/dev/null | while read f; do
  check_staleness "$f" 14
done
find . -path "*/capsules/*.md" 2>/dev/null | while read f; do
  check_staleness "$f" 90
done
```

### Step B3 -- Resolve Missing Dates

For each file with MISSING DATE: add the date field before committing.

**For CLAUDE.md** -- add to the top of the file:
```markdown
<!-- last_updated: YYYY-MM-DD -->
```
Or if the file uses YAML frontmatter, add `last_updated: YYYY-MM-DD` to the
frontmatter block.

**For memory/*.md files** -- add to YAML frontmatter:
```yaml
---
last_updated: YYYY-MM-DD
---
```

**For capsules/*.md** -- add to frontmatter:
```yaml
---
date: YYYY-MM-DD
---
```

Use today's date if the content was written or reviewed today. If the content
is historical (not reviewed this session), use the file's last git commit date:
```bash
git log -1 --format="%as" -- <filename>
```

### Step B4 -- Resolve Stale Files

For each STALE file: do NOT auto-edit content. Staleness is a signal, not an
error. Surface it to the user:

"CLAUDE.md was last updated YYYY-MM-DD (N days ago). Is this still current?
If yes, update the last_updated date. If the content has drifted, review and
update the file before committing."

The user decides whether the content needs refreshing. The gate only flags;
it does not rewrite.

---

## Combined Gate Verdict

After running both Part A and Part B, state a single verdict:

```
Hygiene gate result:
  Part A (bare names):    [N] found -- [X] deleted, [Y] renamed, [Z] held
  Part B (context dates): [M] missing dates -- [P] added
                          [Q] stale files -- [R] surfaced to user

[CLEAR / HOLD]
```

HOLD conditions:
- Any Case C (divergent bare file) unresolved
- User has not confirmed disposition of stale files flagged in B4
- Any MISSING DATE file that could not be auto-dated (e.g., historical content
  requiring user judgment on the correct date)

CLEAR condition: all bare files resolved, all persistent context files have
date signals, no unresolved stale flags.

---

## Principles

**Two failure modes, one gate.** Bare names and undated context files are
both forms of the same problem: persistent artifacts with no temporal identity.
Run both checks every time.

**Date signals are for readers, not just for agents.** A human opening
CLAUDE.md six months from now should be able to immediately see whether the
content is current. The date field is that signal.

**Staleness is advisory, not blocking.** A stale file is a smell, not a
confirmed error. Surface it. Let the user decide. Never auto-edit content
based on a date check alone.

**Missing date = blocking.** A file with no date signal at all is a hard
gap -- the reader has zero temporal context. Adding the date field is
cheap and always safe. Block the commit until it is added.

**Universal scope.** Every project. Every repo. CLAUDE.md files, memory
directories, capsule directories -- wherever persistent context lives.

---

## Edge Cases

**CLAUDE.md is auto-generated and frequently regenerated**
If the project uses `projectmd-gen` or similar to rebuild CLAUDE.md from
scratch, the date should be injected by that skill, not managed manually.
Flag this to the user: "CLAUDE.md appears auto-generated -- consider having
the generation script inject last_updated automatically."

**Memory file dates conflict with content**
If a memory file's `last_updated` date predates events mentioned in the body,
surface the conflict: "Memory file claims last_updated: YYYY-MM-DD but
references events after that date. Review and correct."

**No memory/ or capsules/ directory in this project**
Part B scans only paths that exist. If no memory/ or capsules/ directory is
found, note it and move on. Do not create directories or files.

**File is staged but undated**
Un-stage: `git restore --staged FILE.md`
Add date signal, re-stage: `git add FILE.md`

**Bare file is mid-session active work**
Flag it, do not rename. "CONTINUITY_SEED.md is active -- rename to canonical
form before closing this session." Remind at commit time.
