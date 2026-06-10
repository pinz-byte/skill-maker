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

# Self-refresh this machine's own Cowork so newly published skills are visible here immediately.
# (Marketplace is GitHub-sourced, so this pulls the commit just pushed.)
if command -v claude >/dev/null 2>&1; then
  echo ""
  echo "Refreshing this machine's marketplace cache..."
  claude plugin marketplace update lfp-skills || echo "  (update failed — run it manually)"
fi
echo ""
echo "Published. M2/M3 self-refresh via their daily launchd job, or run there now:"
echo "  claude plugin marketplace update lfp-skills"
