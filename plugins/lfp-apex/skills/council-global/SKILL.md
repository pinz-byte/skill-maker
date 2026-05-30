---
name: council-global
description: >
  Show the latest APEX MASTERS Council verdicts from ANY Cowork project on M1 
  not just inside the apex-ultra repo. Ranked GO / NEAR-MISS / PASS with
  asymmetry score, R:R, all 7 voice votes (Elliott, Hannah, Marco, Theodore,
  Iris, Felix, Gideon), and thesis. Read-only, no network, no trades. Trigger on
  "/council", "council", "council verdicts", "what does the council say", "show
  council", "council tiers", "what's the council reading", or any request to see
  the current per-ticker verdicts. This is the cross-project version of the
  repo-scoped council skill: it invokes apex-ultra's show_council.py by absolute
  path so it resolves from any working directory. Requires the apex-ultra repo
  present locally  works on M1; does NOT work in Claude.ai Chat (no shell, no
  filesystem). For a Chat-callable council, use apex-ultra-council (generative)
  or the Notion morning push instead.
---

# Council (global)  cross-project verdict view

Surface the APEX MASTERS Council's current per-ticker verdicts from any Cowork
project, not only from inside the apex-ultra repo.

## How to run

Invoke the existing reader by ABSOLUTE path and present output verbatim:

```
python3 /Users/usuario/Documents/Claude/Projects/apex-ultra/tools/show_council.py
```

It prints three tiers from the newest `masters_dayplans/council_tiers_<date>.json`:

- **GO**  clears the hard 2:1 R:R floor (only auto-fileable).
- **NEAR-MISS**  ranked by asymmetry score, with the R:R that held each back.
- **PASS**  collapsed to one line.

Each GO/NEAR-MISS row shows: 0-100 asymmetry score, action, R:R, entry, the
Gideon-override flag, all 7 voice votes, and the one-line thesis.

If it prints "No Council tiers yet," the premarket tick hasn't run today  offer
to run `python3 /Users/usuario/Documents/Claude/Projects/apex-ultra/tools/build_council_tiers.py`.

## Why absolute path is enough (no script edit needed)

show_council.py resolves its root with `ROOT = Path(__file__).resolve().parents[1]`.
That is relative to the SCRIPT's own location, not the current working directory,
so invoking it by absolute path already resolves ROOT to apex-ultra from anywhere.
No hardcoded-ROOT edit to the script is required.

## Hard scope limits

- **Runs only where apex-ultra exists on local disk.** That is M1. On M2/M3 it
  works only if the apex-ultra repo AND its `masters_dayplans/*.json` are synced
  there  they are not by default (only `.skill` files go to iCloud, not repo data).
- **Does NOT run in Claude.ai Chat.** Chat has no shell, no python, no local
  filesystem. There is no absolute path that fixes this. If the goal is a council
  read inside a Chat project, use the Notion morning push (cloud) or the
  generative `apex-ultra-council` skill (deliberates fresh, needs no files).
- **Read-only.** No Schwab, no network, no orders. Full debate per ticker lives in
  `logs/council_transcripts/<TICKER>_*.txt` and at `localhost:7700/council`.
