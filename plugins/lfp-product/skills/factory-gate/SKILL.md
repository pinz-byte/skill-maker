---
name: factory-gate
description: >
  Mandatory pre-build gate for the Pagebuilder Factory line. Loads the stage gates
  from PAGEBUILDER_FACTORY_OS.md and BLOCKS any build, runtime, or deploy work until
  the relevant gate passes. Use whenever starting work on any site in pagebuilder,
  before writing build files (S6), before wiring runtime (S7), before deploy (S9), or
  any session in the pagebuilder project. Trigger on: "factory gate", "run the gate",
  "build site", "start [brand] build", "is [site] ready to build", "admit to line",
  "pre-flight", "gate this site", "S0", "dependency contract", or any time a site is
  about to advance a stage. Fires every time, no exceptions  past sites stalled at the
  last mile or shipped wrong data because nothing blocked them.
  NOT phased-deploy (runs the commit-build-deploy sequence): this BLOCKS Pagebuilder Factory work until the stage gates pass.
metadata:
  intent: build
---

# Factory Gate  Pagebuilder pre-build enforcement

The model is not an enforcement mechanism. This gate is. It runs BEFORE a site is allowed
to advance a stage, runs the deterministic checks, and refuses to proceed until they pass.
Same posture as `apex-builder-gate`: it fires every time, no exceptions.

## When it fires
- Before **S0  admit**: a site cannot enter the line.
- Before **S6 Build**: no `index.html`/component is written.
- Before **S7 Runtime**: no function is wired.
- Before **S9 Deploy**: nothing goes live.

If you are about to write build/runtime/deploy output for a pagebuilder site and this gate
has not run this session, that is the failure this skill exists to prevent. Run it first.

## Procedure
1. **Identify the site and the stage** it is trying to advance to.
2. **Run the gate for that stage** (below). Each is a hard PASS/FAIL.
3. **On any FAIL  STOP.** Report the failing gate and the specific finding. Do not write the
   stage output. Do not "fix it inline and continue"  the point is that the block is visible.
4. **On all PASS  proceed**, and log the pass in the site's `VERIFY.md`.

## The gates

| Gate | Stage | Check | Enforcement | Status |
|------|-------|-------|-------------|--------|
| `gate_s0_contract` | S0 | `DEPENDENCY_CONTRACT.md` exists and every row = GREEN (no `?`, AMBER, RED) | script  TODO | scaffold |
| `gate_s6_quality` | S6 | canonical present  JSON-LD valid  single h1  skip link  LCP `fetchpriority="high"` (htmlvalidate + schema validator + axe) | script  TODO | scaffold |
| `gate_s8_datatruth` | S8 | every stat/currency number traced to a confirmed source | `_factory/gates/gate_s8_datatruth.py` | **runnable** |
| `gate_lead` | S7 | POST to each form persists (no silent `submitLead()` stub) | test  TODO | scaffold |
| `gate_wip` | S0 | in-flight site count  cap (23) | script  TODO | scaffold |
| `gate_s9_deploy` | S9 | VERIFY = PASS  canonical == target domain  rollback noted | script  TODO | scaffold |

### Runnable today
```bash
# S8 DATA-TRUTH  flags any unsourced public-facing number. Exit 1 = BLOCK.
python3 _factory/gates/gate_s8_datatruth.py subastop/
```

### TODOs (deferred, written down  not vague intentions)
- `gate_s0_contract.py`  parse the contract table, fail on any non-GREEN row.
- `gate_s6_quality.py`  wrap `html-validate` + `validator.schema.org` + `axe-core`; needs node in CI.
- `gate_lead`  a POST test per form; needs the runtime endpoint to exist first (S7).
- `gate_wip.py`  count sites in in-flight stages on `PORTFOLIO_BOARD.md`.
- `gate_s9_deploy.sh`  pre-deploy hook; needs `git init` + chosen deploy target.

## Install note
This file is a deliverable. It is NOT live until installed into the skill system
(Settings  Capabilities / your plugin-deploy flow). Activating it in a session does not
happen by writing the file  it must be registered like any other skill.

## Principle
Strength matches failure cost. Catastrophic + code-checkable (wrong number, lost lead,
wrong domain, red-dependency admit)  a script that BLOCKS. Judgment (is the brief good,
does the hero feel like the brand) stays with `forensic-auditor` / `ds-enforcer`  code
can't check those, so a gate must not pretend to.
