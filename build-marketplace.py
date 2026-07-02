#!/usr/bin/env python3
"""
build-marketplace.py — regenerate the plugin marketplace from skill sources.

The root <skill>/SKILL.md directories are the edit source of truth. This script
generates the committed marketplace tree:

    .claude-plugin/marketplace.json
    plugins/<plugin>/.claude-plugin/plugin.json
    plugins/<plugin>/skills/<skill>/SKILL.md   (+ references/ if present)

Run after editing any SKILL.md or changing GROUPS, then commit + push. Cowork/Claude
Code picks up changes on `/plugin marketplace update` (or background auto-update).

Usage: python3 build-marketplace.py
"""
import json, re, shutil, subprocess, sys
from pathlib import Path

MARKETPLACE_NAME = "lfp-skills"
OWNER = {"name": "LFP (pinz-byte)"}
MARKETPLACE_DESC = "LFP ecosystem skills: oversight thinkers, core ops, and apex trading."

# plugin -> (description, [skill dirs])
GROUPS = {
    "lfp-thinkers": (
        "Oversight roundtable + router: critical, creative, logic, loop-breaker, ceo-planner, toolbox.",
        ["critical-thinker", "creative-thinker", "logic-thinker", "loop-breaker", "ceo-planner", "toolbox"],
    ),
    "lfp-core": (
        "Core ops/build/meta/comms/QA skills for every working project.",
        ["agent-bridge", "inbox-triage", "git-ops", "machine-bridge", "project-migrate", "self-audit", "reentry",
         "continuity-seed", "soul-builder",
         "session-rules", "meta-no-bare-names", "skill-miner", "workspace-plugin-audit",
         "gcp-iam-resolver", "herald-config-doctor",
         "projectmd-auditor", "projectmd-optimizer", "offload", "auditor-general",
         "qa-mirror", "qa-sequence", "carmatch-intel", "disk-doctor", "notebooklm-bridge", "pm",
         "space-steward"],
    ),
    "lfp-apex": (
        "APEX live-money trading council -- scope to trading projects only.",
        ["apex-builder-gate", "apex-ultra-council", "council-call", "council-debate",
         "council-global"],
    ),
}

ROOT = Path(__file__).resolve().parent


def strip_non_ascii(s: str) -> str:
    return re.sub(r"[^\x00-\x7F\n\r\t ]", "", s)


def main():
    # Single source of truth for inbox UUIDs: regenerate agent-bridge's embedded
    # registry table from canonical (.claude/rules/inbox-registry.md) before packaging.
    # Fails loud if the markers are missing. Closes the hand-sync drift gap.
    subprocess.run([sys.executable, str(ROOT / "gen-inbox-registry.py")], check=True)

    plugins_dir = ROOT / "plugins"
    if plugins_dir.exists():
        shutil.rmtree(plugins_dir)  # regenerate clean

    all_skills = [s for _, (_, skills) in GROUPS.items() for s in skills]
    missing = [s for s in all_skills if not (ROOT / s / "SKILL.md").exists()]
    if missing:
        raise SystemExit(f"ERROR: missing SKILL.md for: {missing}")

    dupes = {s for s in all_skills if all_skills.count(s) > 1}
    if dupes:
        raise SystemExit(f"ERROR: skill listed in more than one group: {dupes}")

    # Fail-loud guard: every skill on disk must be assigned to a group, or it
    # silently never propagates to M2/M3. (Root cause of the projectmd-auditor
    # propagation gap, 2026-06-04.) A skill dir is any top-level dir holding a
    # SKILL.md; the generated plugins/ tree is excluded (no top-level SKILL.md).
    on_disk = {d.name for d in ROOT.iterdir()
               if d.is_dir() and (d / "SKILL.md").exists() and d.name != "plugins"}
    ungrouped = sorted(on_disk - set(all_skills))
    if ungrouped:
        raise SystemExit(
            "ERROR: these built skills are not in any GROUP and would NOT "
            f"propagate:\n  {ungrouped}\n"
            "Add each to a plugin in GROUPS (build-marketplace.py), then rebuild."
        )

    marketplace = {
        "name": MARKETPLACE_NAME,
        "owner": OWNER,
        "description": MARKETPLACE_DESC,
        "plugins": [],
    }

    for plugin, (desc, skills) in GROUPS.items():
        pdir = plugins_dir / plugin
        (pdir / ".claude-plugin").mkdir(parents=True, exist_ok=True)
        # plugin.json — omit "version" so each git commit = new version (auto-update)
        (pdir / ".claude-plugin" / "plugin.json").write_text(json.dumps({
            "name": plugin,
            "description": desc,
            "author": {"name": "LFP"},
        }, indent=2) + "\n")

        for skill in skills:
            src = ROOT / skill
            dst = pdir / "skills" / skill
            dst.mkdir(parents=True, exist_ok=True)
            (dst / "SKILL.md").write_text(strip_non_ascii((src / "SKILL.md").read_text()))
            refs = src / "references"
            if refs.is_dir():
                for f in refs.iterdir():
                    if f.is_file():
                        rdst = dst / "references"
                        rdst.mkdir(exist_ok=True)
                        (rdst / f.name).write_text(strip_non_ascii(f.read_text()))

        marketplace["plugins"].append({
            "name": plugin,
            "source": f"./plugins/{plugin}",
            "description": desc,
        })

    mp_dir = ROOT / ".claude-plugin"
    mp_dir.mkdir(exist_ok=True)
    (mp_dir / "marketplace.json").write_text(json.dumps(marketplace, indent=2) + "\n")

    print(f"Marketplace '{MARKETPLACE_NAME}' built with {len(GROUPS)} plugins, "
          f"{len(all_skills)} skills:")
    for plugin, (_, skills) in GROUPS.items():
        print(f"  {plugin}: {len(skills)} skills")


if __name__ == "__main__":
    main()
