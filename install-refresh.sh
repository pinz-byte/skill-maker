#!/usr/bin/env bash
# install-refresh.sh — install a daily launchd job on THIS machine (run on M2 and M3)
# that keeps the lfp-skills marketplace current, so skills never run silently stale.
#
# What it does, once per day (and at load):
#   1. git pull  in this skill-maker repo  (refresh the marketplace source files)
#   2. claude plugin marketplace update lfp-skills  (re-read so Cowork sees changes)
#
# Run once per machine:   ./install-refresh.sh
# Remove it later with:   ./install-refresh.sh --uninstall
#
# Paths are resolved at install time on the machine that runs this — nothing is
# hardcoded, so it works on M2 and M3 regardless of username or repo location.

set -euo pipefail

LABEL="com.lfp.skill-maker.refresh"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
WRAPPER="$REPO_DIR/.refresh-run.sh"
LOG="$HOME/Library/Logs/$LABEL.log"
HOUR=8   # daily run time (24h). Change if you want a different slot.

if [ "${1:-}" = "--uninstall" ]; then
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || launchctl unload "$PLIST" 2>/dev/null || true
  rm -f "$PLIST" "$WRAPPER"
  echo "Removed $LABEL (plist + wrapper). Log left at $LOG"
  exit 0
fi

# Resolve the claude CLI now; launchd jobs don't inherit your interactive PATH.
CLAUDE_BIN="$(command -v claude || true)"
for c in /usr/local/bin/claude /opt/homebrew/bin/claude "$HOME/.local/bin/claude"; do
  [ -z "$CLAUDE_BIN" ] && [ -x "$c" ] && CLAUDE_BIN="$c"
done
if [ -z "$CLAUDE_BIN" ]; then
  echo "ERROR: could not find the 'claude' CLI on this machine."
  echo "Install it / put it on PATH, then re-run ./install-refresh.sh"
  exit 1
fi

# Write the wrapper the job actually runs.
cat > "$WRAPPER" <<EOF
#!/usr/bin/env bash
set -uo pipefail
echo "===== \$(date '+%Y-%m-%d %H:%M:%S') refresh start ====="
cd "$REPO_DIR" || exit 1
echo "-- git pull --"
git pull --ff-only 2>&1 || echo "git pull failed (continuing to marketplace update)"
echo "-- claude plugin marketplace update lfp-skills --"
"$CLAUDE_BIN" plugin marketplace update lfp-skills 2>&1 || echo "marketplace update failed"
echo "===== \$(date '+%Y-%m-%d %H:%M:%S') refresh done ====="
EOF
chmod +x "$WRAPPER"

mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"

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
echo "  repo:    $REPO_DIR"
echo "  claude:  $CLAUDE_BIN"
echo "  daily:   ${HOUR}:00  (+ once now at load)"
echo "  log:     $LOG"
echo ""
echo "Verify it ran:   tail -n 20 \"$LOG\""
