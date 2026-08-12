---
name: qa-mirror
description: >-
  Desk QA companion. The phone screen is mirrored to the Mac (iPhone Mirroring app preferred;
  QuickTime wired or AirPlay as fallbacks); this skill grabs the live screen on demand via
  computer control and comments on the QA state -- no phone screenshots, no files, no photo-
  gallery contamination. Use whenever the user says "look", "grab", "capture", "what's on
  screen", "check the phone", "see the phone", "look at the phone", "snapshot the phone", "QA
  this", "what do you see", or signals they just did something on the device they want eyes
  on. Also fire on session activation: "start QA", "QA mode", "I'm testing on the phone",
  "watch my QA", "mirror is up". Per-turn pull model -- there is no background watching; each
  grab captures the current live mirror. For the roaming case (testing away from the Mac, no
  mirror) this skill does not apply -- that needs a push-to-folder setup instead. NOT
  carmatch-intel (reads a data pipeline): this grabs the live mirrored phone screen.
metadata:
  intent: observe
---

# qa-mirror -- Desk QA via Live Phone Mirror

## What this is

For QA done at the desk with the phone mirrored to the Mac. Instead of taking
a screenshot on the phone, waiting for it to sync, and dragging it into chat,
the phone screen is shown live in a mirror window and this skill captures that
window on demand with computer control, then comments on what QA shows.

Why this shape:

- No phone screenshots are taken, so nothing lands in Camera Roll and neither
  the phone nor the Mac photo library gets polluted. The contamination problem
  is removed at the source, not rerouted.
- The mirror is always current, so every grab is the live state -- no transport
  latency, no waiting.

## Honest limit: on-demand, not autonomous

There is no background loop. A skill acts only on a chat turn -- it cannot
watch the mirror and inject frames between the user's messages. The model is
pull-on-ping: the user does something on the phone, says "look" (or "next",
"grab", any active-session ping), and the skill captures the current mirror
frame. Because the mirror is live, every ping returns the present state. Set
this expectation; do not imply a live video feed.

## Prerequisites

A mirror window must be visible on the Mac. See QA_MIRROR_SETUP.md. Preferred:
the macOS iPhone Mirroring app (Sequoia 15+ / iOS 18+) -- wireless, opens as a
movable phone-shaped window that parks next to the chat (not fullscreen). The
phone is locked and driven from the Mac. Fallback for hands-on-device testing:
wired iPhone -> QuickTime Player -> New Movie Recording -> select the iPhone
(do NOT press record; the preview is the live mirror, in a resizable window).
Avoid AirPlay receiver -- it forces fullscreen and will not window.

## Computer-use access

Before the first grab, ensure computer-use access to the mirror app (iPhone
Mirroring, or QuickTime Player). Call request_access for it. Both are normal
apps (full tier) -- screenshots, clicks, and bringing the window forward all
work. With iPhone Mirroring you can also drive the phone by clicking inside the
window. If access is not granted, ask for it rather than failing silently.

## Capturing a frame

1. If the mirror window is not frontmost or is occluded, bring it forward
   (open_application on QuickTime Player; switch_display if it is on another
   screen).
2. Take a screenshot of the screen.
3. Read the phone screen from that capture. If the desktop is cluttered, note
   the region the phone occupies and focus the QA reading there; zoom on the
   relevant area if detail matters.

## Continuing QA -- the actual job

Do not stop at "here is the screen." After each grab, advance the QA:

- Report what the current screen shows against the expected state or the active
  checklist item.
- Name anomalies precisely -- wrong copy, misaligned element, error state,
  unexpected navigation, slow render -- not "looks off."
- If comparing to a prior grab this session, state the delta.
- Prompt the next step ("tap into settings and say look") so the loop keeps
  moving.

The point is eyes-on-QA commentary, not an acknowledgement that a screenshot
was captured.

## Session model

On activation ("start QA" / "QA mode"):

1. Take one grab to confirm the mirror is visible and the phone screen is
   readable. If you see the QuickTime chrome but no phone screen, the mirror is
   not selected -- point at QA_MIRROR_SETUP.md.
2. Confirm whether the user wants any grabs saved (see Archiving).
3. From then on, treat short pings ("look", "next", "ok", "go") as capture-now.

## Archiving (optional, best-effort)

This architecture has no automatic per-shot file -- captures are live frames,
not saved screenshots. If the user wants a durable record, save a timestamped
copy of a grab to a QA archive folder on request ("save this one"). If the user
needs every shot archived as a file automatically, that is the push-to-folder
architecture's strength, not this one -- say so rather than pretending live
grabs leave a folder behind.

## Principles

- Mirror is the source of truth and always live; trust the current frame over
  any memory of a prior one.
- On-demand only. No background watching exists -- never imply otherwise.
- Capture then advance. A grab that does not move the QA forward wasted a turn.
- No contamination by design. If the user is still taking phone screenshots,
  redirect them: with the mirror up they should stop -- that is what keeps the
  galleries clean.

## Edge cases

- Mirror shows QuickTime chrome but black/no phone screen: the device source is
  not selected, or the phone is locked -- guide to re-select / unlock.
- Phone auto-locks mid-session: the mirror dims; have the user wake the device.
- Multiple displays: the mirror may be on a second screen -- use switch_display
  to find it.
- Browser/terminal in front of the mirror at capture time is fine for reading
  (screenshot captures the whole screen), but bring QuickTime forward if the
  mirror is occluded.
- AirPlay wireless mirror instead of wired: same flow, slightly more latency;
  the receiver window is the capture target.
- Existing contamination: the galleries already polluted by past QA shots are
  not cleaned by this skill -- offer a one-time bulk delete separately.
