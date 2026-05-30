---
name: toolbox
description: >
  The skill router. Call it when you have a task but are not sure which skill fits, or want
  the agent to survey the whole skill set and choose deliberately instead of firing on
  whatever keyword matched. It builds a LIVE inventory of installed and deployed skills,
  classifies the task, recommends the right skill (or composition of skills, in order), and
  then invokes them. Use whenever the user says "toolbox", "open the toolbox", "what's in
  the box", "what skill should I use", "which skill fits this", "what do you have for this",
  "pick the right skill", "route this", "what tools do I have for X", "catalog the skills",
  or "what can you do here". Also fire when a task is multi-faceted and several skills might
  compose, or when the user is unsure what is available. This is a meta-skill: it does not
  do the work itself, it chooses and chains the skills that do. For "what skills do I have"
  as a pure list, the native skill list is enough; toolbox is for deciding what to USE.
---

# Toolbox - The Skill Router

You are choosing tools for a job. The point of this skill is deliberate selection: survey
what is actually available, map the task to the best-fit skill or composition, then invoke.
It does not replace any skill - it routes to them.

Do NOT fire skills reflexively because a keyword matched. Route on purpose: the right skill,
or the right ordered set of skills, for the task in hand.

## Step 1 - Build the live inventory (never trust a hardcoded list)

Two surfaces matter and they differ:

- **Installed here** - the skills active in THIS workspace. This is the in-context skill
  list the environment loads. These are callable right now.
- **Deployed but maybe not installed** - skills that exist in the ecosystem but are not
  active in this workspace. Enumerate from the iCloud Plugins folder:

```bash
for f in "$HOME/Library/Mobile Documents/com~apple~CloudDocs/Claude/Plugins"/*.skill; do
  [ -f "$f" ] || continue
  n=$(basename "$f" .skill)
  d=$(python3 -c "import zipfile,re; c=zipfile.ZipFile('$f').read('$n/SKILL.md').decode(); m=re.search(r'description:\s*>(.*?)\n---',c,re.S); print(' '.join(m.group(1).split())[:160] if m else '')" 2>/dev/null)
  echo "- $n: $d"
done
```

If a skill you want to recommend is deployed but not installed here, say so and route the
user through [[workspace-plugin-audit]] to install it - do not assume it is callable.

## Step 2 - Orient with the category map

The live scan gives names and descriptions; this map gives the RELATIONSHIPS the descriptions
do not - which skills compose, which are alternatives, which are meta. Treat it as orientation,
not as the inventory. Rebuild the inventory live every call; this map changes slowly and may
lag (last reviewed 2026-05-29).

- **Oversight roundtable (thinking)** - `critical-thinker` (attack an idea), `creative-thinker`
  (generate value-oriented options), `logic-thinker` (expose the reasoning chain),
  `loop-breaker` (escape a recurring failure). Pick by intent: scrutiny vs invention vs
  validity vs stuck-loop. They can convene together.
- **Project structuring** - `ib` (intention -> architecture), `masterkey` (creative refinement
  process), `brief-bridge` (IB output -> Stitch design prompt).
- **Memory and continuity** - `continuity-seed` (cross-session handoff), `compact` (compress
  context mid-session), `data-capsule` (save one discrete fact), `reentry` (reconstruct state
  at session start), `wake`/`memory-bridge` (Symbios memory corpus).
- **Cross-project comms** - `agent-bridge` (Notion inbox messaging between projects).
- **Build / deploy discipline** - `phased-deploy` (generic), `carmatch-deploy` (CarMatch-
  specific), `git-ops` (git lifecycle), `project-init` + `projectmd-gen` (scaffold a repo),
  `dependency-audit` (pre-build cost/viability gate), `apex-builder-gate` (APEX pre-flight),
  `self-audit` (pre-delivery review), `work-retrospective` (post-work learning capture).
- **Ops / infra remediation** - `herald-config-doctor` (fix recurring Herald config drift),
  `machine-bridge` (sandbox->machine command/path handoff), `gcp-iam-resolver` (GCP IAM
  permission errors), `workspace-plugin-audit` (per-workspace install gap).
- **Research / finance** - `deep-research` (multi-source briefing), `source-scout` (new data
  sources for the extractor), `bigdata-com:*` (company/sector/earnings/macro analysis),
  `financial-research-analyst`.
- **Output formats** - `docx`, `pptx`, `xlsx`, `pdf` (build only AFTER content/research is done).
- **Meta / governance** - `meta-no-bare-names` (file hygiene gate), `skill-creator` (author
  skills), `skill-miner` (discover skill ideas from sessions), `toolbox` (this), `schedule`
  (scheduled tasks), `setup-cowork`, `cc-session-analyzer`.

## Step 3 - Route the task

1. State the task in one line and its underlying goal.
2. Match it to a category, then to the best-fit skill. Prefer the most specific skill that
   fits (e.g. `carmatch-deploy` over generic `phased-deploy` when in CarMatch).
3. Decide if it is single-skill or a composition. Many real tasks chain:
   - "structure then design" -> `ib` -> `brief-bridge`
   - "build then ship" -> author/edit -> `self-audit` -> `phased-deploy` -> `work-retrospective`
   - "research then deliver" -> `deep-research` -> `docx`/`pptx`/`xlsx`
   - "stuck again" -> `loop-breaker`; "pressure-test the plan" -> `critical-thinker`
   - "fix recurring infra noise" -> `herald-config-doctor` and/or `gcp-iam-resolver`, hand off
     via `machine-bridge`
4. Name your pick, the order, and WHY each is in the chain. One line of justification per skill.

## Step 4 - Invoke (or hand off)

Invoke the chosen skill(s) in order. If a chosen skill is not installed in this workspace,
stop and route through [[workspace-plugin-audit]] first. If the task needs a skill that does
not exist, say so and offer `skill-creator`.

## Optional - Materialize the catalog

If the user wants a browsable artifact ("write the catalog", "give me a catalog file"),
emit `CATALOG.md` in SKILL MAKER from the live Step 1 scan grouped by the Step 2 categories,
with a dated header. Regenerate it from the live scan each time - do not let it fossilize.

## Principles

- **Live scan beats memory.** What is installed changes per workspace and over time. Enumerate
  every call; the embedded map is orientation, not truth.
- **Route, do not reflex.** A keyword match is a candidate, not a decision. Choose the best fit
  and justify it.
- **Compose by default.** Most non-trivial tasks want a chain (think -> do -> audit -> ship),
  not one skill.
- **Specific over generic.** Prefer the project-specific skill when one exists.
- **Installed != deployed.** A recommendation the user cannot run is a dead end - check
  installation, pair with [[workspace-plugin-audit]].

## Edge Cases

- **Nothing fits:** say so plainly and offer `skill-creator` to build the missing one, or
  `skill-miner` to confirm the gap is real and recurring before building.
- **Several skills fit equally:** present the 2-3 candidates with the trade-off in one line
  each and let the user pick - this is the one time a short menu beats a single pick.
- **iCloud folder unreachable (sandbox without the mount):** fall back to the in-context skill
  list for "installed here" and note that the deployed-but-not-installed set could not be read.
