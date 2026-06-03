# QA Sequence -- Capture Setup

`qa-sequence` reviews a recording of a QA pass and delegates the analysis to a
Sonnet subagent so the images never cost Opus. This is how you capture the
recording. Done per QA pass.

## Why record instead of letting the agent grab

If the Opus session takes the screenshots, the images enter the Opus context --
the exact cost you are trying to avoid. Capturing the recording OUTSIDE any
agent means the images live on disk, and only the cheap Sonnet subagent ever
reads them.

## 1. Create the recordings folder and mount it

```bash
mkdir -p ~/QA-Recordings
```

Mount `~/QA-Recordings` into this QA workspace (Cowork folder access), or the
subagent cannot read the file.

## 2. Record the QA pass

Get the phone mirror up first (iPhone Mirroring app preferred -- see the
qa-mirror setup). Then:

- QuickTime Player -> File -> New Screen Recording.
- Record just the mirror window (drag-select that region) to keep the file
  small and the frames clean.
- Run your QA flow on the phone.
- Stop the recording. Save it into `~/QA-Recordings/` as e.g.
  `pass-YYYY-MM-DD.mov`.

Alternative: the macOS shortcut Shift-Cmd-5 -> record a selected portion.

## 3. Review it

In chat: "review the QA sequence" (or point at the file). The skill spawns a
Sonnet subagent that extracts only the changed frames (mpdecimate) and returns
a QA timeline -- screen states and anomalies -- without ever loading the images
into Opus.

## Cost discipline

- Run QA in a FRESH, lean session. The subagent saves image tokens, but a
  bloated Opus session still reprocesses its whole context every turn.
- Keep recordings short and per-flow. One long recording of an entire day means
  more frames to review; one recording per QA flow keeps each review tight.
- Record the window region, not the full screen, so there is less to dedupe.

## If you want live commentary instead

Recording-then-review is not live. For live, on-demand looks while you test,
use the qa-mirror skill -- but those grabs run on Opus (the image enters the
main session). You are trading cost for immediacy: qa-sequence is cheap and
post-hoc; qa-mirror is immediate and Opus-priced. Pick per task.
