#!/bin/bash
# SessionStart hook -- auto mount-check + continuity gate for SKILL MAKER.
#
# TWO SIGNALS, on purpose:
#   1. stdout FIRED marker  -> tests whether Cowork pipes hook stdout into the
#      agent's context. (First test came back: marker NOT in context.)
#   2. fired.log side-effect -> tests whether the hook EXECUTES AT ALL,
#      independent of stdout surfacing. A file write needs no context plumbing.
#
# Decision table after the next fresh session:
#   marker in context + log line present -> hook fires, stdout surfaced. DONE.
#   no marker        + log line present -> hook fires, stdout NOT surfaced.
#                                          -> switch strategy: hook should write
#                                             context to a file the agent reads,
#                                             or use a different surfacing path.
#   no marker        + no log line       -> Cowork ignores .claude/settings.json
#                                          SessionStart hooks. Behavioral CLAUDE.md
#                                          directive is the only lever. Abandon hook.
#
# PORTABILITY: never hardcode /sessions/<name>/mnt -- it rotates. Anchor on
# $CLAUDE_PROJECT_DIR; fall back to the session-agnostic glob.

TS="$(date '+%Y-%m-%d %H:%M:%S')"
echo "=== [SKILL MAKER SessionStart hook FIRED @ ${TS}] ==="

if ls -d /sessions/*/mnt >/dev/null 2>&1; then
  ENV="cowork-sandbox"
else
  ENV="native-or-unknown"
fi
echo "hook-env: ${ENV}"

MOUNTS="$(ls -1 /sessions/*/mnt/ 2>/dev/null | grep -vE '^(outputs|uploads)$' | sort -u | paste -sd, -)"
[ -n "$MOUNTS" ] && echo "mounted: ${MOUNTS}" || echo "mounted: (none detected)"

# --- side-effect probe: append a line to the first writable target ---
LINE="${TS} | env=${ENV} | cpd=${CLAUDE_PROJECT_DIR:-unset} | mounts=${MOUNTS:-none}"
SBX="$(ls -d /sessions/*/mnt/SKILL\ MAKER 2>/dev/null | head -1)"
WROTE=""
for tgt in "${CLAUDE_PROJECT_DIR}/.claude/hooks/fired.log" "${SBX}/.claude/hooks/fired.log" "/tmp/skillmaker_sessionstart_fired.log"; do
  d="$(dirname "$tgt" 2>/dev/null)"
  [ -d "$d" ] || continue
  if printf '%s\n' "$LINE" >> "$tgt" 2>/dev/null; then WROTE="${WROTE} ${tgt}"; fi
done
echo "fired-log: ${WROTE:-(none writable)}"

# --- seed locate + gate directive ---
if [ -n "$CLAUDE_PROJECT_DIR" ] && [ -f "$CLAUDE_PROJECT_DIR/CONTINUITY_SEED.md" ]; then
  SEED="$CLAUDE_PROJECT_DIR/CONTINUITY_SEED.md"
else
  SEED="$(ls -1t /sessions/*/mnt/*/CONTINUITY_SEED.md 2>/dev/null | head -1)"
fi
[ -n "$SEED" ] && [ -f "$SEED" ] && echo "seed: ${SEED}" || echo "seed: (none found)"

echo "ACTION: Compare 'mounted' against REQUIRED folders in the latest"
echo "CONTINUITY_SEED Mount Manifest. If a REQUIRED folder is missing, STOP and"
echo "name the exact Cowork picker folder(s) to add before other work."
echo "=== [SKILL MAKER SessionStart hook END] ==="
exit 0
