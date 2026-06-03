# QA Screenshot Loop -- Machine-Side Setup

The `qa-screenshot` skill is only the pickup half. This is the transport half:
getting the phone screenshot onto the build machine fast, into a folder the
QA workspace can read. One-time setup, all native macOS. No iCloud Photos.

## Why not iCloud Photos

iCloud Photos is eventually-consistent and battery-optimized -- seconds to
minutes of lag, unreliable. AirDrop on the same LAN is ~1 second, direct,
no cloud round-trip. That is the entire fix for the stall.

## 1. Create the inbox folder

```bash
mkdir -p ~/QA-Inbox
```

## 2. AirDrop the screenshot (one tap)

On the phone: take the screenshot -> tap the thumbnail or share icon ->
AirDrop -> select the build machine. It lands in `~/Downloads`.

AirDrop's destination is always `~/Downloads` and cannot be changed -- that
is why step 3 exists.

## 3. Folder Action to move images into the inbox (native, no install)

AirDrop drops into Downloads; the QA workspace reads QA-Inbox. A Folder
Action auto-moves new images across. Built into macOS via Automator.

Setup:

1. Open Automator -> New -> Folder Action.
2. At the top, set "Folder Action receives files and folders added to" =
   `Downloads`.
3. Add a "Run Shell Script" action, pass input "as arguments", with:

```bash
for f in "$@"; do
  case "$f" in
    *.png|*.PNG|*.jpg|*.JPG|*.jpeg|*.JPEG|*.heic|*.HEIC)
      mv "$f" "$HOME/QA-Inbox/" ;;
  esac
done
```

4. Save as "QA Inbox Mover".

Now every image added to Downloads (including AirDrops) is moved to QA-Inbox
within a second. Non-image downloads are left alone.

Trade-off: this also moves images you download in a browser to QA-Inbox. If
that is noisy, AirDrop to a different Mac user/folder, or tighten the filter
to screenshot dimensions. For most QA use the simple filter is fine.

## 4. Mount QA-Inbox into the QA workspace

In the Cowork project where you run QA, add `~/QA-Inbox` as the workspace
folder (or one of them). The agent can only read mounted folders -- if this
step is skipped, the skill will report an empty inbox even when files are
there.

## 5. Use it

1. On the phone: screenshot -> AirDrop -> build machine (one tap).
2. In the QA chat: "got the shot" / "next" / "it's in".
3. The skill reads the newest image, views it, continues QA.

## Verifying the chain

```bash
ls -lt ~/QA-Inbox | head        # newest screenshot should be on top
cat ~/QA-Inbox/.qa-state.json   # last image the skill processed
```

If a screenshot is missing from QA-Inbox: check it reached Downloads (AirDrop
accepted?), then that the Folder Action is enabled (right-click Downloads ->
Services -> Folder Actions Setup -> ensure "QA Inbox Mover" is on).

## Alternatives considered

- Syncthing over LAN: zero-touch (no AirDrop tap), but requires installing
  Syncthing on phone and Mac. Pick this if you want to drop the one tap.
- iOS Shortcut "Send to QA": a share-sheet shortcut saving to a synced Files
  folder. Cleaner targeting, but still needs a sync tool to reach the Mac.
- HTTP listener on the Mac: fastest and fully scriptable, but is custom infra
  to maintain. Overkill given AirDrop already hits ~1s on LAN.

For LAN + "one tap is fine", AirDrop + Folder Action is the minimal reliable
setup. Revisit Syncthing only if the manual tap becomes the bottleneck.
