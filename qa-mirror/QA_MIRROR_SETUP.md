# QA Mirror -- One-Time Setup

The `qa-mirror` skill captures a live phone mirror on the Mac. This is the
mirror setup. Done once; reused every QA session.

## Why a mirror instead of screenshots

Taking a screenshot on the phone writes it to Camera Roll unconditionally, and
iCloud fans it out to every device's Photos -- that is what contaminated both
galleries. A mirror shows the phone screen live on the Mac without capturing
anything to the phone. You stop taking phone screenshots entirely, so the
contamination stops at the source.

## Option A -- iPhone Mirroring app. Recommended: wireless AND windowed.

Requires macOS Sequoia 15+ and iOS 18+, same Apple ID on both, Bluetooth +
Wi-Fi on.

1. On the Mac, open the "iPhone Mirroring" app (Applications, or Spotlight).
2. Follow the one-time pairing prompt. The iPhone screen opens in a movable,
   phone-shaped window -- not fullscreen.
3. Park that window next to the chat. The phone stays locked; you drive it by
   clicking and typing inside the window.

This is the path that solves the AirPlay fullscreen problem: it is wireless
(no cable) and stays a window you can position. Use it unless your QA needs
you physically handling the device.

## Option B -- Wired QuickTime. For hands-on-device testing.

Use this when you must hold and tap the real phone (gestures, camera, sensors)
while the Mac shows it.

1. Connect the iPhone with a cable; tap "Trust" if prompted.
2. QuickTime Player -> File -> New Movie Recording.
3. Click the chevron next to the record button -> select your iPhone.
4. The live screen appears in a normal resizable window. Do NOT press record;
   the preview itself is the mirror. Resize/position it next to the chat.

## Avoid -- AirPlay receiver.

AirPlay screen mirroring forces the iPhone fullscreen on the Mac and will not
resize into a window. Only workable if you put it on a second display and keep
the chat on the main one. Prefer Option A or B.

## Using it

1. Get the mirror window up (Option A recommended).
2. In chat: "start QA" -- I take one grab to confirm I can read the phone.
3. Drive the QA (in the iPhone Mirroring window, or on the device if wired),
   then say "look" / "next".
4. I capture the live screen and comment on the QA state.

No phone screenshots, no files, no walking to the machine, no waiting on sync.

## Cleaning the existing contamination

The QA shots already polluting your libraries are not removed by switching to a
mirror. To clean them once:

- Phone: Photos -> Albums -> Screenshots -> Select -> delete the QA ones ->
  empty Recently Deleted.
- Mac: Photos app -> Media Types -> Screenshots -> remove QA shots. With iCloud
  Photos on, deleting on one device removes them everywhere.

Ask me to help script a Mac-side cleanup if the volume is large.

## If you also QA roaming (away from the desk)

The mirror only works at the desk. For on-device testing away from the Mac, the
right setup is push-to-folder: an iOS Shortcut triggered by Back Tap that takes
a screenshot and writes it straight to a Files folder (never Camera Roll),
synced to a watched folder the QA workspace reads. That is a separate build --
ask for it if your QA goes mobile. Do NOT use a Downloads Folder Action for
this; it silently relocates every image you download.
