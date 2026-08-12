#!/usr/bin/env bash
# publish.sh — rebuild the plugin marketplace from skill sources and push it.
# Run on M2 (canonical publisher) after editing any SKILL.md (or changing GROUPS in build-marketplace.py).
# Other machines auto-update from the marketplace on Cowork start (or `claude plugin marketplace update`).

set -euo pipefail
cd "$(dirname "$0")"

python3 build-marketplace.py

git add -A
if git diff --cached --quiet; then
  echo "Nothing changed — already published."
  exit 0
fi
git commit -m "skills: rebuild marketplace ($(date '+%Y-%m-%d %H:%M'))"
git push

# Self-refresh this machine's marketplace and every installed lfp-skills plugin.
# Marketplace update alone does not bump installed plugin pins.
if command -v claude >/dev/null 2>&1; then
  echo ""
  echo "Refreshing this machine's marketplace cache..."
  claude plugin marketplace update lfp-skills || echo "  (update failed — run it manually)"
  while read -r plugin; do
    [ -n "$plugin" ] || continue
    echo "Updating installed $plugin..."
    claude plugin update "$plugin" || echo "  (update failed for $plugin — run it manually)"
  done < <(claude plugin list 2>&1 | grep -oE '[A-Za-z0-9_-]+@lfp-skills' | sort -u || true)
fi
echo ""
echo "Published. Other machines self-refresh via their daily launchd job."
echo "For an immediate refresh there, run ./install-refresh.sh once to install/update that job."
