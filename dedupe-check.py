#!/usr/bin/env python3
"""dedupe-check.py -- detects the same skill name installed from more than one source.

Why this exists: for ~5 months SKILL MAKER shipped every skill twice -- once as a standalone
.skill upload and once inside a grouped plugin -- and nothing noticed. 36 names were duplicated,
3 of them triplicated, before a human spotted it in the slash-command picker.

The DELETION is manual (the Cowork account stores have no API and no CLI verb, and the Claude
desktop app is not a computer-use target). The DETECTION is what must never be manual again.

Run inside any Cowork session. Exits 1 if duplicates are found, so it can gate a build or a job.
"""
import os
import sys
import collections

CANDIDATE_ROOTS = [
    os.path.expanduser("~/.claude"),
    "/root/.claude",
]


def collect():
    loc = collections.defaultdict(list)
    seen_root = None
    for root in CANDIDATE_ROOTS:
        sk = os.path.join(root, "skills", "synced")
        pl = os.path.join(root, "plugins", "synced")
        if not (os.path.isdir(sk) or os.path.isdir(pl)):
            continue
        seen_root = root
        if os.path.isdir(sk):
            for n in sorted(os.listdir(sk)):
                if os.path.isdir(os.path.join(sk, n)):
                    loc[n].append("standalone-skill")
        if os.path.isdir(pl):
            for plug in sorted(os.listdir(pl)):
                sd = os.path.join(pl, plug, "skills")
                if os.path.isdir(sd):
                    for n in sorted(os.listdir(sd)):
                        if os.path.isdir(os.path.join(sd, n)):
                            loc[n].append("plugin:" + plug)
        break
    return loc, seen_root


def main():
    loc, root = collect()
    if root is None:
        print("dedupe-check: no synced store found -- run this inside a Cowork session.")
        return 0
    dups = {k: v for k, v in loc.items() if len(v) > 1}
    print("dedupe-check  root=%s  names=%d  duplicated=%d" % (root, len(loc), len(dups)))
    if not dups:
        print("PASS  every skill name resolves to exactly one source.")
        return 0
    print("")
    for k in sorted(dups, key=lambda x: (-len(dups[x]), x)):
        print("  %dx  %-26s %s" % (len(dups[k]), k, ", ".join(dups[k])))
    print("")
    print("FAIL  %d duplicated name(s)." % len(dups))
    print("  Standalone copies: delete in Customize -> Skills.")
    print("  Single-skill plugins: uninstall in Customize -> Plugins.")
    print("  Keep the GROUPED plugin copy (lfp-core / lfp-thinkers / lfp-copy / lfp-apex).")
    print("  This is per-ACCOUNT, not per-machine -- do it once.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
