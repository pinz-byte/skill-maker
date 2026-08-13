---
name: project-init
description: >
  Scaffolds a .claude/ directory for any project — pre-commit hooks, agent config, and coding rules — auto-detected from the project's stack and patterns. Triggers on: "init project", "set up .claude", "scaffold .claude", "add hooks and rules", "project-init", "configure this project", "add pre-commit hooks", "create agent config", or when starting a new repo. Also trigger on "I want every project to have this setup" or "make this codebase smarter". Complementary to projectmd-gen — use both together.
---

# project-init — Project-Aware .claude Scaffolding

You're about to generate a `.claude/` directory that makes Claude Code work like it already knows
this project. The goal: every future session starts informed, every commit is guarded, and every
convention is enforced — not remembered.

## What You Generate

```
.claude/
├── hooks/
│   └── pre-commit.sh       # Stack-appropriate checks that block bad commits
├── agents/
│   └── <project>-builder.md  # Persistent project context for Builder/agent sessions
└── rules/
    ├── <concern-1>.md       # One rule file per detected concern area
    ├── <concern-2>.md
    └── ...
```

## How It Works: Three Phases

### Phase 1: Detect (silent)

Scan the project directory and build a detection profile. Do all of this before showing anything
to the user — they don't need to see the scan process, just the results.

**Stack detection** — check for these markers (in order of confidence):

| Marker | Stack |
|--------|-------|
| `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile` | Python |
| `package.json` | Node.js (check for `next`, `react`, `vue`, `svelte` in deps for framework) |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `pom.xml`, `build.gradle` | Java/Kotlin |
| `Gemfile` | Ruby |
| `composer.json` | PHP |
| `Dockerfile`, `docker-compose.yml` | Container (note alongside primary stack) |

**Entry point detection** — find the main files:
- Python: look for `main.py`, `app.py`, `manage.py`, `*_bot.py`, `server.py`, or scripts in `pyproject.toml`
- Node: check `package.json` → `main`, `scripts.start`, `scripts.dev`
- Go: find `main.go` or `cmd/` directory
- Look for `Procfile`, `railway.json`, `vercel.json`, `netlify.toml` for deploy targets

**External service detection** — scan for:
- Environment variable references (`os.environ`, `process.env`, `os.Getenv`)
- Import patterns (`pinecone`, `openai`, `anthropic`, `stripe`, `supabase`, `firebase`, `redis`, `boto3`, `notion`)
- Config files (`.env.example`, `config.py`, `config.ts`)
- Database connection strings or ORM setup

**Convention detection** — sample existing code for:
- Error handling patterns (try/except vs if/err, centralized vs inline)
- Logging setup (logger name, format)
- Test framework (`pytest`, `jest`, `mocha`, `go test`)
- Code organization (monorepo vs single package, `lib/` vs `src/` vs `pkg/`)
- Existing linting config (`.eslintrc`, `ruff.toml`, `.flake8`, `golangci-lint`)

**File map** — list the top-level structure and key subdirectories. For `lib/` or `src/` dirs,
go one level deeper. Don't recurse into `node_modules`, `__pycache__`, `.git`, `venv`, or `dist`.

### Phase 2: Present Summary

Show the user what you found in a compact summary. This is their chance to correct anything before
you generate. Format it clearly:

```
## Detection Summary

**Stack:** Python 3.x (Telegram bot)
**Entry point:** second_self_bot.py
**Deploy target:** Railway (auto-deploy on main)
**External services:** Pinecone, Notion API, OpenAI, Anthropic, Telegram Bot API
**Test command:** python3 -c "import second_self_bot" (no test suite detected)
**Linting:** None configured
**Key directories:** lib/ (9 modules), config.py

**Will generate:**
- hooks/pre-commit.sh — import check across all lib modules + secret scan
- agents/<project>-builder.md — file map, conventions, deploy flow
- rules/error-handling.md — non-fatal external service pattern
- rules/api-conventions.md — Pinecone/Notion usage patterns
- rules/deploy.md — branch → verify → merge → deploy

Proceed? (or tell me what to adjust)
```

Wait for the user to confirm before generating.

### Phase 3: Generate

Create each file with content adapted to what was detected. Here's how to tailor each component:

#### Hooks: `pre-commit.sh`

The hook script adapts to the detected stack. Always include:
- **Secret scan** (universal) — grep staged files for API key patterns
- **Stack-specific checks:**

| Stack | Checks |
|-------|--------|
| Python | `python3 -c "import <entry_point>"` for main module + each detected lib module. `python3 -m py_compile` on changed `.py` files. |
| Node.js | `npm run lint` if lint script exists. `npx tsc --noEmit` if TypeScript. `npm run build` if build script exists. |
| Go | `go vet ./...` + `go build ./...` |
| Rust | `cargo check` |
| Java/Kotlin | `./gradlew build` or `mvn compile` |
| Ruby | `bundle exec rubocop` if rubocop in Gemfile |

Always make the hook executable and start with `#!/bin/bash` and `set -e`.
Always print clear pass/fail messages with context about what failed.

#### Agent Config: `<project>-builder.md`

Name the agent after the project (from directory name or package name). Include:

1. **One-line project description** — what this thing is and does
2. **Runtime + deploy info** — language version, deploy target, trigger
3. **File map** — table of key files with one-line purpose descriptions. Go deeper for lib/src dirs.
4. **External services** — list each detected service with how it's used
5. **Conventions** — patterns detected from code (error handling, naming, structure)
6. **Verification command** — the one thing to run before committing
7. **Deploy workflow** — step by step
8. **"Never" list** — anti-patterns specific to this project (derived from error handling patterns,
   service usage, and deploy setup)

The agent config should read like a briefing that gets a new contributor (or a new Claude session)
productive in 30 seconds. No filler, no theory — just the patterns and facts needed to work here.

#### Rules: One File Per Concern

Generate rule files based on what's detected. Common patterns:

| Detection | Rule File | Content |
|-----------|-----------|---------|
| External API clients (Pinecone, Stripe, etc.) | `api-conventions.md` | Connection reuse, error handling, retry patterns |
| Database (Notion, Postgres, Redis) | `data-access.md` | Query patterns, ID formats, schema refs |
| HTTP handlers (Express, FastAPI, Flask) | `api-handlers.md` | Route structure, middleware, response format |
| Bot commands (Telegram, Discord, Slack) | `bot-handlers.md` | Command handler template, auth check, response limits |
| Deploy config (Railway, Vercel, Docker) | `deploy.md` | Branch strategy, verify steps, rollback |
| Test setup (pytest, jest) | `testing.md` | Test patterns, fixtures, coverage expectations |
| Error handling patterns | `error-handling.md` | Fatal vs non-fatal, logging, recovery patterns |

Don't generate rule files for concerns that aren't present. A Node.js API doesn't need
`bot-handlers.md`. A Telegram bot doesn't need `api-handlers.md`. Keep it relevant.

Each rule file should be concise — under 60 lines. Format:
- Section header for each pattern
- Brief explanation of why (one line)
- Code example showing the correct pattern
- Anti-pattern to avoid (if relevant)

#### After Generation

Once all files are created:

1. Show a tree of what was generated
2. Provide the exact commands to commit it:
   ```bash
   git add .claude/
   git commit -m "Add .claude config: hooks, agent, rules — auto-generated by claude-init"
   ```
3. Mention that `projectmd-gen` can be run alongside this for the complementary `CLAUDE.md` context file

## Edge Cases

**No clear stack detected:** Ask the user what the primary language/framework is. Generate with
minimal assumptions — basic secret scan hook, generic agent config with file listing, no rules
(since there's nothing confident to codify).

**Monorepo with multiple stacks:** Generate one `.claude/` at the root. Agent config lists all
sub-projects. Hooks run checks for each detected stack on files in that stack's directory.
Rules are scoped by directory (e.g., `rules/backend-api.md`, `rules/frontend-app.md`).

**Existing `.claude/` directory:** Show what exists, ask if the user wants to merge (add missing
files) or replace. Never silently overwrite.

**.claude/rules/ could be huge:** Cap at 5 rule files. Prioritize by: error handling > API conventions > deploy > data access > everything else. If more concerns exist, mention them but don't generate — the user can ask for specific ones later.

## What This Skill Does NOT Do

- It does not generate `CLAUDE.md` — that's `projectmd-gen`'s job
- It does not configure CI/CD — it generates local hooks only
- It does not install dependencies or modify project code
- It does not run the hooks — it creates them for future use
