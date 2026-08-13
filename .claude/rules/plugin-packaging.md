# Rule: Plugin Packaging

## Required zip structure

```
name.plugin
├── .claude-plugin/plugin.json
└── skills/name/SKILL.md
```

Both files must be present. Cowork rejects plugins missing either.

## plugin.json required fields

```json
{
  "name": "skill-name",
  "version": "1.0.0",
  "description": "Under 1024 chars, no emoji",
  "author": {"name": "LFP Ecosystem"}
}
```

## Emoji stripping — always do this before packaging

```python
import re
content = re.sub(r'[^\x00-\x7F\n\r\t ]', '', content)
```
Reason: Cowork plugin validator rejects non-ASCII characters with a silent failure.

## Version bumping rules

- Patch (1.0.x): bug fixes, wording improvements, description tweaks
- Minor (1.x.0): new sections, new fields in message formats, new capabilities
- Major (x.0.0): breaking changes to message format or trigger interface

## Deploy after every build

```bash
./publish.sh
```
Never manually copy individual files — the script handles all plugins atomically.

## Verify before deploying

```python
with zipfile.ZipFile('name.plugin') as zf:
    print(zf.namelist())  # must show both required files
```
