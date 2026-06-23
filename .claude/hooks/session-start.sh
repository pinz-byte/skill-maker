#!/bin/bash
# SessionStart hook -- auto mount-check + continuity gate for SKILL MAKER.
#
# PURPOSE: inject mount facts into the agent's context on turn one of every
# session, so the "X folder isn't mounted this session" failure is caught
# before any work -- without the user having to type "reentry".
#
# EXPERIMENT MARKER: if the FIRED line below shows up in a fresh session's
# context, Cowork honors .claude/settings.json SessionStart hooks. If it never
# appears, Cowork ignores them and the CLAUDE.md behavioral directive is the
# only available lever.
#
# PORTABILITY: never hardcode /sessions/<name>/mnt -- it rotates every session.
# Mount detection uses the /sessions/*/mnt/ glob (session-agnostic). The script
# path is anchored on $CLAUDE_PROJECT_DIR by settings.json, not a literal path.

TS="$(date '+%Y-%m-%d %H:%M:%S')"
echo "=== [SKILL MAKER SessionStart hook FIRED @ ${TS}] ==="

# Where is this running? The Cowork sandbox exposes /sessions/*/mnt; native
# macOS does not. This tells us whether hooks execute in the sandbox or natively.
if ls -d /sessions/*/mnt >/dev/null 2>&1; then
  echo "hook-env: cowork-sandbox"
else
  echo "hook-env: native-or-unknown"
fi

# Detect mounted folders (sandbox only; harmless / empty elsewhere).
MOUNTS="$(ls -1 /sessions/*/mnt/ 2>/dev/null | grep -vE '^(outputs|uploads)$' | sort -u | paste -sd, -)"
if [ -n "$MOUNTS" ]; then
  echo "mounted: ${MOUNTS}"
else
  echo "mounted: (none detected)"
fi

# Locate the latest continuity seed so the agent can compare against its
# REQUIRED Mount Manifest. Prefer the project root, fall back to any mount.
SEED=""
if [ -n "$CLAUDE_PROJECT_DIR" ] && [ -f "$CLAUDE_PROJECT_DIR/CONTINUITY_SEED.md" ]; then
  SEED="$CLAUDE_PROJECT_DIR/CONTINUITY_SEED.md"
else
  SEED="$(ls -1t /sessions/*/mnt/*/CONTINUITY_SEED.md 2>/dev/null | head -1)"
fi
if [ -n "$SEED" ] && [ -f "$SEED" ]; then
  echo "seed: ${SEED}"
else
  echo "seed: (no CONTINUITY_SEED.md found)"
fi

echo "ACTION: Compare 'mounted' above against the REQUIRED folders in the latest"
echo "CONTINUITY_SEED Mount Manifest. If a REQUIRED folder is missing, STOP and"
echo "tell the user the exact Cowork picker name(s) to add before other work."
echo "=== [SKILL MAKER SessionStart hook END] ==="
exit 0
