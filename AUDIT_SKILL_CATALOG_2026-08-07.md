# AUDIT REPORT -- SKILL MAKER skill catalog -- SYSTEM OVERSIGHT -- 2026-08-07
## Verdict summary
Overall: FAIL
## Claims / surfaces audited
Canonical skill inventory is complete and uniquely identifiable -> PASS -> 52 top-level directories contain `SKILL.md`; every frontmatter `name` matches its directory; no two canonical files have the same SHA-256.
Every canonical skill is assigned exactly once to a marketplace plugin -> FAIL -> `build-marketplace.py` assigns `audit-codex-build` and `codex-audit-handoff` twice inside `lfp-core`; 39 entries resolve to 37 unique skills.
Marketplace generation can validate safely without damaging the last good build -> FAIL -> `build-marketplace.py` regenerates `agent-bridge` and removes `plugins/` before its duplicate, missing-source, ungrouped, and metadata checks run.
Canonical sources and the last successful generated marketplace are at parity -> PARTIAL -> all previously generated skills match their ASCII-normalized canonical sources; `audit-codex-build`, `codex-audit-handoff`, and `builder-identity-check` are not yet generated because they are new and the current `GROUPS` duplication blocks rebuilding.
Generated `plugins/` copies are genuine catalog duplicates -> PASS -> they are deterministic distribution artifacts documented by the builder, not independent sources; existing generated copies match canonical normalized content.
Legacy root `.skill` bundles are part of the live catalog -> PASS -> 27 bundles are ignored and untracked; the live channel is the GitHub marketplace, so these are stale local artifacts rather than canonical catalog entries.
The skill router inventories the live catalog from the current distribution channel -> FAIL -> `toolbox/SKILL.md` enumerates the retired iCloud `.skill` directory and treats it as deployed truth.
The Codex project instructions accurately describe the marketplace -> FAIL -> `AGENTS.md` contains invalid `.Codex-plugin`, `~/.Codex`, `.Codex/rules`, and `Codex plugin` substitutions; the real paths and CLI are `.claude-plugin`, `~/.claude`, `.claude/rules`, and `claude plugin`.
The canonical and team marketplace catalogs are structurally separate and internally consistent -> PASS -> five LFP plugins contain 52 unique canonical skills; the ignored `team-toolkit` build contains 19 curated skills across four plugins, and every generated team copy matches its configured sanitized source.
Installed LFP plugins have a single current scope/version -> PARTIAL -> user-scope `lfp-core`, `lfp-copy`, and `lfp-thinkers` match HEAD `2c32b71542d4`; a second project-scope `lfp-core` remains enabled at `4da946450351` from 2026-07-15.
Audit-related skills are redundant copies of one behavior -> PASS -> `auditor-general`, `self-audit`, and `verify-loop` have distinct lifecycle roles; `audit-codex-build` and `codex-audit-handoff` have the highest measured overlap but implement opposite cross-tool directions and share builder identification through `builder-identity-check`.
Skill metadata satisfies current hard limits -> PASS -> all 52 frontmatters parse; names match directories; all descriptions are at or below 1,024 characters.
Skill metadata retains safe maintenance margin -> PARTIAL -> `inpositive-language` and `time-boundary` are exactly 1,024 characters; `project-handover`, `pwa-verify`, and `verify-loop` are 1,016-1,019 characters; `arise` is 1,004 characters.
Documentation and helper scripts consistently describe the live marketplace channel -> PARTIAL -> primary invariants and `docs/distribution.md` identify the marketplace correctly, but `build-skill.py`, `ship-skill.sh`, `sync-skills.sh`, `docs/build-pattern.md`, and `docs/file-structure.md` still present retired `.skill` workflows as executable paths.
## Evidence chains
Marketplace uniqueness -> Parsed `GROUPS` directly from `build-marketplace.py` -> found 54 entries but only 52 unique names, with two duplicated within `lfp-core` -> FAIL because the builder's own duplicate guard will halt the build.
Safe generation -> Read `main()` execution order -> registry regeneration and `shutil.rmtree(plugins_dir)` precede all fail-loud validation -> FAIL because an invalid catalog can delete the last generated marketplace before reporting the error.
Generated parity -> Compared each generated `plugins/<plugin>/skills/<skill>/SKILL.md` to the builder's ASCII-normalized canonical source -> all existing copies match; three new sources have no generated copy -> PARTIAL until a clean build succeeds.
Router inventory -> Read `toolbox/SKILL.md` Step 1 and Edge Cases -> both use the retired iCloud bundles as deployed truth despite `workspace-plugin-audit` and project invariants declaring that channel retired -> FAIL because routing can recommend stale or nonexistent catalog state.
Codex instructions -> Diffed `AGENTS.md` against `CLAUDE.md` and checked real repository paths plus the working `claude plugin list` command -> blind substitutions changed product names, commands, paths, and the reserved-name rule -> FAIL because Codex receives false build/distribution instructions.
Installed duplication -> Ran `claude plugin list` and compared hashes to repository HEAD -> user-scope LFP plugins are current at `2c32b71542d4`, while project-scope `lfp-core` is also enabled at `4da946450351` -> PARTIAL because scope precedence can surface stale behavior nondeterministically.
Legacy documentation -> Searched canonical docs, scripts, and skills for `.skill`, iCloud, Customize, and retired helpers -> live-channel corrections coexist with executable legacy instructions -> PARTIAL because an agent can still select the wrong distribution path.
## Findings by severity
P0 (broken/false claim): The current marketplace definition cannot build because two skills are duplicated in `GROUPS`; `AGENTS.md` gives Codex false canonical paths and CLI commands; `toolbox` inventories the retired distribution channel.
P1 (degraded): Marketplace validation is destructive-before-validating; three new skills are not packaged; a stale duplicate project-scope `lfp-core` install competes with the current user-scope install; legacy publishing scripts and docs remain actionable; six descriptions have little or no safety margin below the hard limit.
P2 (cosmetic/hygiene): Twenty-seven ignored legacy `.skill` bundles remain in the working directory; many canonical files contain non-ASCII characters that are intentionally stripped in the LFP marketplace copy, making source and shipped text visually different even when generation is working as designed.
## Repair path
1. Remove the two duplicate `GROUPS` entries and move every fail-loud validation ahead of registry mutation and `plugins/` deletion.
2. Correct only the invalid product/path/CLI substitutions in `AGENTS.md`; retain Codex-specific session guidance where it is genuinely different.
3. Replace `toolbox` iCloud enumeration with current installed-plugin and canonical-marketplace discovery, and refresh its category map for the current catalog.
4. Rebuild the marketplace and verify 52 unique skills, generated-source parity, valid frontmatter, and a clean second build.
5. Resolve the duplicate `lfp-core` installation deliberately: keep one intended scope and current hash, then restart the consumer application.
6. Turn retired `.skill` scripts into explicit legacy-only entry points or archive them, and update `docs/build-pattern.md` plus `docs/file-structure.md` so the default path is the marketplace.
7. Shorten descriptions at or above 1,000 characters to retain maintenance margin without weakening trigger coverage.
8. Optionally remove ignored root `.skill` bundles after confirming no external process still reads them.
## Not verified
Plugin installation and freshness on M1 and M3 were not reachable; `claude plugin list` evidence applies only to this machine.
Runtime trigger quality for all 52 skills was not empirically benchmarked; this audit checked construction, metadata, topology, distribution parity, and static intent overlap.
GitHub marketplace state beyond local HEAD was not fetched; network publication freshness was outside this local catalog audit.
