#!/usr/bin/env bash
# publish.sh — rebuild the plugin marketplace from skill sources and push it.
# Run on M1 after editing any SKILL.md (or changing GROUPS in build-marketplace.py).
# M2/M3 then auto-update from the marketplace on Cowork start (or `claude plugin marketplace update`).

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
echo ""
echo "Published. M2/M3 pick it up on next Cowork start, or run there:"
echo "  claude plugin marketplace update lfp-skills"
