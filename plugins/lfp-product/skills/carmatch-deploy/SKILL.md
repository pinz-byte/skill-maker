---
name: carmatch-deploy
description: |
  CarMatch.ai-specific deploy workflow with full project context  targets, codebases, gotchas, and
  phase-gated discipline built in. Use this skill whenever deploying CarMatch, shipping CarMatch changes,
  or running any CarMatch build/deploy cycle. Triggers on: "deploy carmatch", "ship carmatch", "push carmatch",
  "carmatch deploy", "deploy the frontend", "deploy functions", "deploy hosting", or any deploy-related
  request when working inside the carmatch-ai repo. Also trigger when the user says "ship it" or "deploy"
  while the current working directory is carmatch-ai. This skill supersedes generic phased-deploy for
  CarMatch  it embeds the same phase discipline but adds project-specific context that eliminates
  re-discovery every session.
metadata:
  intent: build
---

# CarMatch Deploy

Project-aware deploy workflow for CarMatch.ai. This skill knows the exact architecture, targets,
codebases, and failure modes so you don't have to re-explain them every session.

## Project Identity

- **Repo:** `pinz-byte/carmatch-ai`
- **Live URL:** https://carmatch-ai-v0.web.app
- **Admin:** https://carmatch-ai-v0.web.app/#/admin
- **Firebase project:** `carmatch-ai-v0`
- **Hosting target:** `app` (serves from `dist/`)

## Architecture Context

CarMatch is an AI-powered car matching platform with MAX as the conversational concierge.

| Layer | Tech | Notes |
|-------|------|-------|
| Frontend | Vite 6 + React 18 | Single `src/App.jsx` (~4,500 lines) |
| Hosting | Firebase Hosting | Target: `app`, public dir: `dist` |
| Functions | 3 codebases, Node 22 | `functions-ai`, `functions-marketplace`, `functions-sync` |
| Database | Cloud Firestore | Rules: `firestore.rules`, indexes: `firestore.indexes.json` |
| Vector DB | Pinecone (1024-dim) | Used for signal embedding + matching |
| AI | Claude (claude-sonnet-4-20250514) | Intent extraction, archetype detection |
| Auth | Firebase Auth | Anonymous + Google admin |
| PWA | Service Worker + manifest | `sw.js` has no-cache header |
| Storage | Firebase Storage | Rules: `storage.rules` |

### File Structure (Key Files)

```
src/App.jsx               Entire frontend (~4,500 lines)
src/AdminDashboard.jsx    Backoffice component
src/firebase.js           Centralized Firebase init
functions-ai/index.js     AI Cloud Functions (captureIntent, refineSignal, claudeIntentAgent, etc.)
functions-marketplace/    Marketplace functions (createListing, getMyListings, submitOffer)
functions-sync/           Sync functions (processSignal, signalCounter)
functions/                Legacy directory (may still contain old functions  check before deploying)
firebase.json             All deploy targets
firestore.rules           Security rules
firestore.indexes.json    Composite indexes
storage.rules             Storage security rules
carmatch-claudecode.md    Project context doc (read this in Phase 0)
```

## Deploy Targets

These are the exact commands. Do not guess or improvise.

### Frontend Only (most common  ~80% of deploys)

```bash
npm run build && firebase deploy --only hosting:app
```

This is the default. When the user says "deploy" without qualification, this is what they mean.
Build output goes to `dist/`. The hosting target is `app`.

### Functions  By Codebase

Firebase is configured with 3 separate function codebases. Deploy them individually to avoid
cold-start cascades and billing surprises.

```bash
# AI functions only (captureIntent, refineSignal, claudeIntentAgent, embedSignal, getMatches)
cd functions-ai && npm install && cd .. && firebase deploy --only functions:ai

# Marketplace functions only (createListing, getMyListings, submitOffer)
cd functions-marketplace && npm install && cd .. && firebase deploy --only functions:marketplace

# Sync functions only (processSignal, signalCounter, saveSignal)
cd functions-sync && npm install && cd .. && firebase deploy --only functions:sync

# All functions (rarely needed  use only when explicitly asked)
cd functions-ai && npm install && cd .. && \
cd functions-marketplace && npm install && cd .. && \
cd functions-sync && npm install && cd .. && \
firebase deploy --only functions
```

Each codebase has its own `node_modules`. Always `npm install` in the function directory
before deploying  stale dependencies are the #1 cause of function deploy failures.

### Firestore Rules + Indexes

```bash
firebase deploy --only firestore:rules
firebase deploy --only firestore:indexes
firebase deploy --only firestore
```

Only deploy rules when `firestore.rules` or `firestore.indexes.json` actually changed.
Deploying rules unnecessarily can cause brief permission blips.

### Storage Rules

```bash
firebase deploy --only storage
```

### Full Deploy (rare  explicitly requested only)

```bash
npm run build && \
cd functions-ai && npm install && cd .. && \
cd functions-marketplace && npm install && cd .. && \
cd functions-sync && npm install && cd .. && \
firebase deploy
```

This deploys everything: hosting, all 3 function codebases, Firestore rules, indexes, and
storage rules. Only do this when the user explicitly says "full deploy" or "deploy everything."

## The Protocol

This follows the same phase-gate discipline as phased-deploy, but with CarMatch-specific
context pre-loaded.

### Phase 0  Context (~30 seconds)

1. Read `carmatch-claudecode.md` at the project root (this is the CLAUDE.md equivalent)
2. Run `git status` to see what changed
3. Determine deploy scope from what changed:
   - Only `src/` files changed  frontend only
   - Only `functions-ai/` changed  deploy functions:ai
   - Multiple areas changed  deploy each affected target
   - Rules files changed  include rules in deploy

If `carmatch-claudecode.md` doesn't exist, warn the user but proceed  this skill has enough
context to operate without it.

### Phase 1  Plan (~1 minute)

State what you're about to do. Show:

1. **Files to stage**  list them, explain what changed
2. **Commit message**  draft it
3. **Build command**  `npm run build` (if frontend changed)
4. **Deploy command(s)**  exact command(s) from the targets above
5. **What you're NOT deploying**  explicitly name skipped targets

Wait for user confirmation. If the user already said "ship it" or "deploy" in the triggering
message, show the plan but proceed without waiting.

### Phase 2  Commit (~2 minutes)

```bash
# Stage specific files
git add <specific files>

# Verify  no debug artifacts
grep -rn "console\.\(log\|warn\|error\|debug\)" <staged src files> | head -20

# Commit
git commit -m "<message>"

# Push
git push origin main
```

If grep finds console statements, STOP. Show them. Ask the user.
If the commit or push fails, STOP. Show the error. Do not attempt to fix.

### Phase 3  Build (~2-5 minutes)

Only if frontend changed:

```bash
npm run build
```

If the build fails, STOP. Show the error. The most common failures:
- Import errors in App.jsx (it's 4,500 lines  typos happen)
- Missing environment variables in firebase.js
- Vite config issues (check vite.config.js)

If functions changed, install dependencies in each affected codebase:

```bash
cd functions-ai && npm install && cd ..
```

### Phase 4  Deploy (~2-10 minutes)

Run the exact deploy command from Phase 1. Examples:

```bash
# Frontend only (most common)
firebase deploy --only hosting:app

# Frontend + AI functions
firebase deploy --only hosting:app,functions:ai

# Just marketplace functions
firebase deploy --only functions:marketplace
```

If deploy succeeds, confirm with: "Deployed. Live at https://carmatch-ai-v0.web.app"

If deploy fails, STOP. Show the error. Common failures:
- **Auth:** `firebase login` needed  tell the user
- **Functions timeout:** Suggest deploying hosting separately
- **Quota exceeded:** This is a billing issue  user must resolve
- **Target not found:** Check `.firebaserc` for correct project alias

## Hard Rules

1. **Default is hosting-only.** Unless the user says otherwise, deploy hosting only.
2. **Never deploy all functions casually.** 3 codebases  cold starts  billing = pain.
3. **Always npm install in function dirs before deploying functions.** Stale deps = deploy failures.
4. **Never retry a failed command.** Show error, wait.
5. **Never fix build/deploy errors autonomously.** Show error, suggest investigation.
6. **Always push before deploying.** The repo should reflect what's live.
7. **Check the legacy `functions/` directory.** If it still has code, warn the user  it may conflict with the new codebase structure.

## Quick Reference

| What Changed | Deploy Command |
|-------------|---------------|
| `src/` only | `npm run build && firebase deploy --only hosting:app` |
| `functions-ai/` only | `cd functions-ai && npm install && cd .. && firebase deploy --only functions:ai` |
| `functions-marketplace/` only | `cd functions-marketplace && npm install && cd .. && firebase deploy --only functions:marketplace` |
| `functions-sync/` only | `cd functions-sync && npm install && cd .. && firebase deploy --only functions:sync` |
| `firestore.rules` | `firebase deploy --only firestore:rules` |
| `firestore.indexes.json` | `firebase deploy --only firestore:indexes` |
| `storage.rules` | `firebase deploy --only storage` |
| Everything | Full deploy sequence (see above) |
| `src/` + one function codebase | Build, then `firebase deploy --only hosting:app,functions:<codebase>` |
