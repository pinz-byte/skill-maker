---
name: qa-screenshot
description: >
  Pickup half of the phone-to-machine QA loop. When you AirDrop a phone
  screenshot to the build machine, this skill finds the newest unprocessed
  image in the QA inbox folder, views it, and continues QA without you
  locating or dragging the file. Use whenever the user says "got the shot",
  "I airdropped it", "screenshot's in", "check the screenshot", "next shot",
  "next screenshot", "pick up the shot", "QA this screenshot", "newest
  screenshot", "grab the latest", "continue QA", "got mail from the phone",
  or signals a new phone screenshot just landed. Also fire on casual
  variations like "ok it's there", "should be in now", "ready", or "go"
  during an active QA session. Pairs with AirDrop transport and a Folder
  Action mover documented in QA_SETUP.md. This skill does NOT move images
  off the phone -- it consumes what AirDrop + the Folder Action deposit.
---

# qa-screenshot -- Phone Screenshot Pickup for QA

## What this is

The machine-side pickup for a fast phone QA loop. Transport (AirDrop) drops
phone screenshots into a watched inbox folder. This skill grabs the newest
unprocessed image, shows it, and keeps the QA flow moving -- so the user
never hunts for a file or waits on iCloud Photos sync.

This is half of a two-part system:

- Transport (not this skill): AirDrop screenshot -> build machine Downloads
  -> native Folder Action moves it to the QA inbox. See QA_SETUP.md.
- Pickup (this skill): read newest unprocessed image from the inbox, view,
  continue, mark seen.

## The inbox folder

Default convention: a folder named `QA-Inbox` mounted into the current
workspace. Resolve the path in this order:

1. A folder literally named `QA-Inbox` at the workspace root.
2. A path the user named earlier this session -- reuse it, do not re-ask.
3. If neither exists, ask once: "Which folder do AirDropped screenshots land
   in?" Then remember it for the rest of the session.

Cowork agents only see mounted folders. If the user says the screenshot is
there but the inbox is empty or unreadable, the likely cause is the folder is
not mounted into this workspace -- say so and point at QA_SETUP.md rather than
guessing.

## Picking the newest unprocessed image

Image types: `.png`, `.jpg`, `.jpeg`, `.heic`.

State file: `QA-Inbox/.qa-state.json` holding the last processed filename and
its mtime. On each pickup:

1. List image files in the inbox, sorted by mtime descending.
2. Take the newest one whose mtime is greater than the last processed mtime
   (or simply the newest, if no state exists).
3. If nothing is newer than last processed, say "no new screenshot since the
   last one" rather than re-showing the old image.
4. Read/view the chosen image.
5. Update `.qa-state.json` with that filename and mtime.

Never re-view an already-processed image unless the user explicitly asks
("show me the last one again").

## Continuing QA

After viewing, do not stop at "here's the screenshot." Continue whatever QA
context is active:

- If checking a specific screen or bug, report what the screenshot shows
  against the expected state.
- If comparing against a prior shot, diff visually and name the delta.
- If the user is walking a checklist, mark the relevant item and prompt the
  next step.

The point of the skill is to remove the file-shuffling stall, not to add a
"got it" acknowledgement. Move the QA forward.

## Batch mode

If several screenshots landed at once ("I sent three"), process them oldest
to newest, viewing and commenting on each, then update state to the newest.
Do not skip the middle ones.

## Principles

- Latency lives in transport, not here. If pickup feels slow, the bottleneck
  is the AirDrop/Folder Action chain or an unmounted folder -- diagnose there,
  do not retry reads in a loop.
- Idempotent by mtime. The state file is the source of truth for what is
  already seen; trust it over the user's memory of what was sent.
- One inbox per session. Resolve the folder once, reuse silently.
- Fail loud on mount gaps. An empty inbox the user swears is full means a
  mount or Folder Action problem -- name it, point at QA_SETUP.md.

## Edge cases

- Empty inbox: report it and check whether the folder is mounted before
  assuming the user is wrong.
- HEIC images: phone screenshots are usually PNG, but live photos / camera
  shots may be HEIC -- view them the same way; if a viewer cannot decode HEIC,
  convert with `sips -s format png` (macOS) or note the limitation.
- Stale state file: if `.qa-state.json` is corrupt or points at a deleted
  file, reset it to the newest image present and continue.
- Duplicate AirDrops: macOS appends ` 2`, ` 3` to repeat filenames. Treat
  each as a distinct file by mtime; do not assume a name collision means a
  re-send.
