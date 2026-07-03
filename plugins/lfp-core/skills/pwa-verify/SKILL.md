---
name: pwa-verify
description: >
  Post-deploy device verification protocol for PWAs (CarMatch, AVT, and any installed-PWA
  product in the ecosystem). Turns the manual "check it on the phone" loop into a checklist:
  bust the service-worker cache first, verify each fix from the deploy diff individually, then
  write an explicit VERIFIED / UNVERIFIED verdict per fix. Exists because stale service-worker
  bundles have repeatedly masked whether a fix landed -- one defect survived six deploys this
  way before the stale cache was identified as the root cause. Use whenever the user says
  "verify the deploy on device", "did the fix land on the phone", "pwa verify", "bust the cache
  and check", "runtime verify this", "check if it's live on the phone", "verify on device", or
  "hard reload and check". Also trigger proactively right after any CarMatch or AVT deploy,
  before declaring it done. Pairs with qa-mirror for the live screen capture at the desk, and
  with carmatch-deploy / phased-deploy for the deploy itself -- this skill starts where those
  leave off.
---

# PWA Verify -- Post-Deploy Device Verification

## Why this exists

A PWA's installed instance can keep running the old service-worker bundle indefinitely after a
deploy ships. A normal reload does not guarantee a new bundle is active. Skipping the cache-bust
step produces the worst kind of false positive: the fix looks broken (or looks fine) purely
because the device is still running old code, and either direction wastes a deploy cycle. This
is what let one defect survive six deploys before the pattern was caught.

**The rule: never declare a fix verified on-device without confirming the cache was busted
first.** A verdict issued against a stale bundle is not a verdict -- it is noise.

## Step 1 -- Build the fix checklist from the deploy diff

Before touching the device, turn the deploy into a list of individually verifiable claims. Read
the diff or commit message and extract one line per behavioral change:

```
Deploy: [commit hash / deploy tag]
Fixes to verify:
1. [specific behavior that should now happen] -- was: [what it did before]
2. [specific behavior] -- was: [what it did before]
```

Generic "check that it works" is not a checklist item. Each line must describe an observable,
falsifiable behavior on the device.

## Step 2 -- Bust the cache (mandatory, first, every time)

1. Force-close the PWA (do not just background it -- swipe it away / fully quit).
2. Reopen it. If the product exposes a build/version indicator (footer hash, about screen,
   console log), read it and confirm it matches the just-shipped deploy. If no version indicator
   exists, treat this as a gap worth flagging to the user, not something to skip past.
3. If the version does not match after a force-close and reopen, the service worker has not
   picked up the new bundle yet. Do not proceed to verification -- wait and retry, or escalate
   if it does not resolve within a reasonable window.

## Step 3 -- Walk the checklist, one fix at a time

For each line from Step 1:
1. Reproduce the exact steps that used to trigger the broken behavior.
2. Observe the actual result on the freshly-busted device.
3. Capture the screen at the moment of observation -- via qa-mirror if the phone is mirrored at
   the desk, or via a relayed device screenshot otherwise.
4. Record the verdict immediately, per fix, before moving to the next one. Do not batch
   observations and reconstruct verdicts from memory afterward.

## Step 4 -- Write back explicit verdicts

Never summarize a device pass as "looks good" or "seems fixed." Output one line per fix:

```
VERIFIED   -- [fix description] -- confirmed at [build/version], observed [what you saw]
UNVERIFIED -- [fix description] -- [why: still broken / cache stale / couldn't reproduce / no version indicator to confirm bundle]
```

A deploy with any UNVERIFIED line is not closed. Say so plainly rather than letting an
UNVERIFIED item quietly get treated as done.

## Principles

- **Stale service worker is the default suspect.** If a fix "isn't showing up" on device, assume
  a stale bundle before assuming the fix is wrong -- cache-bust again before debugging the code.
- **Verdict per fix, not per deploy.** A deploy can ship three fixes where two are verified and
  one isn't. Collapsing that into one pass/fail for the whole deploy hides the gap.
- **Capture at the moment of observation.** A screenshot taken after the fact, from memory of
  what the screen showed, is not evidence.
- **No version indicator is itself a finding.** If the product has no way to confirm which
  bundle is running, that's a gap worth surfacing (and a good candidate for a follow-up fix),
  not something to work around silently every time.

## Edge Cases

- **Product has no exposed version/build indicator:** fall back to timing -- wait a fixed window
  past the deploy plus one full force-close/reopen cycle, and note in the verdict that the bundle
  version could not be directly confirmed.
- **Multiple test devices:** run the full checklist independently on each; a verdict on one
  device does not transfer to another -- service worker update timing differs per device.
- **Can't force-close (testing via browser tab, not installed PWA):** a full hard-reload
  (clear-cache reload, not a normal refresh) is the substitute -- check devtools Application tab
  for the active service worker if available.
- **Fix depends on backend state, not just frontend bundle:** confirm the backend deploy landed
  too before blaming the device -- an UNVERIFIED result can originate server-side.
