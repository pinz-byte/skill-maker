---
name: live-builder-bridge
description: >-
  Governance contract for a LIVE, supervised builder session adapted for Kiro: the supervisor
  agent uses control_bash_process to hold a persistent terminal, sends kickoff commands, reads
  output incrementally via get_process_output, corrects drift, and returns the consolidated
  result to the user. Covers preflight, authority envelope, protocol states
  (PREFLIGHT/RUNNING/NEEDS_HUMAN_SECRET/NEEDS_HUMAN_AUTH/NEEDS_HUMAN_JUDGMENT/VERIFYING/
  BLOCKED/COMPLETE), secret and consent gates, exact-query acceptance with UNEVALUATED as a
  valid verdict, append-only evidence ledger, hard stops and recovery. Trigger on "live builder
  bridge", "connect a builder", "conecta un builder", "supervise the builder", "run this under
  LBB", or whenever one agent is about to drive another agent's terminal in real time. Applies
  to BOTH roles: the supervisor follows it; a builder session receiving an LBB kickoff executes
  under it. NOT offload (fire-and-forget subagent) or builder-handoff (async BUILDER_PROMPT)
  or agent-bridge (Notion inboxes): this is synchronous control of a live terminal.
metadata:
  intent: manage
  platform: kiro
  based-on: live-builder-bridge v1.0 (2026-08-21)
---

# Live Builder Bridge (LBB) -- Kiro Adaptation, v1.0

Based on: Notion "DRAFT SKILL INPUT -- Live Builder Bridge v1.0" (3c3da327-abb1-813d-b303-d7b50036651c),
proven live on LFP-01 2026-08-21. This adaptation maps the LBB contract to Kiro's tool surface.

## Kiro Transport Mapping

The original LBB relies on Codex PTY primitives. Kiro provides equivalent capability through
its background process tools:

| Codex Primitive | Kiro Equivalent | Notes |
|---|---|---|
| `start_process(tty=true)` | `control_bash_process(action="start", command=...)` | Returns `terminalId` as session handle |
| `send_input(session_id, text)` | Not direct -- use new `control_bash_process` start or pipe via the command | See "Input Pattern" below |
| `poll_output(session_id)` | `get_process_output(terminalId, lines=N)` | Incremental reads |
| `list_processes()` | `list_processes()` | Monitor all active builders |
| terminate | `control_bash_process(action="stop", terminalId=...)` | Clean shutdown |

### Input Pattern (Kiro)

Kiro's `control_bash_process` starts a persistent process but does not have a `send_input`
primitive for an already-running process. The Kiro LBB pattern therefore uses:

1. **For Claude Code as builder:** Start the builder with the full kickoff as the command:
   ```
   control_bash_process(action="start", command="claude --resume <id> --print", cwd=<worktree>)
   ```
   Or for a fresh session:
   ```
   control_bash_process(action="start", command="claude -p '<kickoff prompt>'", cwd=<worktree>)
   ```

2. **For script-based builders:** Start the script directly:
   ```
   control_bash_process(action="start", command="bash BUILDER_PROMPT_execute.sh", cwd=<worktree>)
   ```

3. **For sub-agent builders (Kiro-native):** Use `invoke_sub_agent`:
   ```
   invoke_sub_agent(name="general-task-execution", prompt=<contract>)
   ```
   This is fire-and-return (not fire-and-forget like offload) -- the sub-agent returns its
   result to the supervisor within the same session.

### Supervision Loop (Kiro)

```
1. control_bash_process(action="start", ...) -> terminalId
2. LOOP:
   a. get_process_output(terminalId, lines=50)
   b. Compare output vs contract expectations
   c. If drift detected: stop process, correct, restart with amended command
   d. If gate hit: pause, surface to user, await decision
   e. If complete: verify acceptance criteria
3. control_bash_process(action="stop", terminalId=...)
```

## Two transports, never confused

| Transport | What it is | Control of a window |
|---|---|---|
| **Live Builder Bridge** (this skill) | supervisor holds a terminalId to a persistent process, reads output, verifies | YES, synchronous |
| **Agent Bridge / Taskmaster** | async project-to-project mail via Notion inboxes + Focus Queue | NO |
| **Sub-agent (invoke_sub_agent)** | delegated task with result returned to supervisor | YES, but opaque during execution |

Rung: goal-based supervised (rung 2) within one turn; drops to turn-based (rung 1) at every human gate.

## Roles -- which one are you?

- **Supervisor** (Kiro session with `control_bash_process` / `invoke_sub_agent` access): owns
  sections 1-8 below.
- **Builder** (the Claude Code process or sub-agent receiving the kickoff): executes the contract
  literally, reports exact commands/outputs/gate status, never substitutes acceptance queries.
- **User (POPs)**: intention, scope, spend, strategy, human gates, secrets. Never a relay.

## Preflight (declare available only if verified)

| Dependency | Required | Verify (Kiro) | If missing |
|---|---|---|---|
| Claude Code installed on machine | yes | `execute_bash("which claude")` returns path | use builder-handoff (async); never fake |
| Background process capability | yes | `control_bash_process` available in tool list | fall back to `invoke_sub_agent` |
| Real repo + runtime | yes | `execute_bash("git -C <path> status")` succeeds | stop; resolve path first |
| Browser connector | only for web UI | `execute_bash("claude --help")` shows browser flag | `NEEDS_HUMAN_AUTH` |
| Authenticated session | only for dashboards | target page loads | `NEEDS_HUMAN_AUTH` |
| Preinstalled secrets | per task | presence check only, never the value | `NEEDS_HUMAN_SECRET` |

## Authority matrix

| Actor | May | May not |
|---|---|---|
| User (POPs) | set intention, scope, decisions, spend, strategy, human gates; enter secrets | be used as a mechanical relay |
| Supervisor (Kiro) | audit contract; start/supervise builder via terminalId; verify evidence | invent authorization, expose secrets, widen scope |
| Builder (Claude Code / sub-agent) | run commands, edit, test inside contract scope | widen scope, expose secrets, decide a user-reserved gate |

## Protocol states (exactly one at any time)

| State | Meaning | Kiro Action |
|---|---|---|
| `PREFLIGHT` | measuring capabilities | `execute_bash` checks |
| `RUNNING` | builder executing | `get_process_output(terminalId)` polling |
| `NEEDS_HUMAN_SECRET` | credential needed | Surface to user, await input |
| `NEEDS_HUMAN_AUTH` | login/MFA missing | Surface to user, await confirmation |
| `NEEDS_HUMAN_JUDGMENT` | decision needed | Show evidence, await explicit decision |
| `VERIFYING` | checking acceptance | Run verification commands |
| `BLOCKED` | hard stop hit | Report with evidence |
| `COMPLETE` | goal met | Final report, stop process |

`UNEVALUATED` is a valid verdict. Never converted to PASS/FAIL by running a different query.

## Operating protocol (supervisor in Kiro)

### 1. Authority envelope
Record: goal + output artifact; repo/services in scope; permitted mutations; exclusions;
mechanical vs human gates; stop conditions; secret handling.

### 2. Isolate the workspace
```
execute_bash("git -C <worktree> status")
execute_bash("git -C <worktree> log --oneline -5")
```
Measure HEAD, modified files, branch state. Dedicated branch when pre-existing changes exist.

### 3. Intent -> executable contract
Write `BUILDER_PROMPT_*.md` with real commands, no placeholders, exact acceptance criteria,
stop-after-two-failures rule.

### 4. Open the live bridge (Kiro)

**Option A -- Claude Code as builder:**
```
control_bash_process(
  action="start",
  command="claude -p 'Read BUILDER_PROMPT_<slug>.md and execute end to end. Report exact commands and outputs. Stop after two identical failures.'",
  cwd="<worktree>"
)
-> terminalId
```

**Option B -- Sub-agent as builder:**
```
invoke_sub_agent(
  name="general-task-execution",
  prompt="<full contract content>",
  contextFiles=[{path: "BUILDER_PROMPT_<slug>.md"}]
)
```

**Option C -- Script execution:**
```
control_bash_process(
  action="start",
  command="bash ./deploy.sh",
  cwd="<worktree>"
)
-> terminalId
```

### 5. Supervise by evidence

For background processes (Options A & C):
```
LOOP every 10-30s:
  get_process_output(terminalId, lines=50)
  - Compare action vs contract
  - Log evidence
  - If drift: stop + correct + restart
  - If gate: surface to user
  - If done: move to VERIFYING
```

For sub-agents (Option B): result returns directly when complete.

### 6. Human gates

- **Secrets:** Verify SET/MISSING only. User enters value directly in their terminal or
  dashboard. Never ask for or echo the value.
- **Judgment:** Show full evidence and the exact bar first; then user issues explicit decision.
- **External state:** Push, deploy, third-party changes only when contract authorizes them.

### 7. Close and make durable

Before `COMPLETE`:
- Re-run each acceptance gate via `execute_bash`
- Emit PASS / FAIL / UNEVALUATED table
- Fix stale summaries in the same commit
- `control_bash_process(action="stop", terminalId=...)` to clean up
- Commit the artifact of record

### 8. Kiro hooks (optional enforcement layer)

Create a PostToolUse hook to log all `control_bash_process` and `execute_bash` calls during
an LBB run:

```json
{
  "version": "v1",
  "hooks": [{
    "name": "LBB Evidence Logger",
    "trigger": "PostToolUse",
    "matcher": "control_bash_process|execute_bash",
    "action": {
      "type": "command",
      "command": "echo \"$(date -u +%Y-%m-%dT%H:%M:%SZ) | $TOOL_NAME | $TOOL_RESULT\" >> .kiro/lbb-ledger.log"
    }
  }]
}
```

## Hard stop conditions (stop + report)

- Same check fails twice with same error
- A secret appears in stdout/process output
- Worktree has unexpected changes or remote advanced
- Builder proposes out-of-scope mutation
- Gate requires an absent surface
- Attempt to close a gate with a different query/host/mode
- A human decision documented without prior evidence

## Recovery (Kiro)

| Failure | Recovery |
|---|---|
| Process alive, no output | `get_process_output` with more lines; `list_processes` to verify status |
| Process stopped unexpectedly | `list_processes` shows "stopped"; inspect last output; restart from contract + ledger |
| Sub-agent timeout | Result includes partial work; resume with remaining tasks |
| Output truncated | Request more lines or split into smaller commands |
| Remote advanced | Re-measure with `execute_bash("git fetch && git log origin/main..HEAD")` |
| Builder loops | `control_bash_process(action="stop")`, mark `BLOCKED` |

## Kiro vs Codex -- Capability Delta

| Capability | Codex | Kiro | Status |
|---|---|---|---|
| Persistent PTY with send_input | Native | Partial (start + poll, no mid-stream input) | WORKAROUND via restart |
| Incremental output reading | Native | `get_process_output(lines=N)` | EQUIVALENT |
| Process lifecycle | Native | `control_bash_process` start/stop | EQUIVALENT |
| Sub-agent delegation | N/A | `invoke_sub_agent` | KIRO ADVANTAGE |
| Hook-based enforcement | N/A | `.kiro/hooks/` | KIRO ADVANTAGE |
| Browser control | Chrome connector | Not native (use CLI tools) | LIMITATION |

## Known constraints (Kiro-specific)

- **No mid-stream input.** Kiro cannot send input to an already-running process. If the builder
  needs interactive input, the supervisor must stop and restart with amended parameters, or use
  a sub-agent which handles its own I/O.
- **No native browser automation.** Unlike Codex's Chrome connector, Kiro has no browser
  primitive for dashboard verification. Use `web_fetch` for API checks, or surface browser
  verification as a `NEEDS_HUMAN_AUTH` gate.
- **Sub-agent opacity.** When using `invoke_sub_agent`, supervision is opaque during execution.
  You get the result but not incremental evidence. Prefer `control_bash_process` when real-time
  supervision matters.
- **This skill is a contract, not an enforcer.** Enforcement is stronger in Kiro (hooks can
  block tool use via PreToolUse), but the hook in section 8 is optional. Today compliance is
  the supervisor's reading of the output.

## Protocol acceptance (a run complies only if all hold)

1. Builder identified and bound to a persistent handle (terminalId or sub-agent invocation)
2. Every surface had an explicit controller
3. Secrets never passed through chat, logs, process output, or commits
4. Gates ran literally on the correct host or stayed `UNEVALUATED`
5. Human decisions bound to evidence actually shown
6. Final artifact corrected, committed, transported when authorized
7. User intervened only for authority, authentication, secret or judgment
