---
name: machine-bridge
description: >
  Hardening skill for the sandbox-to-machine handoff. Cowork agents run in a Linux sandbox
  whose session path rotates every session and whose mounts can lag the user's machine,
  producing a recurring failure class: scripts that hardcode a dead session path, commands
  shipped with literal placeholders the user pastes verbatim, and stale launchd/venv/git
  state on the machine. Use whenever you are about to hand the user a command to run on
  their machine, deploy across the sandbox-iCloud boundary, or commit from their terminal.
  Trigger on "run this on my machine", "give me the terminal commands", "deploy to icloud",
  "this path is broken again", "commit from my terminal", "it pasted the placeholder",
  "launchd is running an old version", or "the sandbox is behind". Also fire proactively
  before emitting any bash block the user will paste, and when you write or edit a
  deploy/launchd/cron script. Fire on "why did that command fail" when it is a placeholder
  or stale path.
---

# Machine Bridge

You run in a sandbox. The user runs on a Mac (M1/M2/M3). The two filesystems are different,
the sandbox session path rotates every session, and the machine's background state (launchd,
venv, git index) can be ahead of or behind what you see. Most "it broke again" loops in this
ecosystem trace to one of three handoff mistakes. This skill prevents all three.

## The Three Failure Modes

1. **Hardcoded session path.** A script bakes in `/sessions/<name>/...`. Session IDs rotate,
   so next session the path is dead and the script silently writes to nowhere (e.g. iCloud
   got a broken alias instead of real files because the deploy script hardcoded an old
   session path).

2. **Literal placeholder in a command.** You hand the user a command containing
   `YOUR_PROJECT`, `PROJECT_ID`, `<path>`, etc. They paste it verbatim and it errors. Every
   placeholder you leave in is a guaranteed failed paste.

3. **Stale machine-side state.** launchd runs an older copy of a script than the one in the
   sandbox; the venv exists on the machine but not the sandbox; a `.git/index.lock` from a
   sandbox-side git attempt blocks the machine commit. The sandbox mount lags the machine.

## Rules Before You Emit Any Machine Command

### Resolve paths at runtime — never hardcode a session

In scripts, derive the source from the script's own location, not a literal session path:

```bash
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
```

In one-off commands, use `$HOME` and stable project paths, never `/sessions/...`:

```bash
# good
cd "$HOME/Documents/Claude/Projects/<project>"
# bad — dies next session
cd /sessions/relaxed-funny-pasteur/mnt/...
```

If a doc or CLAUDE.md still shows a `/sessions/<name>/...` path in an example, that is a
latent version of failure mode 1 — flag it for replacement with the `$HOME` form.

### No literal placeholders — fill every value or refuse to emit

Before handing over a command, scan it for ALL-CAPS tokens, angle brackets, and `YOUR_`.
Each one must be resolved to a real value first. If you genuinely cannot know a value (e.g.
the user's GCP project ID), do not bury it in a runnable block — pull it out into a single
explicit "set this first" line so it cannot be pasted by accident:

```bash
PROJECT_ID=   # <-- fill this in, then run the block below
```

Better: discover it. `gcloud config get-value project`, `git remote -v`, `ls` — resolve the
value rather than asking the user to.

### Check machine-side staleness before blaming the code

When a launchd/cron job fails but the sandbox file looks clean, suspect a version mismatch,
not a bug. Have the user reload the agent against the current file rather than re-editing:

```bash
launchctl unload ~/Library/LaunchAgents/<label>.plist && \
launchctl load   ~/Library/LaunchAgents/<label>.plist
```

For git, a sandbox-side commit attempt can leave a lock the machine must clear:

```bash
rm -f "$HOME/Documents/Claude/Projects/<project>/.git/index.lock"
```

State explicitly when an operation must run on the machine (commits, launchd, anything
needing the local venv or real credentials) versus what you can do in the sandbox.

## Handoff Checklist (run mentally before every machine command)

- Paths use `$HOME` / runtime resolution, zero `/sessions/...` literals.
- Zero unfilled placeholders; every value is real or isolated on its own set-this line.
- Stated which side runs it (sandbox vs machine) and why.
- If launchd/cron/venv is involved, included the reload/clear step.
- If it crosses the iCloud boundary, used the self-resolving deploy script, not a manual cp
  with a hardcoded source.

## Principles

- **The sandbox is not the machine.** Anything needing real credentials, the local venv, or
  background daemons runs on the machine. Say so; do not let the user assume sandbox success
  means machine success.
- **A command with a placeholder is a broken command.** Treat an unfilled token as a bug you
  ship, not a note to the user.
- **Stale beats wrong-looking.** When machine output disagrees with a clean sandbox file, the
  default hypothesis is a version/mount lag, not a code error. Reload before you rewrite.
- Pairs with [[herald-config-doctor]] (unmounted report paths) and the project deploy script
  (which already self-resolves SRC — keep it that way).
- **Pairs with `builder-handoff` (VMC skill).** That skill fires on the same moment this one
  does -- about to hand the user a multi-step terminal sequence -- but takes the opposite
  move: instead of hardening the command for the human to run, it writes a BUILDER_PROMPT
  file for a builder-agent session to execute instead. When a BUILDER_PROMPT file is being
  generated, this skill's checklist still applies to the command blocks inside it -- a
  builder session is exactly as vulnerable to a hardcoded dead session path or an unfilled
  placeholder as a human pasting a command would be. Run the Handoff Checklist against the
  BUILDER_PROMPT's command blocks before considering it finished, not just against commands
  aimed directly at the user.
