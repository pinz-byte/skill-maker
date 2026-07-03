#!/usr/bin/env bash
# install-refresh.sh — install a daily launchd job on THIS machine (run on M1/M2/M3)
# that keeps the lfp-skills marketplace current, so skills never run silently stale.
#
# The lfp-skills marketplace is GitHub-sourced, so `claude plugin marketplace update`
# pulls straight from GitHub into ~/.claude — it does NOT need the repo in ~/Documents.
# The wrapper therefore lives in ~/Library (NOT in ~/Documents): macOS TCC blocks
# launchd-spawned processes from executing or reading anything under ~/Documents,
# which is why the previous in-repo wrapper failed with "Operation not permitted".
#
# FIX (2026-07-03): `claude plugin marketplace update` only refreshes the
# marketplace's own metadata/cache — it does NOT bump plugins already installed
# from it. Those stay pinned to whatever commit was current at install time.
# Live incident: M3's lfp-core/lfp-thinkers were pinned 52 commits / 5+ weeks stale
# despite this job running daily, causing "Unknown skill: project-migrate" long
# after the skill was published. The wrapper below now ALSO loops every installed
# `@lfp-skills` plugin through `claude plugin update <plugin>@lfp-skills`.
# Machines that installed this job before 2026-07-03 are running the OLD
# marketplace-only wrapper until this script is re-run there.
#
# Run once per machine (and re-run after this 2026-07-03 fix):   ./install-refresh.sh
# Remove it later with:   ./install-refresh.sh --uninstall

set -euo pipefail

LABEL="com.lfp.skill-maker.refresh"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
SUPPORT="$HOME/Library/Application Support/lfp-skill-maker"
WRAPPER="$SUPPORT/refresh-run.sh"
LOG="$HOME/Library/Logs/$LABEL.log"
HOUR=8   # daily run time (24h). Change if you want a different slot.

if [ "${1:-}" = "--uninstall" ]; then
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || launchctl unload "$PLIST" 2>/dev/null || true
  rm -f "$PLIST" "$WRAPPER"
  rmdir "$SUPPORT" 2>/dev/null || true
  echo "Removed $LABEL (plist + wrapper). Log left at $LOG"
  exit 0
fi

# Resolve the claude CLI now; launchd jobs don't inherit your interactive PATH.
CLAUDE_BIN="$(command -v claude || true)"
for c in /opt/homebrew/bin/claude /usr/local/bin/claude "$HOME/.local/bin/claude"; do
  [ -z "$CLAUDE_BIN" ] && [ -x "$c" ] && CLAUDE_BIN="$c"
done
if [ -z "$CLAUDE_BIN" ]; then
  echo "ERROR: could not find the 'claude' CLI on this machine."
  echo "Install it / put it on PATH, then re-run ./install-refresh.sh"
  exit 1
fi
CLAUDE_DIR="$(dirname "$CLAUDE_BIN")"   # node usually sits next to claude (nvm/brew)

mkdir -p "$SUPPORT" "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"

# Write the wrapper the job runs. It touches ONLY ~/.claude (via claude) — no
# ~/Documents access, so no TCC wall. PATH is widened so claude can find node.
cat > "$WRAPPER" <<EOF
#!/usr/bin/env bash
set -uo pipefail
export PATH="$CLAUDE_DIR:/opt/homebrew/bin:/usr/local/bin:\$PATH"
echo "===== \$(date '+%Y-%m-%d %H:%M:%S') refresh start ====="
"$CLAUDE_BIN" plugin marketplace update lfp-skills 2>&1 || echo "marketplace update FAILED"
# Marketplace update alone does NOT bump plugins already installed from it — they
# stay pinned to their install-time commit (see 2026-07-03 incident above). Bump
# every installed lfp-skills plugin explicitly.
"$CLAUDE_BIN" plugin list 2>&1 | grep -oE '[A-Za-z0-9_-]+@lfp-skills' | sort -u | while read -r p; do
  echo "-- updating \$p --"
  "$CLAUDE_BIN" plugin update "\$p" 2>&1 || echo "update FAILED for \$p"
done
echo "===== \$(date '+%Y-%m-%d %H:%M:%S') refresh done ====="
EOF
chmod +x "$WRAPPER"

# Write the launchd plist: run at load + daily at $HOUR:00.
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$WRAPPER</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>$HOUR</integer><key>Minute</key><integer>0</integer></dict>
  <key>StandardOutPath</key><string>$LOG</string>
  <key>StandardErrorPath</key><string>$LOG</string>
</dict>
</plist>
EOF

# (Re)load it.
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || launchctl unload "$PLIST" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST" 2>/dev/null || launchctl load "$PLIST"

echo "Installed $LABEL"
echo "  claude:  $CLAUDE_BIN"
echo "  wrapper: $WRAPPER  (outside ~/Documents — TCC-safe)"
echo "  daily:   ${HOUR}:00  (+ once now at load)"
echo "  log:     $LOG"
echo ""
echo "Verify it ran:   sleep 5; tail -n 20 \"$LOG\""
