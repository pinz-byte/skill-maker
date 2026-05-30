---
name: git-ops
description: >
  Full Git autonomy skill for co-worker agents. Covers the complete Git lifecycle without
  requiring user intervention: writing clean structured commit messages, squashing and cleaning
  messy WIP history, reading the git log to produce a build state summary, managing branches
  (create, rename, delete stale), and resolving merge conflicts autonomously — escalating to
  the user only when a genuine domain decision is required. Use this skill whenever the user or
  an agent needs to commit, clean history, read the log, summarize build state, manage branches,
  or resolve conflicts. Trigger on: "commit this", "clean the log", "squash these commits",
  "what does the log say", "build state from git", "clean up branches", "there's a conflict",
  "git status", "prepare for review", "git hygiene", or any request involving Git operations
  in a build session. Also trigger proactively at the end of any build session to ensure the
  log is clean before handoff.
---

# Git Ops — Full Git Autonomy Protocol

You are a co-worker agent operating in a multi-machine build ecosystem. Git is your shared record
of what was built, when, and why. A clean log is not cosmetic — it's the primary mechanism by
which any agent (or the user) can reconstruct build state after a session gap. Your job is to
maintain it with discipline, so no human needs to intervene in routine Git operations.

This skill covers four areas: **COMMIT**, **CLEAN**, **READ**, and **BRANCH**. A fifth — 
**CONFLICT** — handles the one scenario where you may need to escalate.

---

## COMMIT — writing clean, structured commit messages

Every commit message follows this format:

```
[TYPE]([scope]): [imperative summary, max 72 chars]

[Optional body — what changed and why, not how. Wrap at 72 chars.]

[Optional footer — breaking changes, references, BRIDGE/RELAY IDs]
```

### Types

| Type | When to use |
|---|---|
| `feat` | New feature or capability added |
| `fix` | Bug fix |
| `build` | Build system, config, dependencies |
| `refactor` | Code restructured — no behavior change |
| `data` | Data pipeline, schema, migration |
| `deploy` | Deployment config, environment |
| `wip` | Work in progress — only if mid-session save |
| `chore` | Cleanup, formatting, dead code removal |
| `docs` | Documentation only |

### Scope

The scope is the project or subsystem affected. Use short lowercase names matching the initiative:
`subastop`, `carmatch`, `avt`, `sensei`, `symbios`, `bridge`, `api`, `db`, `ui`, `auth`, etc.

### Rules for writing the summary

- Imperative mood: "add user auth" not "added user auth" or "adding user auth"
- No period at the end
- Specific enough to understand without reading the diff
- Never: "fix bug", "update code", "changes", "wip", "misc", "stuff"

### Examples

```
feat(carmatch): add session persistence to /matches navigation

fix(subastop): resolve engine key deletion on high-volume auction days

build(avt): upgrade extractor pipeline to support 3 new LATAM sources

data(sensei): migrate optimizer schema to v2 token structure

deploy(symbios): resolve 4x Render deploy failures — update start command
```

### When to write the body

Write a body when:
- The commit closes a multi-session problem (explain what the root cause was)
- The change has non-obvious side effects
- A BRIDGE or RELAY ID is relevant (include it in the footer)
- It's a breaking change (start footer with `BREAKING CHANGE:`)

### Committing autonomously

Before every commit:
1. Run `git status` — confirm what's staged
2. Run `git diff --staged` — read the actual changes
3. Write the message from what you observed, not from what you intended
4. If multiple logical changes are staged together, split them into separate commits

Never commit everything in one blob. One logical change = one commit.

---

## CLEAN — squashing and rewriting messy history

Use this before: code review, PR creation, sharing a branch, or any session handoff where the
log needs to be readable.

### When to clean

Clean when you see any of these in `git log --oneline`:
- `wip`, `fix`, `update`, `changes`, `temp`, `asdf`, numbered commits (`fix 2`, `fix 3`)
- Multiple commits touching the same file for the same logical reason
- More than 3 consecutive commits without a meaningful feature boundary

### How to clean

**Step 1 — Audit the log**

```bash
git log --oneline -20
```

Read the last 20 commits. Identify logical groupings — commits that belong together as one
coherent unit of work.

**Step 2 — Determine the squash boundary**

Find the last commit that is already clean and should not be touched. Everything after it is
your squash target. Note its hash.

**Step 3 — Interactive rebase**

```bash
git rebase -i [clean-commit-hash]
```

In the rebase editor:
- `pick` the first commit of each logical group
- `squash` (or `s`) subsequent commits that belong to the same unit
- `reword` (or `r`) any commits with bad messages that should stand alone

**Step 4 — Write clean messages for squashed commits**

When the rebase editor opens for each squash group, write a fresh commit message following the
COMMIT format above. Ignore all the individual WIP messages — write from what the combined
diff actually does.

**Step 5 — Verify**

```bash
git log --oneline -20
```

Every commit in the cleaned range should now be readable as a standalone unit of work.

### Safety rules

- Never rebase commits that have already been pushed to a shared remote and pulled by others
- If unsure whether commits are shared: `git log origin/[branch]..HEAD` — only rebase what's
  ahead of origin
- Always work on a named branch, never directly on main
- If something goes wrong: `git rebase --abort` returns you to the pre-rebase state

---

## READ — producing a build state summary from git log

Use this when: entering a session on an unfamiliar machine, picking up a BRIDGE or RELAY packet,
running reentry on a specific project, or when asked "what's the state of this build."

### Step 1 — Gather the log

```bash
git log --oneline --since="7 days ago"
git status
git branch -a
```

### Step 2 — Parse for signal

Read the log looking for:
- **Last completed feature** — the most recent `feat()` commit
- **Last fix** — the most recent `fix()` commit and what it addressed
- **In-progress work** — any `wip()` commits or uncommitted changes in `git status`
- **Stale surfaces** — areas of the codebase with no recent commits (may be blocked or abandoned)
- **Density pattern** — many commits to the same scope = active build surface

### Step 3 — Produce the build state summary

Output in this format:

```
GIT STATE — [repo/project] — [date]

LAST COMPLETED WORK
[feat or fix commit — what was built or resolved]

IN PROGRESS
[wip commits or uncommitted changes — what's mid-flight]

RECENT ACTIVITY (last 7 days)
[3-5 bullet points: key commits by scope, most recent first]

STALE SURFACES
[Files or scopes with no recent activity that might be blocked]

BRANCH
[Current branch name and how far ahead/behind origin]

ASSESSMENT
[1-2 sentences: what this build is ready for next, and what's blocking it]
```

This summary is the primary input for the reentry skill's machine thread reconstruction. If
you're running a reentry hutch, this is how you reconstruct M1/M2/M3 build state.

---

## BRANCH — autonomous branch management

### Naming convention

```
[type]/[scope]-[short-description]
```

Examples:
- `feat/carmatch-session-persistence`
- `fix/subastop-engine-key-deletion`
- `build/avt-pipeline-v2`
- `deploy/symbios-render-recovery`

### Creating branches

Always branch from the cleanest stable point. Before creating:

```bash
git status          # confirm clean working tree
git pull origin main # ensure you're current
git checkout -b [branch-name]
```

### Deleting stale branches

A branch is stale if:
- It was merged more than 7 days ago
- It has no commits in 14+ days and no open BRIDGE referencing it
- It was a `wip/` or `temp/` branch that served its purpose

To audit and clean:

```bash
# Branches merged into main
git branch --merged main

# Branches with no recent commits
git for-each-ref --sort=committerdate refs/heads/ --format='%(committerdate:short) %(refname:short)'
```

Delete locally: `git branch -d [branch-name]`
Delete remote: `git push origin --delete [branch-name]`

Never delete a branch that has unmerged commits unless you've confirmed the work is abandoned.
When in doubt, check with the user before deleting.

### Branch hygiene rule

At the end of every build session: check how many open branches exist. If more than 5 unmerged
branches, surface them to the user as a quick audit item. Don't delete without confirmation —
just surface.

---

## CONFLICT — resolving merge conflicts autonomously

Most conflicts are mechanical. Some require a domain decision. Know the difference and act
accordingly.

### Conflicts you can resolve autonomously

Resolve without asking when:
- One side adds code the other side doesn't touch (take both)
- The conflict is in formatting, whitespace, or imports (take the cleaner version)
- One version is clearly a later iteration of the same thing (take the more recent)
- The conflict is in a generated file (take the version that matches the current build config)

### How to resolve

```bash
git status              # identify conflicted files
git diff               # read the conflict markers
```

For each conflict marker (`<<<<<<<`, `=======`, `>>>>>>>`):
1. Read both sides fully before deciding
2. Resolve by editing the file to the correct combined state — don't just pick one side blindly
3. Remove all conflict markers
4. Verify the file is syntactically valid after resolution

After resolving all files:
```bash
git add [resolved-files]
git commit -m "fix([scope]): resolve merge conflict — [brief description of what was merged]"
```

### Conflicts that require escalation

Stop and surface to the user when:
- Two versions represent genuinely different architectural decisions
- One version contains logic the other deleted intentionally (you don't know which intention wins)
- The conflict is in a schema, migration, or data contract that affects other projects
- You've resolved the markers but the result doesn't make semantic sense

Escalation format:
```
Conflict in [file] requires your decision.

OPTION A ([branch name]):
[What this version does — 1-2 sentences]

OPTION B ([branch name]):
[What this version does — 1-2 sentences]

Why I can't decide: [one sentence — what's the domain ambiguity]
```

---

## End-of-session Git checklist

Run this before closing any build session:

1. `git status` — no untracked or modified files should be left uncommitted
2. `git log --oneline -10` — no `wip` commits unless genuinely mid-flight
3. `git branch` — no temp branches that served their purpose
4. Write a session-close commit if needed: `chore([scope]): session close — [what state the build is in]`

This checklist is what makes the reentry skill accurate. A clean log at session close = fast
reconstruction at session open.

---

## Principles

**The log is for the next agent, not the current one.** Write every commit as if the person
reading it has no context about your session. They shouldn't need to ask you what happened.

**One logical change, one commit.** Resist the urge to batch. If you fixed two bugs and added
a feature, that's three commits.

**Never force-push shared branches.** Rebase is only safe on commits that haven't left your
machine yet. If in doubt: don't rebase, squash in a new commit instead.

**Escalate conflicts early.** A conflict that blocks a build for 30 minutes while you try to
infer intent is worse than a 2-sentence escalation to the user. Know the line.

**Clean log = fast reentry.** The git-ops discipline and the reentry skill are directly
connected. Every clean commit is a data point the reentry hutch can use.
