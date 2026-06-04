# Distribution detail (on-demand)

Skills are distributed via a private GitHub repo, NOT iCloud. iCloud sync proved
unreliable (M2 ran ~2 weeks stale, silently). Git is the source of truth:
deterministic, versioned, inspectable. (Established 2026-05-29.)

- Remote: `git@github.com:pinz-byte/skill-maker.git` (private; HTTPS form works too)
- M1 is the source of truth -- skills are authored and built here.
- After building a skill on M1: `git add -A && git commit -m "..." && git push`
- On M2/M3: `cd ~/Documents/Claude/Projects/skill-maker && ./sync-skills.sh`
  (runs `git pull` and lists exactly which `.skill` files changed so you know
  what to re-add)
- Install per workspace: Cowork -> Customize -> Skills -> + -> browse to the
  repo folder -> select the `.skill` -> confirm the toggle is ON.

Per-workspace install is manual and irreducible: git distributes the FILES
across machines; each Cowork workspace still adds + enables each skill
separately (Cowork isolates plugins per project on purpose). iCloud and
`deploy-plugins.sh` are legacy -- superseded by git.
