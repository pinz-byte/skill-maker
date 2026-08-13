---
name: council
description: >-
  Show the latest APEX MASTERS Council verdicts  ranked GO / NEAR-MISS / PASS with asymmetry
  score, R:R, all 7 voice votes, and thesis. Trigger on "/council", "council", "council
  verdicts", "what does the council say", "show council", "council tiers", "GO NEAR-MISS",
  "what's the council reading", or any request to see the Council's current per-ticker opinion
  without opening the dashboard. NOT council-run (fires a fresh intraday deliberation): this
  DISPLAYS the latest cached verdicts, read-only.
metadata:
  intent: decide
---

Show the APEX MASTERS Council's current per-ticker verdicts in chat.

Run this from the apex-ultra repo root and present the output verbatim (it is already formatted for reading):

```
python3 tools/show_council.py
```

It reads the newest `masters_dayplans/council_tiers_<date>.json` (written by the autonomous loop's premarket tick, or by `tools/build_council_tiers.py`) and prints three tiers:

- **GO**  verdicts clearing the hard 2:1 R:R floor (the only auto-fileable ones).
- **NEAR-MISS**  ranked by asymmetry score, with the R:R that held each back.
- **PASS**  collapsed to one line.

Each GO/NEAR-MISS row shows: the 0100 asymmetry score, action, R:R, entry, the Gideon-override flag, all 7 voice votes (Elliott / Hannah / Marco / Theodore / Iris / Felix / Gideon), and the one-line thesis.

If the script prints "No Council tiers yet," the loop hasn't run a premarket tick today  offer to run `python3 tools/build_council_tiers.py` to rebuild the view from saved transcripts.

Read-only: no Schwab, no network, no trades. It surfaces what the Council already decided. The full debate per ticker lives in `logs/council_transcripts/<TICKER>_*.txt` and on the dashboard at `localhost:7700/council`.
