#!/usr/bin/env bash
# ship-skill.sh <skill-name> — build a skill, commit it, and push to the private remote.
# Run on M1 (the source of truth). M2/M3 then run ./sync-skills.sh to pull.
#
# Example:  ./ship-skill.sh logic-thinker

set -euo pipefail
cd "$(dirname "$0")"

NAME="${1:-}"
if [ -z "$NAME" ]; then
  echo "Usage: ./ship-skill.sh <skill-name>"
  exit 1
fi
if [ ! -f "$NAME/SKILL.md" ]; then
  echo "ERROR: $NAME/SKILL.md not found — nothing to build."
  exit 1
fi

echo "== building $NAME =="
python3 build-skill.py "$NAME"

echo ""
echo "== committing + pushing =="
git add -A
git commit -m "feat($NAME): build + ship $NAME.skill"
git push

echo ""
echo "Shipped $NAME.skill. On M2/M3:  ./sync-skills.sh   then upload $NAME.skill per workspace."
