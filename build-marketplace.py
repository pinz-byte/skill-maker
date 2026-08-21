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

import yaml

MARKETPLACE_NAME = "lfp-skills"
OWNER = {"name": "LFP (pinz-byte)"}
MARKETPLACE_DESC = "LFP ecosystem skills: oversight thinkers, core ops, and apex trading."

# plugin -> (description, [skill dirs])
GROUPS = {
    "lfp-pm": (
        "Project Manager loader -- pm-live reads the canonical PM protocol from Notion at invocation time, so protocol edits land everywhere instantly without republishing. Fresh plugin on purpose: breaks the stale account-store cache that pinned the old pm.",
        ["pm-live"],
    ),
    "lfp-thinkers": (
        "Oversight roundtable + router: critical, creative, logic, loop-breaker, ceo-planner, toolbox -- plus the Master Key creative process, the Intention Builder framework and extended-reasoning escalation.",
        ["critical-thinker", "creative-thinker", "logic-thinker", "loop-breaker",
         "ceo-planner", "toolbox", "masterkey", "ib", "ultrathink"],
    ),
    "lfp-core": (
        "Core ops/build/meta/comms/QA skills for every working project.",
        ["agent-bridge", "inbox-triage", "git-ops", "machine-bridge", "project-migrate",
         "self-audit", "reentry", "continuity-seed", "session-bootstrap", "soul-builder",
         "arise", "time-boundary", "session-rules", "meta-no-bare-names", "skill-miner",
         "workspace-plugin-audit", "gcp-iam-resolver", "gcloud-auth-doctor",
         "herald-config-doctor",
         "projectmd-auditor", "projectmd-optimizer", "offload", "auditor-general",
         "audit-codex-build", "codex-audit-handoff", "builder-identity-check", "qa-mirror",
         "qa-sequence", "pwa-verify", "carmatch-intel", "disk-doctor", "notebooklm-bridge",
         "space-steward", "inpositive-language", "project-handover",
         "skillmaker-publish", "verify-loop", "builder-handoff", "projectmd-gen",
         "project-init", "cc-session-analyzer", "work-retrospective", "forensic-auditor",
         "data-analyst", "live-builder-bridge", "coworker-enroll"],
    ),
    "lfp-apex": (
        "APEX live-money trading council and runtime health -- scope to trading projects only.",
        ["apex-builder-gate", "apex-ultra-council", "council-call", "council-debate",
         "council-global", "apex-health", "council", "council-run"],
    ),
    "lfp-copy": (
        "Tone and copy skills for VMC Subastas commercial content -- outreach sequences, marketplace listings, page copy and source grounding.",
        ["patel-tone-converter", "copy-masterkey", "vmc-listing-copy", "copy-deck",
         "voice-bench-gate"],
    ),
    "lfp-design": (
        "Personal-project design-system enforcement (non-Subastop) -- e-ink brand tokens and component drift checks.",
        ["astrodiary-ds-enforcer"],
    ),
    "lfp-product": (
        "Subastop / VMC / CarMatch product line -- build, deploy, design-system and pre-ship gates. Scope to product projects only.",
        ["brief-bridge", "dashboard-section", "ds-enforcer", "factory-gate", "carmatch-deploy",
         "phased-deploy", "source-scout", "pre-deliver", "dependency-audit"],
    ),
    "lfp-symbios": (
        "Symbios personal-OS layer -- session consciousness, capture and weekly continuity. Scope to Symbios and personal projects.",
        ["wake", "investigator", "data-capsule", "cowork-friday-handoff"],
    ),
    "lfp-labs": (
        "Narrow single-project instruments -- voice architecture and production series artwork. Install only where the project lives.",
        ["amorata-voice-system", "apu-series-generator"],
    ),
}

ROOT = Path(__file__).resolve().parent


def strip_non_ascii(s: str) -> str:
    return re.sub(r"[^\x00-\x7F\n\r\t ]", "", s)


def parse_frontmatter(skill_md_path: Path) -> dict:
    text = skill_md_path.read_text()
    if not text.startswith("---"):
        raise SystemExit(f"ERROR: {skill_md_path} missing YAML frontmatter (must start with '---')")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise SystemExit(f"ERROR: {skill_md_path} malformed frontmatter (need opening and closing '---')")
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        raise SystemExit(f"ERROR: {skill_md_path} invalid YAML frontmatter: {e}")
    return meta


def main():
    plugins_dir = ROOT / "plugins"

    # Dead-channel gate (added 2026-08-12). The retired per-.skill / iCloud pipeline
    # (build-skill.py, ship-skill.sh, sync-skills.sh, deploy-plugins.sh) shipped a SECOND
    # artifact for every skill. That is how 32 skills came to exist twice in the Cowork
    # account stores and 3 of them three times. The scripts are gone; this gate makes sure
    # a stray artifact or a resurrected script fails the build loudly instead of quietly
    # re-manufacturing duplicates.
    strays = sorted(
        [p.name for p in ROOT.glob("*.skill")]
        + [p.name for p in ROOT.glob("*.plugin")]
        + [n for n in ("build-skill.py", "ship-skill.sh", "sync-skills.sh", "deploy-plugins.sh")
           if (ROOT / n).exists()]
    )
    if strays:
        raise SystemExit(
            "ERROR: dead-channel artifacts present in repo root: "
            + ", ".join(strays)
            + "\n  There is exactly ONE channel: grouped plugins via this script + ./publish.sh."
            + "\n  See .claude/rules/deploy-target.md. Delete these; do not resurrect them."
        )

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

    # Fail-loud guard: catch the two known Cowork silent-rejection conditions
    # before packaging (per .claude/rules/skill-authoring.md) -- description
    # over 1024 chars, and "claude" appearing in the skill name (reserved word).
    # Same PRAETOR-inspired principle as the ungrouped-skill check above: catch
    # it at the one enforcement point that already works, before it ships.
    violations = []
    for skill in all_skills:
        meta = parse_frontmatter(ROOT / skill / "SKILL.md")
        name = str(meta.get("name", skill))
        desc = str(meta.get("description", ""))
        if len(desc) > 1024:
            violations.append(f"{skill}: description is {len(desc)} chars (limit 1024)")
        if "claude" in name.lower():
            violations.append(f"{skill}: name '{name}' contains reserved word 'claude'")
    if violations:
        raise SystemExit(
            "ERROR: skill(s) would be silently rejected by Cowork:\n  "
            + "\n  ".join(violations)
        )

    # All fail-loud checks must finish before mutating canonical or generated files.
    # This preserves the last known-good marketplace when a new catalog definition
    # is invalid.
    subprocess.run([sys.executable, str(ROOT / "gen-inbox-registry.py")], check=True)

    if plugins_dir.exists():
        shutil.rmtree(plugins_dir)  # regenerate clean only after validation passes

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


_BLOCK_ON_CHECK = True


def _post_build():
    """Regenerate CATALOG.md so the intent index never drifts from source.
    Added 2026-08-12 by wire-catalog.py. See CATALOG.md / intent-map.tsv."""
    import subprocess, sys as _sys
    audit = ROOT / "skill-intent-audit.py"
    if not audit.exists():
        print("  (skill-intent-audit.py absent -- CATALOG.md not regenerated)")
        return
    subprocess.run([_sys.executable, str(audit), "catalog", str(ROOT)], check=False)
    htm = ROOT / "make-catalog-html.py"
    if htm.exists():
        subprocess.run([_sys.executable, str(htm)], cwd=str(ROOT), check=False)
    if _BLOCK_ON_CHECK:
        r = subprocess.run([_sys.executable, str(audit), "check", str(ROOT)], check=False)
        if r.returncode != 0:
            raise SystemExit("build blocked: intent partition check failed")

if __name__ == "__main__":
    main()
    _post_build()
