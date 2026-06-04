---
name: offload
description: >
  Spin up a cheaper subagent (Sonnet or Haiku) on demand from inside an
  Opus-locked session to do heavy read/research/analysis work, so Opus stays
  the orchestrator and only ingests the small result. The Agent-tool model
  override is honored even when the session model picker is locked to Opus.
  Use whenever the user says "offload this", "delega esto", "delega a sonnet",
  "hazlo barato", "spinea un agente barato", "spin a cheap agent", "no gastes
  Opus en esto", "manda esto a un subagente", "delegate this", "cheap subagent
  for this", "haz esto con sonnet/haiku", or wants to avoid burning Opus on
  bulk or heavy work. Best for work a subagent can fully self-contain --
  reading large files, web research, multi-file code scans, data crunching --
  where Opus never needs to see the raw data. Not for work that needs Opus to
  read the data itself, nor for computer-use/screenshot capture in a subagent.
---

# offload -- Delegate Heavy Work to a Cheaper Subagent

## What this is

A locked-to-Opus session cannot change its own model -- not via the UI picker,
not via a skill. But the Agent tool's `model` parameter is a separate path that
the lock does NOT cover: from an Opus session you can spawn a subagent on
Sonnet or Haiku. This skill makes that a deliberate, on-demand move: push the
heavy lifting to a cheap subagent, keep Opus as the thin orchestrator that only
sees the distilled result.

Two wins, both verified in test: cost (the raw data and heavy tokens hit the
cheap model, not Opus) and speed (the test subagent returned in ~2s vs Opus
minute-scale turns).

## The load-bearing judgment: when delegation actually saves

Delegation saves only when the subagent can SELF-CONTAIN the heavy part and
return something small. Get this wrong and you save nothing.

Saves (delegate these):
- Reading/summarizing large files or folders -- the subagent reads from disk,
  Opus sees only the summary.
- Web research -- the subagent does the searches and fetches; Opus never
  ingests the pages.
- Multi-file code scans, grep-and-report across a repo.
- Bulk data crunching, transforms, extraction over a dataset.
- Anything repetitive over many items.

Does NOT save (do not pretend it does):
- Tasks where Opus must read the data itself to even frame the request -- if
  the raw data lands in Opus context anyway, delegating adds overhead.
- Tiny tasks -- subagent spin-up overhead exceeds the work.
- Live computer-use / screenshot capture -- a subagent's access to those tools
  is unreliable; capture on Opus, or keep that on the main thread.

The test: "can the subagent do this by reading from disk/web and hand me back a
short result?" If yes, offload. If Opus has to see the raw input regardless,
don't.

## How to delegate

When triggered, call the Agent tool with:

- `model`: "sonnet" by default (good quality/vision, far cheaper than Opus).
  Use "haiku" only when the user wants cheapest and the task is simple/bulk.
- `subagent_type`: "general-purpose" unless a specialized agent fits.
- A SELF-CONTAINED prompt. The subagent has a fresh context and cannot see this
  conversation -- hand it everything: the task, the exact file paths or URLs,
  the data, and the precise shape of the result you want back.
- Instruct it to return ONLY the distilled result, not the raw data, so Opus
  stays light.

For independent bulk work, spawn several subagents in one message so they run
in parallel.

Return the subagent's result to the user with minimal Opus commentary. Do not
re-ingest the raw data yourself -- that defeats the purpose.

## Verification (do once)

The override is honored in a locked session (tested: claude-sonnet-4-6, ~2s),
but self-report is weak evidence. Confirm conclusively in the usage dashboard:
after a delegated run, a Sonnet/Haiku line item should appear. If only Opus
shows, the lock reaches subagents too in your account and offload buys nothing
-- stop using it and say so.

## Honest limits

- Opus still runs every turn. Delegation removes the heavy delegated work from
  Opus, not the per-turn orchestration cost.
- Fresh context per subagent. It knows nothing you did not put in its prompt;
  no shared memory with this session.
- One-shot return. The subagent reports once at the end -- no streaming,
  no mid-run back-and-forth (unless you continue it via SendMessage).
- Capture tools unreliable in subagents -- keep computer-use on the main thread.

## Principles

- Heavy data never touches Opus. The whole point. If you find yourself reading
  the raw input in the main session, you have already lost the saving.
- Self-contained prompts. A subagent with a vague prompt and no data wastes the
  delegation. Over-specify.
- Sonnet by default, Haiku for cheap bulk, Opus only for the orchestration and
  the final judgment.
- Delegate batches, not trivia. Spin-up overhead must be smaller than the work.

## Edge cases

- Override silently ignored (account-wide lock reaches subagents): the dashboard
  shows Opus for the subagent run. Then offload is a placebo -- report it, stop.
- Subagent needs a tool it lacks: it will say so; re-scope what you hand it, or
  do that part on the main thread.
- Task too small: skip delegation, do it inline -- the round trip is not worth
  it.
- User wants the cheapest possible run on weak-vision or nuanced work: warn that
  Haiku may miss subtlety; default to Sonnet.
