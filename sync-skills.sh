#!/usr/bin/env bash
# sync-skills.sh — pull the latest skills from the private remote and report what changed.
# Run on M1/M2/M3 to keep the .skill set at parity across machines.
#
# After it lists changed skills, re-add those in each Cowork workspace that needs them:
#   Customize -> Skills -> + -> browse to THIS folder -> select the .skill.
# (Updating a .skill still requires a manual re-add per workspace — Cowork caches the
#  installed copy. This script keeps the FILES current; activation stays manual.)

set -euo pipefail
cd "$(dirname "$0")"

echo "== sync-skills =="
echo "Folder: $(pwd)"
echo ""

before=$(git rev-parse HEAD 2>/dev/null || echo "none")
echo "Fetching latest from remote..."
git pull --ff-only
after=$(git rev-parse HEAD)

echo ""
if [ "$before" = "$after" ]; then
  echo "Already up to date — no skill changes since last sync."
else
  echo "Skills changed in this pull — RE-ADD these in your workspaces:"
  changed=$(git diff --name-only "$before" "$after" | grep '\.skill$' || true)
  if [ -n "$changed" ]; then
    echo "$changed" | sed 's/^/  * /'
  else
    echo "  (commit landed, but no .skill files changed)"
  fi
fi

echo ""
echo "All skills available in this folder ($(ls -1 *.skill 2>/dev/null | wc -l | tr -d ' ') total):"
ls -1 *.skill 2>/dev/null | sed 's/\.skill$//; s/^/  - /'
