#!/usr/bin/env python3
"""Build the Subastop AI team toolkit marketplace (curated subset).

Reads skill sources from this repo (single source of truth) and generates a
standalone repo tree in team-toolkit/ ready to push to a PRIVATE GitHub repo
(subascorp/ai-toolkit -- existing company org). Team installs with:
    claude plugin marketplace add subascorp/ai-toolkit

Curated: no apex, no agent-bridge/inbox UUIDs, no machine-specific skills.
Run natively (sandbox may block rmtree on mounts): python3 build-team-toolkit.py
"""
import json, re, shutil
from pathlib import Path

MARKETPLACE_NAME = "subastop-ai"
OWNER = {"name": "Subastop"}
MARKETPLACE_DESC = "Subastop AI team toolkit: oversight thinkers + core working discipline."

# plugin -> (description, [skill dirs])
TEAM_GROUPS = {
    "subastop-thinkers": (
        "Oversight roundtable: critical, creative, logic, loop-breaker, ceo-planner.",
        ["critical-thinker", "creative-thinker", "logic-thinker", "loop-breaker",
         "ceo-planner"],
    ),
    "subastop-core": (
        "Core working discipline: git, self-audit, continuity, context files, delegation, deploy verification.",
        ["git-ops", "self-audit", "continuity-seed", "soul-builder",
         "projectmd-auditor", "projectmd-optimizer", "offload", "auditor-general",
         "meta-no-bare-names", "pwa-verify"],
    ),
    "subastop-design": (
        "Subastop Design System v3 enforcement for all ecosystem UIs.",
        ["ds-enforcer"],
    ),
    "subastop-copy": (
        "VMC Subastas commercial copy: outreach tone-conversion, cascading copy pipeline, and auction-listing descriptions.",
        ["patel-tone-converter", "copy-masterkey", "vmc-listing-copy"],
    ),
}

# Skills whose content depends on non-ASCII glyphs (DS separators, UI glyphs).
# Marketplace channel tolerates UTF-8 (verified: installed ds-enforcer runs with
# these glyphs in Cowork). ASCII-strip would corrupt the spec.
KEEP_UTF8 = {"ds-enforcer"}

# Light sanitization for team copies (personal shorthand -> generic).
SUBS = [(re.compile(r"\bPOPs'"), "the user's"), (re.compile(r"\bPOPs\b"), "the user")]

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "team-toolkit"


def clean(text: str, keep_utf8: bool = False) -> str:
    if not keep_utf8:
        text = re.sub(r"[^\x00-\x7F\n\r\t ]", "", text)  # legacy .plugin channel rejected non-ASCII
    for pat, rep in SUBS:
        text = pat.sub(rep, text)
    return text


def skill_src(name: str) -> Path:
    """Resolve a skill source dir: repo root first, then team-skills/ (team-only sources)."""
    for base in (ROOT, ROOT / "team-skills"):
        if (base / name / "SKILL.md").exists():
            return base / name
    raise SystemExit(f"ERROR: missing SKILL.md for: {name}")


def main():
    all_skills = [s for _, (_, skills) in TEAM_GROUPS.items() for s in skills]
    srcs = {s: skill_src(s) for s in all_skills}  # fails loud on missing

    if OUT.exists():
        try:
            # Clean regen, but NEVER touch OUT/.git -- team-toolkit carries its own
            # independent repo (pushed to subascorp/ai-toolkit). A wholesale rmtree(OUT)
            # destroys that repo and its remote on every refresh, silently downgrading
            # every "git add -A && git commit && git push" run from inside team-toolkit/
            # into a no-op against a missing repo (git then walks up to the SKILL MAKER
            # parent .git instead and commits there under a misleading message).
            for child in OUT.iterdir():
                if child.name == ".git":
                    continue
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink()
        except PermissionError:
            print("WARN: sandbox blocks unlink -- overwriting in place. "
                  "If you REMOVED a skill from TEAM_GROUPS, rebuild natively.")
    else:
        OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ".claude-plugin").mkdir(parents=True, exist_ok=True)

    marketplace = {
        "name": MARKETPLACE_NAME,
        "owner": OWNER,
        "description": MARKETPLACE_DESC,
        "plugins": [],
    }

    for plugin, (desc, skills) in TEAM_GROUPS.items():
        pdir = OUT / "plugins" / plugin
        (pdir / ".claude-plugin").mkdir(parents=True, exist_ok=True)
        (pdir / ".claude-plugin" / "plugin.json").write_text(json.dumps({
            "name": plugin,
            "description": desc,
            "author": {"name": "Subastop"},
        }, indent=2) + "\n")

        for skill in skills:
            src = srcs[skill]
            keep = skill in KEEP_UTF8
            dst = pdir / "skills" / skill
            dst.mkdir(parents=True, exist_ok=True)
            (dst / "SKILL.md").write_text(clean((src / "SKILL.md").read_text(), keep))
            refs = src / "references"
            if refs.is_dir():
                (dst / "references").mkdir(exist_ok=True)
                for f in refs.iterdir():
                    if f.is_file():
                        (dst / "references" / f.name).write_text(clean(f.read_text(), keep))

        marketplace["plugins"].append({
            "name": plugin,
            "source": f"./plugins/{plugin}",
            "description": desc,
        })

    (OUT / ".claude-plugin" / "marketplace.json").write_text(
        json.dumps(marketplace, indent=2) + "\n")

    # README for the team repo (onboarding lives here too).
    onboarding = ROOT / "TEAM_ONBOARDING.md"
    if onboarding.exists():
        (OUT / "README.md").write_text(clean(onboarding.read_text()))

    n = sum(len(s) for _, (_, s) in TEAM_GROUPS.items())
    print(f"OK: {len(TEAM_GROUPS)} plugins, {n} skills -> {OUT}")

    if not (OUT / ".git").exists():
        print(
            "\nWARNING: team-toolkit/.git does not exist -- this directory has no repo of "
            "its own yet. DO NOT run 'git add -A && git commit && git push' from inside "
            "team-toolkit/ right now: with no .git here, git will silently fall through to "
            "the SKILL MAKER parent repo and commit/push there instead (this has already "
            "happened once). Run the one-time setup first:\n"
            "    cd team-toolkit && git init -b main && git add -A "
            "&& git commit -m 'feat: subastop-ai team toolkit v1' "
            "&& gh repo create subascorp/ai-toolkit --private --source . --push"
        )


if __name__ == "__main__":
    main()
