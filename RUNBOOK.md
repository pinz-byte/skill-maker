# SKILL MAKER Runbook

Last updated: 2026-06-09

Copy-paste-safe command blocks for the common SKILL MAKER flows. Every block is ASCII
with no inline comments, because interactive zsh does NOT treat `#` as a comment -- a
pasted comment line runs as a command and throws errors. Explanations live in prose,
never inside the code fences.

Three paste rules:
1. No `#` comment lines inside a command block.
2. Always quote the path -- "SKILL MAKER" contains a space.
3. Never paste a `<placeholder>` in angle brackets. Substitute the real value first.

## Publish (most common)

Run on M1 after editing any SKILL.md or changing GROUPS. Rebuilds the marketplace
(which regenerates the agent-bridge inbox table from canonical), commits, pushes, and
refreshes M1's own cache.

```
cd "$HOME/Documents/Claude/Projects/SKILL MAKER"
./publish.sh
```

Then on M2 and M3 (or wait for their daily launchd job):

```
claude plugin marketplace update lfp-skills
```

## Add a new inbox project

Canonical source is `.claude/rules/inbox-registry.md`. Add the row to its table, then
regenerate and publish. Never hand-edit the table in `agent-bridge/SKILL.md` -- it is
generated.

```
cd "$HOME/Documents/Claude/Projects/SKILL MAKER"
python3 gen-inbox-registry.py
./publish.sh
```

## Add a new skill

Create `<newskill>/SKILL.md`, then add its directory name to a plugin list in `GROUPS`
inside `build-marketplace.py` (lfp-thinkers, lfp-core, or lfp-apex). The build fails
loud if a skill on disk is ungrouped.

```
cd "$HOME/Documents/Claude/Projects/SKILL MAKER"
python3 build-marketplace.py
./publish.sh
```

## Verify and troubleshoot

```
cd "$HOME/Documents/Claude/Projects/SKILL MAKER"
git status
git log --oneline -3
python3 gen-inbox-registry.py --check
```

How to read the output:

- git status "up to date with 'origin/main'" and "working tree clean" -- fully shipped.
- git status "ahead of 'origin/main' by N commits" -- committed but not pushed. Run `git push`.
- publish.sh "Nothing changed -- already published" -- the rebuild was byte-identical to
  the last commit. Normal; it means there was nothing new to ship.
- gen-inbox-registry.py --check exits nonzero -- the agent-bridge table drifted from
  canonical. Run `python3 gen-inbox-registry.py` then `./publish.sh`.
- build-marketplace.py halts on "not in any GROUP" -- add the skill dir to a GROUP, rebuild.
