#!/usr/bin/env python3
"""regroup-rescued.py -- promote the 31 rescued account-only skills into the marketplace.

Run once, natively, from the SKILL MAKER repo root:

    python3 regroup-rescued.py

What it does:
  1. Moves rescued/<skill>/ -> <skill>/  (build-marketplace.py reads top-level
     <skill>/SKILL.md as the edit source of truth).
  2. Rewrites the GROUPS block in build-marketplace.py with the new grouping,
     adding three bundles: lfp-product, lfp-symbios, lfp-labs.
  3. Leaves rescued/skill-creator alone -- it ships with Anthropic's LICENSE.txt
     and is not ours to republish.

Idempotent: re-running after a partial move is safe. Backs up build-marketplace.py
to build-marketplace.py.bak before touching it.
"""
import os
import re
import shutil
import sys

ROOT = os.path.abspath(os.path.dirname(__file__))
RESCUED = os.path.join(ROOT, "rescued")
BUILD = os.path.join(ROOT, "build-marketplace.py")

DO_NOT_PROMOTE = {"skill-creator"}

NEW_MEMBERS = {
    "lfp-apex":     ["apex-health", "council", "council-run"],
    "lfp-copy":     ["copy-deck", "voice-bench-gate"],
    "lfp-thinkers": ["masterkey", "ib", "ultrathink"],
    "lfp-core":     ["builder-handoff", "projectmd-gen", "project-init",
                     "cc-session-analyzer", "work-retrospective",
                     "forensic-auditor", "data-analyst"],
}

NEW_BUNDLES = {
    "lfp-product": (
        "Subastop / VMC / CarMatch product line -- build, deploy, design-system and "
        "pre-ship gates. Scope to product projects only.",
        ["brief-bridge", "dashboard-section", "ds-enforcer", "factory-gate",
         "carmatch-deploy", "phased-deploy", "source-scout", "pre-deliver",
         "dependency-audit"],
    ),
    "lfp-symbios": (
        "Symbios personal-OS layer -- session consciousness, capture and weekly "
        "continuity. Scope to Symbios and personal projects.",
        ["wake", "investigator", "morning", "data-capsule", "cowork-friday-handoff"],
    ),
    "lfp-labs": (
        "Narrow single-project instruments -- voice architecture and production "
        "series artwork. Install only where the project lives.",
        ["amorata-voice-system", "apu-series-generator"],
    ),
}

EXISTING = {
    "lfp-thinkers": (
        "Oversight roundtable + router: critical, creative, logic, loop-breaker, "
        "ceo-planner, toolbox -- plus the Master Key creative process, the Intention "
        "Builder framework and extended-reasoning escalation.",
        ["critical-thinker", "creative-thinker", "logic-thinker", "loop-breaker",
         "ceo-planner", "toolbox"],
    ),
    "lfp-core": (
        "Core ops/build/meta/comms/QA skills for every working project.",
        ["agent-bridge", "inbox-triage", "git-ops", "machine-bridge", "project-migrate",
         "self-audit", "reentry", "continuity-seed", "session-bootstrap", "soul-builder",
         "arise", "time-boundary", "session-rules", "meta-no-bare-names", "skill-miner",
         "workspace-plugin-audit", "gcp-iam-resolver", "herald-config-doctor",
         "projectmd-auditor", "projectmd-optimizer", "offload", "auditor-general",
         "audit-codex-build", "codex-audit-handoff", "builder-identity-check",
         "qa-mirror", "qa-sequence", "pwa-verify", "carmatch-intel", "disk-doctor",
         "notebooklm-bridge", "pm", "space-steward", "inpositive-language",
         "project-handover", "skillmaker-publish", "verify-loop"],
    ),
    "lfp-apex": (
        "APEX live-money trading council and runtime health -- scope to trading "
        "projects only.",
        ["apex-builder-gate", "apex-ultra-council", "council-call", "council-debate",
         "council-global"],
    ),
    "lfp-copy": (
        "Tone and copy skills for VMC Subastas commercial content -- outreach "
        "sequences, marketplace listings, page copy and source grounding.",
        ["patel-tone-converter", "copy-masterkey", "vmc-listing-copy"],
    ),
    "lfp-design": (
        "Personal-project design-system enforcement (non-Subastop) -- e-ink brand "
        "tokens and component drift checks.",
        ["astrodiary-ds-enforcer"],
    ),
}


def build_groups():
    groups = {}
    for name, (desc, skills) in EXISTING.items():
        groups[name] = (desc, list(skills) + NEW_MEMBERS.get(name, []))
    for name, (desc, skills) in NEW_BUNDLES.items():
        groups[name] = (desc, list(skills))
    return groups


def render(groups):
    out = ["GROUPS = {"]
    for name, (desc, skills) in groups.items():
        out.append(f'    "{name}": (')
        out.append(f'        "{desc}",')
        line, buf = "        [", []
        for s in skills:
            item = f'"{s}", '
            if len(line) + len(item) > 96:
                buf.append(line.rstrip())
                line = "         " + item
            else:
                line += item
        buf.append(line.rstrip().rstrip(",") + "],")
        out.extend(buf)
        out.append("    ),")
    out.append("}")
    return "\n".join(out)


def main():
    if not os.path.isfile(BUILD):
        sys.exit("ERROR: run this from the SKILL MAKER repo root (build-marketplace.py not found).")

    groups = build_groups()
    promoting = [s for _, (_, sk) in NEW_BUNDLES.items() for s in sk]
    promoting += [s for sk in NEW_MEMBERS.values() for s in sk]

    moved, already, missing = [], [], []
    for name in sorted(promoting):
        src, dst = os.path.join(RESCUED, name), os.path.join(ROOT, name)
        if os.path.isdir(dst):
            already.append(name)
        elif os.path.isdir(src):
            shutil.move(src, dst)
            moved.append(name)
        else:
            missing.append(name)

    if missing:
        sys.exit(f"ERROR: not found in rescued/ nor at root: {missing}\nNothing was written to build-marketplace.py.")

    for name, (_, skills) in groups.items():
        for s in skills:
            if not os.path.isfile(os.path.join(ROOT, s, "SKILL.md")):
                sys.exit(f"ERROR: {name} lists '{s}' but {s}/SKILL.md does not exist. Aborting before build edit.")

    src = open(BUILD, encoding="utf-8").read()
    if not re.search(r"^GROUPS = \{", src, re.M):
        sys.exit("ERROR: could not locate the GROUPS block in build-marketplace.py.")
    shutil.copy2(BUILD, BUILD + ".bak")
    new = re.sub(r"^GROUPS = \{.*?^\}", render(groups), src, count=1, flags=re.M | re.S)
    open(BUILD, "w", encoding="utf-8").write(new)

    total = sum(len(sk) for _, sk in groups.values())
    print(f"moved {len(moved)} skills out of rescued/  (already at root: {len(already)})")
    print(f"GROUPS rewritten: {len(groups)} plugins, {total} skills  (backup: build-marketplace.py.bak)")
    for name, (_, sk) in groups.items():
        print(f"  {len(sk):>3}  {name}")
    left = sorted(os.listdir(RESCUED)) if os.path.isdir(RESCUED) else []
    print(f"\nleft in rescued/ on purpose: {left or 'nothing'}")
    print("  (skill-creator ships Anthropic's LICENSE.txt -- not ours to republish)")
    print("\nNEXT:\n  python3 skill-intent-audit.py assign --apply\n  ./publish.sh")


if __name__ == "__main__":
    main()
