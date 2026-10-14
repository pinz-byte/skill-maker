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
2. **Cowork ACCOUNT plugin store** (per account, what every Cowork/cloud session reads; proven
   again 2026-10-14: web, desktop and a cloud session all served the same snapshot) --
   Claude desktop app (2.37337.1): Customize -> Plugins -> Yours -> open ONE installed plugin
   (e.g. Lfp core) -> `Update`. That pulls the WHOLE marketplace snapshot for the account, not
   just that plugin: afterwards every lfp-* reads "On latest version" and the skill counts move
   (2026-10-14: Lfp core 46 -> 49, Lfp product 9 -> 8). Verify in a FRESH Cowork session.
   BROKEN as of 2026-10-14 (app 2.37337.1): the marketplace-level "Check for updates" (the `...`
   menu) fails every time with "Couldn't check for updates. Try again.", and "Add marketplace"
   only answers "already added". Do not fight that button; use a plugin's Update. The WEB UI
   (claude.ai Customize -> Plugins) has no update control at all. "Sync automatically" is
   documented for Cowork but was not found in this UI. Every plugin.json now carries a
   history-derived `version` and the CLI pins by it ("updated from <sha> to 1.62.0").
3. **Cowork ACCOUNT skills store** -- standalone uploads. Nothing new goes here, ever. Its
   existing contents are duplication debt being retired.

## Verify

Never verify a skill fix in the session that made it -- a session's plugin copy freezes at
session start. Open a FRESH session and read the loaded body.
