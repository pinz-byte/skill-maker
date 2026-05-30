#!/bin/bash
# deploy-plugins.sh
# Copies all .skill files from SKILL MAKER to iCloud Drive/Claude/Plugins
# Run after any skill build to sync across M1, M2, M3

if [ -d "/sessions" ]; then
  # Sandbox session names change every session -- never hardcode them.
  # Resolve SRC relative to this script's own location instead.
  SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  DST="$HOME/Library/Mobile Documents/com~apple~CloudDocs/Claude/Plugins"
else
  SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  DST="/Users/usuario/Library/Mobile Documents/com~apple~CloudDocs/Claude/Plugins"
fi

mkdir -p "$DST"

count=0
for f in "$SRC"/*.skill; do
    [ -f "$f" ] || continue
    name=$(basename "$f")
    cp "$f" "$DST/"
    echo "  copied: $name"
    ((count++))
done

echo ""
echo "$count skill(s) deployed to iCloud Drive/Claude/Plugins"
echo "Available on M2 and M3 once iCloud syncs."
