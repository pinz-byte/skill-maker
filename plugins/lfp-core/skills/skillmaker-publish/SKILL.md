---
name: skillmaker-publish
description: >-
  SKILL MAKER's publish pre-flight and runner: validates every skill's SKILL.md (GROUP
  assignment in build-marketplace.py, description under 1024 chars, no reserved "claude" in
  the name) and scans for non-ASCII content the pipeline would silently mangle --
  transliterates it to clean ASCII with --fix instead of losing bytes -- then runs
  ./publish.sh natively or hands off the exact command when the session is sandboxed (Cowork
  agents cannot git-write or unlink in this repo). Use this skill whenever the user says
  "publish this", "publish the skill", "ship it", "run publish", "publish the marketplace",
  "push the marketplace", "deploy skills", or "./publish.sh" while working in the SKILL MAKER
  project. Also trigger right after a new or edited skill is added to this repo and the next
  step is shipping it, or when the user asks "how do I publish", "how do I run it", or "how to
  run it" in this project context. NOT skill-miner (proposes new skills): this validates and
  ships what already exists.
metadata:
  intent: build
---
# SKILL MAKER Publish

## What this skill does
Runs the pre-flight + publish sequence for this project's skill marketplace, so the
checks `build-marketplace.py` already enforces -- plus one it doesn't -- get caught
before a broken build ships, not after.

## How it works
1. Run the pre-flight script from the repo root:
   ```bash
   python3 skillmaker-publish/references/preflight.py
   ```
   It re-derives GROUPS, `parse_frontmatter`, and `strip_non_ascii` live from
   `build-marketplace.py` (no duplicated logic to drift out of sync), then additionally
   scans every skill's `SKILL.md` + `references/` for non-ASCII bytes -- because
   `build-marketplace.py`'s `strip_non_ascii` **deletes** those bytes instead of
   transliterating them (e.g. accented "metodo" becomes "mtodo", ene "senal" becomes
   "seal" -- an actual English word). This was discovered shipping
   `patel-tone-converter` (2026-07-14) and isn't caught anywhere else in the pipeline.

2. If non-ASCII content is flagged, transliterate it in place before packaging:
   ```bash
   python3 skillmaker-publish/references/preflight.py --fix
   ```
   This normalizes accents, ene, em/en-dashes, and curly quotes to clean ASCII
   equivalents rather than deleting characters -- keeps Spanish (or any
   accented-language) content readable instead of garbled.

3. Environment matters -- the script detects which one it's in:
   - **Sandboxed Cowork session:** the sandbox mount blocks `unlink`/`rmtree` and
     `.git/index.lock` writes in this repo (known limitation). The script runs the
     read-only checks and prints the exact native handoff command instead of attempting
     to publish.
   - **Native M2 terminal:** the script can check and publish in one go:
     ```bash
     python3 skillmaker-publish/references/preflight.py --publish
     ```
     This runs `./publish.sh` and auto-recovers from a stale `.git/index.lock` left by a
     prior sandbox git command, retrying once.

4. If invoked from a sandboxed agent session, always end by giving the user the exact
   native command -- don't just say "run ./publish.sh", say:
   ```
   cd "/Users/lfp/Projects/SKILL MAKER"
   ./publish.sh
   ```

## Principles
- Never attempt `./publish.sh`, `build-marketplace.py`, or any git write from a sandboxed
  Cowork session -- it fails on unlink/rmtree or leaves a stale `index.lock`. Detect and
  hand off instead of retrying blindly.
- Non-ASCII content is not automatically wrong -- Spanish or other accented-language
  skill content is legitimate. The fix is transliteration (readable ASCII), never silent
  deletion (garbled ASCII). Don't skip `--fix` for a skill with real accented body text.
- The pre-flight script derives its checks live from `build-marketplace.py`'s own
  `GROUPS` / `parse_frontmatter` / `strip_non_ascii` -- it does not hardcode a second
  copy of `GROUPS`, so it can't silently drift out of sync when `GROUPS` changes.

## Edge Cases
- New skill added but not yet in `GROUPS`: pre-flight reports it as "ungrouped" and
  blocks publish -- add it to a plugin group in `build-marketplace.py` first (create a
  new group if none of the existing ones fit; don't force it into an unrelated one).
- `index.lock` still present after one automatic retry: something else is holding it
  (another process, a genuinely concurrent git operation) -- stop and investigate rather
  than looping retries.
- Nothing staged (`git status --short` is empty): pre-flight reports "nothing to
  publish" and exits without running `publish.sh` -- there's nothing new to ship.
- `--fix` changes file contents on disk -- review the diff before publishing if the
  skill's accented content is nuanced (tone/copy skills especially), since transliteration
  is a one-way, lossy operation on the shipped copy.
