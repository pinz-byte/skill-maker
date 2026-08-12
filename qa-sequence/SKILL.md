---
name: qa-sequence
description: >
  Reviews a recorded QA pass cheaply by delegating all image analysis to a
  Sonnet subagent, so screenshot/frame tokens never hit an Opus-locked main
  session. Input is a screen recording (.mov/.mp4) or a folder of frames in a
  mounted QA folder; output is a QA timeline (timestamp -> screen state ->
  anomalies). Use whenever the user says "review the QA sequence", "analiza la
  grabacion", "review the recording", "revisa el clip", "analiza el mov",
  "qa sequence", "review the QA pass", "analiza la secuencia", "check the
  recording", or hands over a screen recording of a QA session. Also fire when
  the user wants QA analysis done without spending Opus on the images. This is
  the batch/recorded counterpart to qa-mirror (live, on-demand grabs); use
  qa-sequence when a recording exists and cost matters, qa-mirror for live
  single looks. Pairs with QA_SEQUENCE_SETUP.md for the capture step.
metadata:
  intent: audit
---

# qa-sequence -- Cheap Recorded-QA Review via Sonnet Subagent

## What this is and why it exists

The QA session is locked to Opus. Analyzing screenshots on Opus is the
expensive part (image tokens). This skill keeps every image off Opus: capture
happens outside any agent (a screen recording on disk), and all frame
extraction and visual analysis is delegated to a Sonnet subagent via the Agent
tool's model override. The Opus main thread only relays the subagent's text
report.

Result: you pay Sonnet rates for the vision work, Opus only for a short
hand-off. This is the legitimate version of "change the model on demand" -- a
skill cannot switch the session model (skills are prompts; the runtime owns the
model), but it CAN delegate the heavy work to a cheaper subagent.

## Hard limits -- state these, do not oversell

- Partial saving, not total. Delegation removes image tokens from Opus. It does
  NOT remove Opus reprocessing the main-session context each turn. For maximum
  saving, run this in a FRESH, lean session, not a bloated one.
- Not live. The recording is reviewed after the fact. There is no real-time
  commentary -- that is qa-mirror's job, and qa-mirror grabs run on Opus.
- Subagent model override depends on the runtime honoring it. If an org-level
  lock forces all inference to Opus, the override may not take effect. Verify
  once (see Verification) before assuming savings.

## Input

A screen recording or frame folder in a mounted QA folder (default
`QA-Recordings/`). Resolve the path: a folder named `QA-Recordings` at the
workspace root, else a path the user named this session, else ask once. The
folder must be mounted into this workspace or the subagent cannot read it.

Accepted: `.mov`, `.mp4` (recordings); or a folder of `.png`/`.jpg` frames.

## The delegation -- this is the core behavior

When triggered, do NOT analyze frames in the main (Opus) session. Spawn a
subagent with the Agent tool, `model: "sonnet"`, and hand it the file path plus
the instructions below. Return the subagent's report to the user with minimal
added commentary. Never read the frames/recording into the Opus context
yourself -- that defeats the entire purpose.

Subagent prompt to use (adapt the path):

  You are reviewing a recorded QA pass. Do not summarize lightly; produce a
  precise QA timeline.
  1. Ensure ffmpeg is available (install if needed).
  2. Extract only meaningfully-changed frames with mpdecimate, e.g.:
       ffmpeg -i <FILE> -vf "mpdecimate=hi=64*12:lo=64*5:frac=0.1,setpts=N/FRAME_RATE/TB" -vsync vfr <OUTDIR>/f_%04d.png
     If input is already a frame folder, skip extraction and dedupe visually.
  3. View the kept frames in order.
  4. Output a timeline: for each distinct screen state, give an approximate
     timestamp, what screen/state it is, and any anomaly (wrong copy,
     misalignment, error state, unexpected nav, broken layout, slow/blank
     render). Call anomalies precisely; do not say "looks off".
  5. End with a short list of the issues worth fixing, ordered by severity.
  Return the timeline and issue list as text only.

If the user wants the cheapest possible run and accepts weaker vision on fine
detail, use `model: "haiku"` instead. Default to sonnet -- haiku can miss
subtle UI defects.

## Verification (run once)

The first time, confirm the override is actually taking effect: after the
subagent returns, note whether the run behaved like a delegated call. If the
org lock overrides the model param, delegation buys nothing and the honest move
is to stop pretending it does -- tell the user and fall back to reviewing in a
lean session.

## Principles

- Images never touch Opus. The whole point. If you find yourself viewing frames
  in the main session, you have already lost the saving.
- Dedupe before analysis. mpdecimate first -- never analyze 40 identical frames
  of a static screen.
- Delegate batches, not single frames. Subagent overhead only pays off across
  many frames; for one live look, use qa-mirror and accept Opus.
- Precision over volume. A tight timeline of real state changes beats a frame
  dump.

## Edge cases

- Folder not mounted: the subagent reports it cannot read the path -- this is a
  mount gap, not a bad recording. Point at QA_SEQUENCE_SETUP.md.
- No ffmpeg: the subagent installs it (apt-get/pip) or falls back to sampling
  frames at a fixed interval.
- Very long recording: cap extracted frames (e.g. mpdecimate plus a max fps)
  so the subagent is not handed thousands of images.
- Recording includes desktop chrome around the phone window: tell the subagent
  to focus the phone region when reading.
