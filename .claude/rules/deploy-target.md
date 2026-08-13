# Rule: Deploy Target
> Rewritten 2026-08-12. The previous version of this file was the manufacturing line for
> duplicated skills: it ordered every build deployed to iCloud as one-skill .plugin files,
> which is how 32 skills came to exist twice and 3 (agent-bridge, git-ops, reentry) three times.

## There is exactly ONE channel: the git marketplace

Skills ship as part of a GROUPED plugin (`lfp-core`, `lfp-thinkers`, `lfp-copy`, `lfp-apex`,
`lfp-design`) via `build-marketplace.py` + `./publish.sh`. Nothing else is a deploy target.

## Forbidden

- Do NOT build or ship `.skill` files. `build-skill.py`, `ship-skill.sh`, `sync-skills.sh`
  are DEAD. Any `.skill` on disk is an artifact of the retired channel, not an output.
- Do NOT deploy to iCloud. `deploy-plugins.sh` is DEAD; that channel is retired.
- Do NOT create one-skill plugins. Every new skill joins an existing GROUP in
  `build-marketplace.py`. A skill with no GROUP fails the build, by design.

## Shipping is a THREE-store ritual, not a push

`git push` reaches none of the Cowork stores. A skill is not "done" until all three are current:

1. **M2 local CLI** -- `./publish.sh` (runs `claude plugin marketplace update lfp-skills` +
   `claude plugin update <p>@lfp-skills` at BOTH `--scope user` and `--scope project`).
2. **Cowork ACCOUNT plugin store** (per account, what every Cowork/cloud session reads) --
   Claude desktop app: Customize -> Plugins -> Browse -> `Personal` -> the `···` beside the
   marketplace `skill-maker` -> refresh. THEN each plugin's `Update`. The per-plugin Update
   button reports "On latest version" while serving a stale build until that `···` refresh runs.
3. **Cowork ACCOUNT skills store** -- standalone uploads. Nothing new goes here, ever. Its
   existing contents are duplication debt being retired.

## Verify

Never verify a skill fix in the session that made it -- a session's plugin copy freezes at
session start. Open a FRESH session and read the loaded body.
