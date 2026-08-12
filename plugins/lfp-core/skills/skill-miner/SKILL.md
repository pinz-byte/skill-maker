---
name: skill-miner
description: >-
  Analyzes session transcripts across all Cowork projects to surface friction patterns,
  repeated failures, and untapped opportunities  then generates ranked skill proposals ready
  to build in SKILL MAKER. Use this skill whenever the user says "mine sessions", "what skills
  should we build", "what are the pain points", "analyze transcripts", "skill proposals",
  "what keeps breaking", "find patterns", "what should we automate", "skill opportunities",
  "what do agents struggle with", or any request to discover skill ideas from real usage data.
  Also trigger when the user asks "what's causing the most overhead" or "where are agents
  wasting time". This is the intelligence layer that closes the loop between ecosystem usage
  and skill creation  run it periodically (weekly or when the backlog runs dry) to keep SKILL
  MAKER building the right things. NOT skillmaker-publish (ships finished skills) or
  soul-builder (writes SOUL.md): this only proposes what to build next.
metadata:
  intent: build
---

# Skill Miner

Reads session transcripts, finds what keeps breaking, and turns friction into
skill proposals. The goal is to eliminate rediscovery  patterns that appear
repeatedly across sessions are prime candidates for skills that solve them once
and permanently.

## How It Works

### Phase 1  Session Inventory

Call `list_sessions` to get the full session list. Extract:
- Session titles (reveal intent and domain)
- Frequency patterns (same title repeating = unresolved problem)
- Recency (last 30 days weighted higher)

Group by domain from the title:
- Herald/broadcaster sessions
- Morning routine sessions
- Context reconstruction sessions (reentry, continuity seed, resume)
- Cross-project sessions (bridge, integration, assessment)
- Build/deploy sessions
- Trading/finance sessions
- Any other clusters that emerge

### Phase 2  Transcript Sampling

For the top 3-5 friction clusters identified in Phase 1, read transcripts from
representative sessions. Use `read_transcript` with limit 20 on 2-3 sessions per
cluster.

What to look for in transcripts:
- Repeated tool calls that suggest the agent had to rediscover something
- User corrections ("no, not that", "that's wrong again")
- Sessions that start with context reconstruction before doing any real work
- The same multi-step sequence appearing in multiple sessions
- Errors that required multiple attempts to resolve
- Skills the agent tried to use that weren't available ("/skill-name not found")
- Tasks the agent completed from scratch that a skill could have handled in one step

### Phase 3  Pattern Classification

Classify each pattern into one of four categories:

**RECURRING FAILURE**  Something breaks repeatedly. Same error, same fix, same
overhead. High-value target: a skill that prevents the failure or speeds recovery.

**CONTEXT TAX**  Agent spends significant time reconstructing context before
doing real work. Signals a missing initialization or briefing skill.

**REINVENTED WHEEL**  Agent wrote the same helper code, ran the same sequence,
or performed the same research multiple times across sessions. Bundle it.

**MISSED TRIGGER**  Agent tried to use a skill that didn't exist, or clearly
needed one but didn't know to ask. Gap in skill coverage.

### Phase 4  Skill Proposals

For each pattern, generate a skill proposal in this format:

---
**[SKILL NAME]**  Category: [RECURRING FAILURE / CONTEXT TAX / REINVENTED WHEEL / MISSED TRIGGER]

**Problem:** What keeps happening. Be specific  cite the session titles or
transcript evidence.

**Proposed skill:** What it does in one sentence.

**Trigger phrases:** 3-5 phrases a user would actually say to invoke it.

**Value:** What overhead it eliminates. Estimate in sessions-per-week if the
pattern frequency makes that possible.

**Complexity:** LOW / MEDIUM / HIGH  how hard to build.

**Build priority:** IMMEDIATE / SOON / BACKLOG  based on frequency and value.
---

### Phase 5  Ranked Output

Present proposals ranked by: (frequency x value) / complexity.

IMMEDIATE priority items first. Give the user a clear "build this next" recommendation.

End with a one-line summary: "X patterns found across Y sessions. Top candidate: [name]."

## Principles

**Evidence over intuition.** Every proposal must cite actual session data  title
frequency, transcript quotes, or observable tool call patterns. No speculation
dressed as insight.

**Specificity is the standard.** "Herald keeps breaking" is not a proposal.
"Herald health monitor runs 3x/week because agents can't detect the silent circuit
breaker failure  a herald-diagnostics skill that checks consecutive_failures and
delivery queue status would eliminate this" is a proposal.

**Frequency beats severity.** A mild friction that appears 10x/week is worth more
than a catastrophic failure that happened once. Build for the pattern, not the
drama.

**Don't propose what already exists.** Check the installed skills before proposing.
A skill that duplicates reentry or self-audit is wasted effort. Propose extensions
or complements instead.

**Proposals are drafts, not mandates.** Present them for the user to approve,
reject, or reprioritize. The user knows context the transcripts don't reveal.

## Edge Cases

**If transcripts are too short to yield signal:** Note this. Some sessions are
quick and leave no useful trace. Compensate by sampling more sessions from that
cluster.

**If a pattern is already partially addressed by an existing skill:** Note the
gap specifically  "reentry exists but doesn't cover X" is more useful than
ignoring the pattern or proposing a full replacement.

**If the user asks to mine a specific project or time window:** Filter by cwd
path in the session list (each session has a working directory that identifies
the project) or by session recency before Phase 2.

**If no clear patterns emerge:** Say so directly. "Sessions are too diverse to
cluster  no high-frequency patterns in the last 30 sessions" is a valid finding.
Don't manufacture proposals from thin signal.
