# Team Skills for Kiro

Core skills shared across all team projects. These are universal workflows
that don't depend on any specific project or infrastructure.

## Installation

Copy this directory into your project:

```bash
cp -r team-skills/.kiro /path/to/your-project/
git add .kiro/skills && git commit -m "feat: add team kiro skills"
```

Or use the install script:

```bash
cd /path/to/your-project
/path/to/skill-maker/install-kiro-skills.sh --workspace
```

## What's included

| Category | Skills |
|----------|--------|
| **Reasoning** | critical-thinker, creative-thinker, logic-thinker, loop-breaker, ultrathink |
| **Quality** | self-audit, auditor-general, verify-loop, dependency-audit |
| **Git & Deploy** | git-ops, phased-deploy, meta-no-bare-names |
| **Project Setup** | projectmd-gen, projectmd-optimizer, project-init |
| **Session Mgmt** | continuity-seed, reentry, session-bootstrap |
| **Strategy** | ib, ceo-planner, masterkey, work-retrospective |
| **Delegation** | builder-handoff, offload, toolbox |
| **Analysis** | forensic-auditor, data-analyst |

## How they activate

- **Automatically** — Kiro matches your message against skill descriptions
- **Slash commands** — Type `/critical-thinker`, `/git-ops`, etc.
- **Trigger phrases** — "think with me", "commit this", "challenge this", etc.

## Workspace vs Global

- `.kiro/skills/` (workspace) — available to everyone on this project
- `~/.kiro/skills/` (global) — your personal skills across all projects

Workspace takes priority when names collide.
