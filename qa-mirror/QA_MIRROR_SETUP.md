# QA Mirror -- One-Time Setup

The `qa-mirror` skill captures a live phone mirror on the Mac. This is the
mirror setup. Done once; reused every QA session.

## Why a mirror instead of screenshots

Taking a screenshot on the phone writes it to Camera Roll unconditionally, and
iCloud fans it out to every device's Photos -- that is what contaminated both
galleries. A mirror shows the phone screen live on the Mac without capturing
anything to the phone. You stop taking phone screenshots entirely, so the
contamination stops at the source.

## Option A -- Wired (QuickTime). Recommended: lowest latency, most reliable.

1. Connect the iPhone to the Mac with a cable. Tap "Trust" on the phone if
   prompted.
2. Open QuickTime Player.
3. Menu: File -> New Movie Recording.
4. In the recording window, click the small chevron/arrow next to the red
   record button.
5. Under Camera, select your iPhone. The live phone screen appears in the
   window.
6. Do NOT press record. The preview itself is the live mirror. Leave this
   window open and visible during QA.

## Option B -- Wireless (AirPlay). No cable, slightly more latency.

1. On the Mac, ensure AirPlay receiver is available (recent macOS: System
   Settings -> General -> AirDrop & Handoff -> AirPlay Receiver = on).
2. On the phone: Control Center -> Screen Mirroring -> select the Mac.
3. The phone screen appears in a window on the Mac. Keep it visible.

## Using it

1. Get the mirror window up (Option A or B).
2. In chat: "start QA" -- I take one grab to confirm I can see the phone.
3. Do whatever you are testing on the phone, then say "look" / "next".
4. I capture the live screen and comment on the QA state.

No screenshots, no files, no walking to the machine, no waiting on sync.

## Cleaning the existing contamination

The QA shots already polluting your libraries are not removed by switching to a
mirror. To clean them once:

- Phone: Photos -> Albums -> Screenshots -> Select -> delete the QA ones ->
  empty Recently Deleted.
- Mac: Photos app -> Media Types -> Screenshots -> remove QA shots. If iCloud
  Photos is on, deleting on one device removes them everywhere.

Ask me to help script a Mac-side cleanup if the volume is large.

## If you also QA roaming (away from the desk)

The mirror only works at the desk. For on-device testing away from the Mac, the
right setup is push-to-folder: an iOS Shortcut triggered by Back Tap that takes
a screenshot and writes it straight to a Files folder (never Camera Roll),
synced to a watched folder the QA workspace reads. That is a separate build --
ask for it if your QA goes mobile. Do NOT use a Downloads Folder Action for
this; it silently relocates every image you download.
