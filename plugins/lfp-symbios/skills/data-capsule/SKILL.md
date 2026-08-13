---
name: data-capsule
description: |
  Captures a specific piece of discovered information from the current conversation and saves it as a
  standalone file in the project's capsules directory. Use this skill whenever the user says "save this",
  "capture this", "capsule this", "remember this", "store this", "log this", "note this down",
  "save that config", "keep this for later", "don't lose this", "bookmark this", or any request to
  preserve a discrete piece of information discovered during the session. Also trigger when the user
  says "data capsule", "save a capsule", or "capsule" followed by a description. This is NOT a session
  summary (use compact for that) or a full handoff (use continuity-seed). Data capsule captures ONE
  specific thing: a config, a schema, a credential location, a pricing structure, an API endpoint,
  a discovery, a contact detail, an environment variable  any atomic fact worth preserving as a
  standalone reference file. Think of it as a sticky note that lives in the project forever.
metadata:
  intent: orient
---

# Data Capsule  Atomic Knowledge Capture

Extracts a single piece of discovered information from the conversation and saves it as a
standalone, searchable file in the project. Each capsule is one fact, one config, one discovery 
small enough to scan in 5 seconds, permanent enough to reference in any future session.

## Why This Exists

Conversations are where knowledge gets discovered, but conversations die. The important config
you found at minute 47 of a 3-hour session? Gone. The API endpoint that took 20 minutes to
figure out? Buried in context. The pricing structure you finally decoded? Lost to `/compact`.

Data capsules extract these discoveries and give them a permanent address in the project.
Any future session can read them. Any future Claude instance knows what was found.

## When to Trigger

**Trigger on:**
- "Save this" / "capture this" / "capsule this" / "remember this"
- "Don't lose this" / "keep this for later" / "note this down"
- "Save that config" / "log that endpoint" / "store that schema"
- "Data capsule" / "capsule" followed by a topic
- Any request to preserve a specific discrete finding

**Don't trigger on:**
- Full session summaries  use `compact`
- Cross-session handoffs  use `continuity-seed`
- General note-taking or journaling  not this skill's job
- Saving code files  just write the file directly

**Proactive trigger:** If Claude discovers something non-obvious during work  an undocumented
API behavior, a config that took multiple attempts to get right, a workaround for a bug 
suggest capsulating it:
> "That took a while to figure out. Want me to capsule this so you don't have to rediscover it?"

## Step 1  Identify What to Capture

From the conversation, extract the specific piece of information. Ask yourself:

1. **What is it?** (config, endpoint, schema, credential path, pricing, contact, behavior, workaround)
2. **Why does it matter?** (was hard to find, is easy to forget, will be needed again)
3. **What's the minimum context needed to make it useful standalone?**

If the user said "save this" but it's ambiguous what "this" refers to, ask:
> "What specifically should I capsule? The [X] we just found, or the [Y]?"

## Step 2  Generate the Capsule

Each capsule follows this format. Keep it tight  a capsule that takes more than 30 seconds
to read is too long.

```markdown
# [Descriptive Title]
> Type: [config | endpoint | schema | credential | pricing | contact | behavior | workaround | reference]
> Project: [project name]
> Captured: [YYYY-MM-DD]
> Context: [1-sentence description of when/why this was discovered]

## Content

[The actual information. Be precise. Include exact values, paths, URLs, code blocks.
No fluff, no explanation beyond what's needed to use this info.]

## Usage

[How to use this info. A command to run, a file to edit, where to paste it.
Skip this section if the content is self-explanatory.]

## Source

[Where this came from  URL, API docs, error message, trial and error, etc.]
```

### Capsule Examples

**Config capsule:**
```markdown
# Firebase Functions Runtime Config
> Type: config
> Project: carmatch-ai
> Captured: 2026-03-20
> Context: Discovered during deploy debugging  functions need Node 22 explicitly set

## Content

All three function codebases require `"runtime": "nodejs22"` in firebase.json.
Without explicit runtime, Firebase defaults to Node 18 which breaks the Anthropic SDK.

\```json
{
  "source": "functions-ai",
  "codebase": "ai",
  "runtime": "nodejs22"
}
\```

## Source

Trial and error during first deploy. Firebase docs don't mention the default clearly.
```

**Endpoint capsule:**
```markdown
# Pinecone Upsert Endpoint for Signal Vectors
> Type: endpoint
> Project: carmatch-ai
> Captured: 2026-03-15
> Context: Found after testing multiple Pinecone API versions

## Content

- Index: `carmatch-signals`
- Dimension: 1024
- Metric: cosine
- Namespace: `production`
- Upsert URL: `https://carmatch-signals-xxxxx.svc.us-east-1.pinecone.io/vectors/upsert`

## Usage

Used by `embedSignal` Cloud Function. API key stored in Firebase Functions config,
not in code. Access via `functions.config().pinecone.api_key`.

## Source

Pinecone dashboard + functions-ai/index.js
```

## Step 3  Save the Capsule

### Naming Convention

Filename: `[date]_[type]_[slug].md`

Examples:
- `2026-03-20_config_firebase-functions-runtime.md`
- `2026-03-15_endpoint_pinecone-upsert.md`
- `2026-03-18_workaround_vite-build-memory-limit.md`

### Save Location

Save to a `capsules/` directory in the project root:

```bash
mkdir -p capsules
```

If running in Cowork without project access, save to outputs:

```bash
mkdir -p /mnt/user-data/outputs/capsules
```

### Create an Index

After saving, update (or create) `capsules/INDEX.md`:

```markdown
# Data Capsules  [Project Name]

| Date | Type | Title | File |
|------|------|-------|------|
| 2026-03-20 | config | Firebase Functions Runtime Config | 2026-03-20_config_firebase-functions-runtime.md |
| 2026-03-15 | endpoint | Pinecone Upsert Endpoint | 2026-03-15_endpoint_pinecone-upsert.md |
```

Append new entries to the bottom of the table. Don't rewrite existing entries.

## Step 4  Confirm

After saving, confirm briefly:

> "Capsule saved: **[title]**  `capsules/[filename]`"

No lengthy explanation needed. The user knows what they asked to save.

## Bulk Capture

If the user says "capsule everything important from this session," scan the conversation for:

1. Configs that were discovered or modified
2. Endpoints that were tested or confirmed
3. Workarounds for bugs or unexpected behavior
4. Schemas or data structures that were defined
5. Environment details that would be hard to re-derive

Generate one capsule per discovery. Don't merge unrelated findings into a single file 
each capsule should be independently useful.

## Reading Capsules

At session start, if a `capsules/` directory exists in the project, scan the INDEX.md
to understand what's already been captured. This prevents re-discovering known information
and prevents duplicate capsules.

When the user asks "what capsules do we have?" or "what did we capture?", read and
summarize INDEX.md.

## Relation to Other Skills

- **continuity-seed**  Seeds capture session state (what's in progress, what's next).
  Capsules capture atomic facts (a config, an endpoint). Seeds expire. Capsules are permanent.
- **compact**  Compact compresses everything. Capsules extract specific things.
  After a compact, the original context is gone  but capsules survive because they're files.
- **CLAUDE.md**  CLAUDE.md describes the project architecture broadly.
  Capsules capture specific discoveries that aren't part of the architecture doc.
  If a capsule is important enough, promote it into CLAUDE.md.
