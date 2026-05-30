# Rule: Deploy Target

## All plugins go to iCloud

Every .plugin file built in this workspace must be deployed to iCloud Drive so that
M2 and M3 pick it up automatically on sync.

iCloud target path (native macOS):
  /Users/usuario/Library/Mobile Documents/com~apple~CloudDocs/Claude/Plugins/

## Always use deploy-plugins.sh -- never copy manually

```bash
bash "/sessions/relaxed-funny-pasteur/mnt/SKILL MAKER/deploy-plugins.sh"
```

The script is sandbox-aware: it detects whether it is running inside Claude's
sandbox or natively on macOS and resolves paths correctly in both environments.

## When to run

Run deploy-plugins.sh immediately after every plugin build or rebuild. Do not
consider a plugin "done" until it has been deployed to iCloud.

## Verify after deploy

```bash
ls ~/Library/Mobile\ Documents/com~apple~CloudDocs/Claude/Plugins/
```

All current .plugin files should appear. If the new plugin is missing, copy manually:

```bash
cp "/sessions/relaxed-funny-pasteur/mnt/SKILL MAKER/<name>.plugin" \
   ~/Library/Mobile\ Documents/com~apple~CloudDocs/Claude/Plugins/
```
