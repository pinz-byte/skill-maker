---
name: disk-doctor
description: >-
  Mac disk space diagnosis and cleanup skill. Identifies what is eating disk space and
  generates safe, targeted cleanup commands -- with special knowledge of Claude's own data
  accumulation (vm_bundles, caches, sessions). Use whenever the user says "disk is full",
  "running out of space", "free up space", "clean my mac", "disk doctor", "disk cleanup",
  "what's taking space", "why is my disk full", "need more disk space", or any variation. Also
  trigger automatically when the bash sandbox fails to start with "Not enough disk space" or
  "Workspace unavailable" -- that is a disk emergency and this skill should fire immediately
  without waiting for the user to ask. Fire on "vm_bundles", "Claude taking up space", "claude
  sessions disk", or any mention of Claude app data eating storage. NOT machine-bridge
  (sandbox-to-machine handoff) or gcp-iam-resolver: Mac disk space only.
metadata:
  intent: diagnose
---

# Disk Doctor

Diagnose and clean Mac disk space. Specializes in the Claude/Cowork data accumulation
pattern that is the #1 recurring cause of full disks on LFP machines.

## When the Sandbox Is Dead

If the bash workspace fails with "Not enough disk space" or "Workspace unavailable",
the disk is critically full (usually <5 GB free). Skip bash -- use computer use to
open System Settings > General > Storage for the visual breakdown, then give the user
Terminal commands to paste. This skill works without the sandbox.

## Phase 1: Assess

Run these in Terminal (paste as one block):

```bash
echo "=== DISK FREE ===" && df -h / | tail -1
echo "=== TOP APP SUPPORT ===" && du -sh ~/Library/Application\ Support/* 2>/dev/null | sort -rh | head -15
echo "=== CLAUDE INTERNALS ===" && du -sh ~/Library/Application\ Support/Claude/*/ 2>/dev/null | sort -rh | head -10
echo "=== VM BUNDLES ===" && ls -lt ~/Library/Application\ Support/Claude/vm_bundles/
echo "=== CONTAINERS ===" && du -sh ~/Library/Containers/* 2>/dev/null | sort -rh | head -8
```

## Phase 2: Interpret the Output

### Claude vm_bundles (most common culprit, can hit 8-20 GB)

The `vm_bundles/` directory holds Linux sandbox VMs for Cowork sessions.

| Entry | What it is | Safe to delete? |
|---|---|---|
| `claudevm.bundle` (today's date) | ACTIVE session VM | NO -- deleting kills the current session |
| `warm` | Pre-warmed standby VM | YES -- rebuilds on next session start |
| Any bundle older than today | Dead session VM | YES |

Rule: delete everything except `claudevm.bundle` modified today.

```bash
# See what's there and when modified
ls -lt ~/Library/Application\ Support/Claude/vm_bundles/

# Delete the warm standby (typically 8 GB)
rm -rf ~/Library/Application\ Support/Claude/vm_bundles/warm

# Delete bundles older than 1 day (keeps today's active bundle safe)
find ~/Library/Application\ Support/Claude/vm_bundles/ -maxdepth 1 -mindepth 1 -mtime +1 -exec rm -rf {} +

# Verify
du -sh ~/Library/Application\ Support/Claude/vm_bundles/
```

### Claude Caches (safe to clear, rebuilds automatically)

```bash
rm -rf ~/Library/Application\ Support/Claude/Cache/*
rm -rf ~/Library/Application\ Support/Claude/Code\ Cache/*
rm -rf ~/Library/Application\ Support/Claude/GPUCache/*
```

### Claude local-agent-mode-sessions (session metadata, 1-5 GB typical)

Old session directories under `local-agent-mode-sessions/` accumulate. The active
session directory is the one touched today -- leave it. Delete the rest.

```bash
# See count and age
ls -lt ~/Library/Application\ Support/Claude/local-agent-mode-sessions/ | head -20

# Delete sessions older than 7 days
find ~/Library/Application\ Support/Claude/local-agent-mode-sessions/ \
  -maxdepth 1 -mindepth 1 -type d -mtime +7 -exec rm -rf {} +
```

### User Caches (~100-500 MB, some protected by macOS)

```bash
rm -rf ~/Library/Caches/*
# "Operation not permitted" errors on Apple system caches are normal -- ignore them
```

### Chrome Cache (close Chrome first)

```bash
rm -rf ~/Library/Application\ Support/Google/Chrome/Default/Cache/
rm -rf ~/Library/Application\ Support/Google/Chrome/Profile\ */Cache/
```

### Homebrew Old Versions

```bash
brew cleanup --prune=all
```

### Trash

```bash
osascript -e 'tell application "Finder" to empty trash'
```

## Phase 3: Verify

After cleanup, re-check:

```bash
df -h /
du -sh ~/Library/Application\ Support/Claude/
```

Expected recovery from a typical cleanup:
- vm_bundles warm: 8-12 GB
- Caches: 500 MB - 2 GB
- Old sessions: 500 MB - 2 GB
- Chrome: 100-500 MB

## Common Patterns on LFP Machines

From observed sessions (Jun 2026):

- **System Data 85 GB** on a 245 GB disk -- root cause was Claude vm_bundles (16 GB)
  + Google Chrome (7 GB) + accumulated app caches
- `vm_bundles/warm` alone was ~8 GB -- this single delete is usually the fastest win
- iOS backups were NOT present (no mobile backups to worry about)
- Docker not installed -- no Docker cleanup needed
- No Xcode DerivedData (empty dir)

## Safe vs. Risky Reference

| Safe to delete | Do NOT delete |
|---|---|
| `vm_bundles/warm` | `vm_bundles/claudevm.bundle` (today) |
| `Claude/Cache/*` | `Claude/claude-code/` |
| `Claude/Code Cache/*` | `Claude/Local Storage/` |
| Old sessions (>7 days) | Active session (today) |
| `~/Library/Caches/*` (ignoring permission errors) | Any Apple system container |
| Chrome cache | Chrome user profiles / bookmarks |
| Homebrew old versions | Homebrew cellar (installed formulae) |
| Trash | Anything in ~/Documents, ~/Projects |
