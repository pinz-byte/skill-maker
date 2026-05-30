#!/bin/bash
set -e

echo "Running SKILL MAKER pre-commit checks..."

PASS=true

# 1. Secret scan
staged=$(git diff --cached --name-only)
if git diff --cached | grep -iE '(sk-[a-zA-Z0-9]{20,}|Bearer [a-zA-Z0-9\-_.]{20,}|api_key\s*=\s*["\x27][^"\x27]{10,})' > /dev/null 2>&1; then
    echo "  FAIL: Possible API key or secret detected in staged files"
    PASS=false
fi

# 2. SKILL.md frontmatter validation
for skill_file in $(echo "$staged" | grep 'SKILL\.md$'); do
    if [ -f "$skill_file" ]; then
        if ! grep -q '^name:' "$skill_file"; then
            echo "  FAIL: $skill_file missing 'name:' in frontmatter"
            PASS=false
        fi
        if grep -P '[^\x00-\x7F]' "$skill_file" > /dev/null 2>&1; then
            echo "  FAIL: $skill_file contains emoji/non-ASCII (will break plugin packaging)"
            echo "        Fix: sed -i '' 's/[^ -~\t\n\r]//g' $skill_file"
            PASS=false
        fi
        echo "  OK:   $skill_file"
    fi
done

# 3. Plugin structure validation
for plugin_file in $(echo "$staged" | grep '\.plugin$'); do
    if [ -f "$plugin_file" ]; then
        python3 -c "
import zipfile, json, sys
try:
    with zipfile.ZipFile('$plugin_file') as zf:
        names = zf.namelist()
        assert '.claude-plugin/plugin.json' in names, 'missing .claude-plugin/plugin.json'
        assert any(n.endswith('SKILL.md') for n in names), 'missing skills/*/SKILL.md'
        meta = json.loads(zf.read('.claude-plugin/plugin.json'))
        assert 'name' in meta, 'plugin.json missing name'
        assert 'version' in meta, 'plugin.json missing version'
        assert len(meta.get('description','')) <= 1024, 'description > 1024 chars'
    print('  OK:   $plugin_file')
except Exception as e:
    print(f'  FAIL: $plugin_file — {e}')
    sys.exit(1)
"
    fi
done

if [ "$PASS" = false ]; then
    echo ""
    echo "Pre-commit checks FAILED. Fix above and retry."
    exit 1
fi

echo "All checks passed."
