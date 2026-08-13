---
name: cc-session-analyzer
description: >-
  Analyzes your Claude Code sessions from the last 30 days and generates a rich HTML report
  covering usage patterns, friction points, workflow strengths, and personalized skill/command
  recommendations. Use this skill whenever the user asks to "analyze my Claude Code sessions",
  "review my workflow", "what skills should I use", "how have I been using Claude Code", "show
  my usage patterns", "generate a session report", "what are my friction points", or any
  request to understand, visualize, or improve their Claude Code usage habits. Also trigger
  when the user asks for a "productivity report", "usage heatmap", or "session analysis".
  Trigger even for casual variations like "how do I use Claude Code?" or "am I using it well?"
  NOT work-retrospective (audits one finished piece of work): this mines 30 days of Claude
  Code sessions into an HTML usage report.
metadata:
  intent: audit
---

# Claude Code Session Analyzer

Generates an HTML intelligence report from your Claude Code session history.

## What it produces

A single self-contained HTML file with:
- **Activity heatmap**  sessions by day/hour over the last 30 days
- **Tool usage breakdown**  which tools dominate your workflow
- **Task distribution**  how you split time across Dev / Fix / Deploy / Research
- **Friction map**  recurring error patterns that slow you down
- **Project activity**  which repos you've been working in
- **Workflow strengths**  patterns where you're operating at peak
- **Personalized recommendations**  skills and slash commands you should adopt based on your actual behavior

---

## Step-by-step workflow

### 1. Run the analyzer script

```bash
python3 "$(dirname "$0")/../scripts/analyze_sessions.py" > /tmp/cc_analysis.json
```

If the user wants a different window (e.g., 60 days):
```bash
CC_ANALYZE_DAYS=60 python3 "$(dirname "$0")/../scripts/analyze_sessions.py" > /tmp/cc_analysis.json
```

If the script errors with "projects dir not found", ask the user to confirm their Claude install path and set `CLAUDE_DIR=/path/to/.claude`.

### 2. Read the JSON output

```bash
cat /tmp/cc_analysis.json
```

Load the full JSON into context. Key fields to consume:
- `meta`  summary stats
- `tool_usage`  ranked list of `[tool_name, count]` pairs
- `task_distribution`  `[category, count]` pairs
- `error_patterns`  `[pattern_label, count]` pairs
- `day_distribution` / `hour_distribution`  activity timing
- `project_distribution`  repos touched
- `daily_sessions`  `[date, count]` pairs for the trend line
- `sessions`  last 50 individual sessions for spot-check
- `skill_affinity`  inferred skill needs from behavior

### 3. Generate the HTML report

Use the data to generate a **single self-contained HTML file** at `/tmp/cc_report.html`.

**Report design requirements:**
- Dark theme preferred (background `#0f1117`, surface `#1a1d27`, accent `#7c6cf8`)
- All charts rendered with pure SVG or vanilla JS  NO external CDN dependencies
- Sections: Executive Summary  Tool Usage  Task Mix  Activity Timing  Friction Points  Projects  Recommendations
- Each section has a short 1-2 sentence **insight** written in POPs' voice (direct, founder-level, no fluff)
- Recommendations section must list specific skill names from the user's installed skills + 23 slash commands

**Executive Summary card must show:**
- Total sessions | Avg session duration | Peak day + hour | Error rate (errors/total tool calls %)

**Chart types to use:**
- Tool usage  horizontal bar chart (SVG)
- Task distribution  donut/pie (SVG)
- Activity by hour  area sparkline or bar (SVG)  
- Daily sessions trend  line sparkline (SVG)
- Error patterns  horizontal bar chart (SVG)

**Recommendations logic:**
Cross-reference `skill_affinity` with the user's installed skills list from their system prompt. Match behavioral signals to skills:

| Behavioral signal | Skill to recommend |
|---|---|
| `bash_tool` heavy + deploy tasks | `phased-deploy` |
| Frontend/React sessions | `frontend-design` |
| web_fetch heavy | `source-scout` |
| Long sessions (>30 min) | `ultrathink` |
| PDF/doc tasks | `pdf` or `docx` |
| Any spreadsheet work | `xlsx` |
| Repeating patterns | `skill-creator` (suggest capturing as a skill) |

Also recommend `/clear` if avg session is >45 min (context bloat risk), and `/compact` if many long sessions detected.

### 4. Deliver the report

```bash
cp /tmp/cc_report.html /path/to/output/cc_session_report.html
```

Present the file to the user with `present_files` if available.

Then give a **3-bullet verbal summary** in the chat:
1. Your #1 workflow strength
2. Your biggest friction pattern
3. The single highest-leverage change you can make today

---

## Edge cases

- **Empty or sparse data**: If fewer than 5 sessions found, note it and generate a minimal report with whatever is available. Suggest the user check their Claude version (`claude --version`)  older versions may use a different storage path.
- **Very long sessions (>120 min)**: Flag as a potential context-overload risk in the report.
- **Single project dominance (>80%)**: Note in the insight that the user may benefit from template/skill extraction for that project's repeated patterns.
- **Error rate >15%**: Escalate this as a "critical friction" finding in the Executive Summary card.

---

## Notes on Claude Code session storage

Sessions live at `~/.claude/projects/{encoded-project-path}/*.jsonl`

Each JSONL line is a message event with:
- `type` / `role`: `user` | `assistant`  
- `message.content`: array of content blocks (text, tool_use, tool_result)
- `timestamp`: ISO string or Unix ms

The `analyze_sessions.py` script handles all parsing. If the path structure changes in future Claude Code versions, update the `PROJECTS_DIR` variable at the top of the script.
