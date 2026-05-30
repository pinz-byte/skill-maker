#!/usr/bin/env bash
# install-automation.sh <publish|update> — install a launchd agent for hands-off skill sync.
#
#   publish   M1 (authoring machine): every 5 min, rebuild the marketplace and push if anything changed.
#   update    M2/M3 (mirrors): every 10 min, refresh the lfp-skills marketplace from the remote.
#
# All paths are resolved at runtime (no hardcoded user/home), so this works on any machine
# regardless of username or repo folder name. launchd does NOT load your shell profile, which
# is why we bake absolute paths into the generated plist.

set -euo pipefail

ROLE="${1:-}"
case "$ROLE" in
  publish|update) ;;
  *) echo "Usage: ./install-automation.sh <publish|update>"; exit 1 ;;
esac

REPO="$(cd "$(dirname "$0")/.." && pwd)"          # repo root (parent of automation/)
CLAUDE_BIN="$(command -v claude || true)"
LA="$HOME/Library/LaunchAgents"
LOGS="$HOME/Library/Logs"
mkdir -p "$LA" "$LOGS"

if [ "$ROLE" = "publish" ]; then
  LABEL="com.lfp.skillmaker.publish"
  PROG="<string>/bin/bash</string><string>$REPO/publish.sh</string>"
  INTERVAL=300
  BINDIR="$(dirname "${CLAUDE_BIN:-/opt/homebrew/bin/claude}")"   # for gh on PATH
else
  [ -n "$CLAUDE_BIN" ] || { echo "ERROR: 'claude' is not on PATH; install the Claude CLI first."; exit 1; }
  LABEL="com.lfp.skillmaker.update"
  PROG="<string>$CLAUDE_BIN</string><string>plugin</string><string>marketplace</string><string>update</string><string>lfp-skills</string>"
  INTERVAL=600
  BINDIR="$(dirname "$CLAUDE_BIN")"
fi

PLIST="$LA/$LABEL.plist"
cat > "$PLIST" <<PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array>$PROG</array>
  <key>EnvironmentVariables</key><dict>
    <key>PATH</key><string>$BINDIR:/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>HOME</key><string>$HOME</string>
  </dict>
  <key>StartInterval</key><integer>$INTERVAL</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>$LOGS/$LABEL.log</string>
  <key>StandardErrorPath</key><string>$LOGS/$LABEL.log</string>
</dict>
</plist>
PLISTEOF

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "Installed $LABEL (runs every ${INTERVAL}s)."
echo "  plist: $PLIST"
echo "  log:   $LOGS/$LABEL.log"
echo "To stop later: launchctl unload \"$PLIST\""
