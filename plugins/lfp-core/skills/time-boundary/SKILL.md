---
name: time-boundary
description: >
  All-terrain time-awareness check for the start of any conversation, on any surface (Cowork M1/M2/M3, Claude.ai Chat) and any project -- not scoped to Symbios or to any one skill. Establishes how much time has passed since the last interaction using whatever signal is actually available, and states the boundary explicitly instead of letting conversational tone ("ok", "let's go", "hey") imply continuity that the clock doesn't support. Use at the start of any conversation, on any bare or casual opener, or any point where a heavier orientation skill (arise, reentry, session-bootstrap) is about to deliver continuity-dependent content -- this runs first and feeds them. Also trigger on "what time is it", "how long has it been", "check the time", "time boundary", "are we in a new session", "are you tracking time", or any request to be aware of elapsed time. Fire it even without being asked, before any state-dependent response, same as arise and reentry -- a skipped time check is a silent failure, not a harmless one.
---

## Why this exists

Session boundaries kept getting silently overwritten by conversational tone -- a bare "ok" read as continuation of something that actually closed hours earlier. The gap was never a missing feature in one project's skill; it was that no dependency-free check existed anywhere. A Notion-backed or Cowork-only check (see arise's Phase 2a) covers exactly one surface. This skill is the general version: it works with zero required tools, because a required tool is a single point of failure on any surface that doesn't have it wired up -- and "doesn't have it wired up" is exactly what happens on Chat.

## Protocol

### Step 1 -- Get a "now" signal, cheapest first

Try in order, stop at the first that resolves:

1. Session/environment context that already states the current date or time -- Cowork injects this automatically every turn; check there before calling anything.
2. A live time tool, if this environment exposes one.
3. If neither exists: say so plainly rather than guessing -- "no current-time signal available in this environment."

### Step 2 -- Get a "last contact" signal, cheapest first

Try in order, stop at the first that resolves:

1. Anything already loaded in this session that carries a timestamp: a continuity seed, a Continuity Feed entry (if arise already ran), project memory's last-modified note, or -- if this is a continuing thread, not a fresh one -- the timestamp of the prior turn.
2. If this is a genuinely fresh thread with nothing loaded: ask directly, one line, before doing anything continuity-dependent -- "How long has it been since we last talked?" This is not a failure state. The user is the one constant present on every surface; asking them is the correct all-terrain fallback when no system carries the answer.

### Step 3 -- State the boundary, don't imply it

Once both signals resolve (from a tool, from context, or from the user's own answer), do the arithmetic and say it in one line, before anything else: *"[X since last contact -- treating this as a new session]"* or *"[minutes since last turn -- continuing]"*. Never let a casual opener stand in for this line. Silence here is the exact failure this skill exists to close.

### Step 4 -- Hand off, don't duplicate

If a heavier orientation skill applies to this project (arise for Symbios, reentry, session-bootstrap), this check runs first and those skills read the Step 3 line rather than re-deriving their own boundary math. One source of truth for "how much time passed," reused everywhere -- not one implementation per project.

## Failure handling

**No time source anywhere, user doesn't answer**: proceed, but flag it once -- "operating with no time-boundary signal; if elapsed time matters for what we're doing, say so." Don't ask twice in the same session.

**Contradicts a loaded continuity artifact** (a seed says "2h ago," the user says "it's been three days"): trust the user's direct statement over any stored artifact. Stored state can be stale; the person talking to you right now cannot be.

**Multiple candidate "last contact" signals disagree** (CF entry says one thing, project memory says another): use the most recent one, name that you picked it, and don't silently average or guess.
