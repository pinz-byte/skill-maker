---
name: phased-deploy
description: |
  Enforces a disciplined phased workflow for committing, building, and deploying code.
  Use this skill whenever the user asks to "deploy", "commit and deploy", "push to production",
  "build and deploy", "ship it", "release", "go live", or any variation of staging + building + deploying code.
  Also trigger on "phase deploy", "phased deploy", or "deploy with phases". If the user says "commit" alongside
  "build" or "deploy", use this skill. Even if the task seems simple — a one-line fix that needs deploying —
  use this skill. The phased discipline prevents the class of errors where agents spiral on failures or
  deploy broken code. Do NOT trigger for pure code editing, refactoring, or planning that doesn't involve
  deployment.
  NOT carmatch-deploy (CarMatch-specific targets and gotchas): this is the generic phased commit-build-deploy discipline for any project.
metadata:
  intent: build
---

# Phased Deploy

A disciplined, phased workflow for getting code from local changes to production.
The entire point of this skill is to prevent agent spiral — where Claude retries failing commands,
guesses at fixes, or plows ahead after errors. Every phase has a gate. Every failure is a hard stop.

## Why This Exists

Deploying code involves sequential steps where each depends on the last succeeding.
Without structure, agents tend to:
- Skip reading project context and break conventions
- Retry failing builds with random fixes instead of stopping
- Deploy without verifying the build succeeded
- Attempt to fix infrastructure issues (Firebase, DNS, permissions) they can't resolve

This skill eliminates all of that by enforcing a strict phase-gate protocol.

## The Protocol

### Phase 0 — Context (~30 seconds)

Read `CLAUDE.md` at the project root. This file contains project-specific rules: architecture,
naming conventions, deploy targets, what NOT to do. Without it, you're flying blind.

If `CLAUDE.md` doesn't exist, tell the user:
> "No CLAUDE.md found. I don't have project context. Want me to scan the project and create one first, or proceed without it?"

Do not proceed to Phase 1 until you understand the project's deploy setup (hosting targets,
build commands, which services to skip).

### Phase 1 — Plan (~1 minute)

State what you're about to do. Do NOT change any files. List:

1. **Files to stage** — which files changed and what the changes are
2. **Commit message** — draft it, show it
3. **Build command** — what you'll run (e.g., `npm run build`)
4. **Deploy command** — what you'll run (e.g., `firebase deploy --only hosting`)
5. **What you're NOT deploying** — explicitly state skipped services (functions, rules, etc.) if applicable

Wait for user confirmation before proceeding. If the user says "go" or "yes" or "do it", proceed.
If context is unambiguous and the user already said "go" in the triggering message, you may proceed
without waiting — but still show the plan.

### Phase 2 — Execute (~2 minutes)

Stage and commit. Run verification between staging and committing:

```bash
# Stage
git add <specific files>

# Verify — confirm no console.log or debug artifacts remain
grep -rn "console\.\(log\|warn\|error\|debug\)" <staged files> | head -20

# Commit (only if verification passes)
git commit -m "<message>"
```

If the grep finds issues, STOP. Show the findings. Ask the user if they want to clean up first or commit anyway.

If the commit fails (hooks, merge conflicts, etc.), STOP. Show the exact error. Do not attempt to fix.

### Phase 3 — Build (~5 minutes)

Run the build command from the project root:

```bash
npm run build
```

If the build fails, STOP. Show the exact error output. Do not attempt to fix. Say:
> "Build failed. Here's the error. Want me to investigate, or do you want to handle it?"

If the build succeeds, confirm:
> "Build succeeded. Proceeding to deploy."

### Phase 4 — Deploy (~2-10 minutes)

Run the deploy command:

```bash
firebase deploy --only hosting
```

Use the deploy target specified in CLAUDE.md or the user's instructions. If neither exists,
ask which target to deploy.

If deploy fails, STOP. Show the exact error. Do not retry. Say:
> "Deploy failed. Here's the error. This is usually an infrastructure/permissions issue — want me to investigate or do you want to handle it?"

If deploy succeeds, confirm with the live URL:
> "Deployed successfully. Live at <url>."

## Hard Rules

1. **Never retry a failed command.** Show the error. Wait.
2. **Never attempt to fix build/deploy errors autonomously.** These are often infrastructure, permissions, or config issues that require human judgment.
3. **Never deploy functions unless explicitly asked.** Default to `--only hosting`. Cloud Functions have cold-start timeouts, dependency issues, and billing implications that are separate from frontend deploys.
4. **Always verify before committing.** The 10-second grep catches 90% of accidental debug code.
5. **One phase at a time.** Complete each phase fully before starting the next.
6. **If context is > 60%, suggest `/compact` before starting.** Heavy context causes timeouts and spiral.

## Multi-Project Deploys

When deploying multiple projects (e.g., AVT + CarMatch), run them sequentially, not in parallel.
Complete all 4 phases for Project A before starting Phase 0 for Project B.
This prevents cross-contamination of errors and keeps the failure surface small.

## Common Deploy Targets

These are reference patterns. Always defer to CLAUDE.md for the actual project config.

| Platform | Hosting Only | Functions Only | Everything |
|----------|-------------|---------------|------------|
| Firebase | `firebase deploy --only hosting` | `firebase deploy --only functions` | `firebase deploy` |
| Vercel | `vercel --prod` | n/a | `vercel --prod` |
| Netlify | `netlify deploy --prod` | `netlify functions:deploy` | `netlify deploy --prod` |

## Timing Expectations

| Phase | Typical Duration | If Exceeding |
|-------|-----------------|--------------|
| 0 — Context | 30s | Something's wrong with file access |
| 1 — Plan | 1 min | You're overthinking it |
| 2 — Execute | 2 min | Git issue — stop and report |
| 3 — Build | 5 min | Large project or dependency issue |
| 4 — Deploy | 2-10 min | Network/infra dependent |

Total: ~10-20 minutes for a standard deploy cycle.

## Recovery Patterns

**Build fails with missing dependency:**
> Stop. Show error. Do not run `npm install` unless the user explicitly asks.

**Deploy fails with auth/permission error:**
> Stop. Show error. This requires the user to re-authenticate (`firebase login`) or fix IAM permissions.

**Deploy fails with "functions timeout":**
> Stop. This is a Cloud Functions issue, not a hosting issue. Suggest: "Try `firebase deploy --only hosting` to skip functions."

**Git commit fails with hook error:**
> Stop. Show the hook output. Do not use `--no-verify`. The hook caught something real.

**Context window above 70%:**
> Suggest `/compact` or `/clear` before starting. Heavy context causes agent timeouts.
