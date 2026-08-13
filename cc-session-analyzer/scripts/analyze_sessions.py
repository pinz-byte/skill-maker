#!/usr/bin/env python3
"""
Claude Code Session Analyzer
Scans ~/.claude/projects/ JSONL files for the last N days,
extracts usage patterns, and outputs structured JSON for HTML report generation.
"""

import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta, timezone
from collections import defaultdict, Counter

# ── Config ────────────────────────────────────────────────────────────────────
DAYS = int(os.environ.get("CC_ANALYZE_DAYS", "30"))
CLAUDE_DIR = Path(os.environ.get("CLAUDE_DIR", Path.home() / ".claude"))
PROJECTS_DIR = CLAUDE_DIR / "projects"

# ── Helpers ───────────────────────────────────────────────────────────────────
def parse_jsonl_safe(path: Path) -> list[dict]:
    events = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    except Exception:
        pass
    return events

def extract_tool_name(event: dict) -> str | None:
    """Pull tool name from a tool_use content block."""
    content = event.get("message", {}).get("content", [])
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                return block.get("name")
    return None

def extract_tool_names(event: dict) -> list[str]:
    """Pull ALL tool names from a single event."""
    tools = []
    content = event.get("message", {}).get("content", [])
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                name = block.get("name")
                if name:
                    tools.append(name)
    return tools

def extract_tool_error(event: dict) -> str | None:
    """Check if a tool_result block contains an error."""
    content = event.get("message", {}).get("content", [])
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_result":
                if block.get("is_error"):
                    inner = block.get("content", [])
                    if isinstance(inner, list):
                        for ib in inner:
                            if ib.get("type") == "text":
                                return ib.get("text", "")[:200]
                    elif isinstance(inner, str):
                        return inner[:200]
    return None

def classify_task(events: list[dict]) -> str:
    """Heuristic: guess the primary task category for a session."""
    all_text = " ".join(
        block.get("text", "")
        for e in events
        for block in (e.get("message", {}).get("content", []) if isinstance(e.get("message", {}).get("content"), list) else [])
        if isinstance(block, dict) and block.get("type") == "text"
    ).lower()
    
    tools_used = [t for e in events for t in extract_tool_names(e)]
    tool_str = " ".join(tools_used).lower()

    if any(w in all_text for w in ["deploy", "firebase", "build", "ci/cd", "npm run"]):
        return "Deploy / Release"
    if any(w in all_text for w in ["bug", "fix", "error", "traceback", "exception", "broken"]):
        return "Bug Fix"
    if any(w in all_text for w in ["refactor", "clean", "migrate", "rename"]):
        return "Refactor"
    if any(w in all_text for w in ["feat", "feature", "implement", "add", "create component"]):
        return "Feature Dev"
    if any(w in all_text for w in ["research", "explain", "how does", "what is", "analyze"]):
        return "Research / Learning"
    if "bash_tool" in tool_str and "str_replace" not in tool_str:
        return "Scripting / Ops"
    if any(w in all_text for w in ["pdf", "report", "doc", "spreadsheet", "xlsx"]):
        return "Document / Output"
    if any(w in all_text for w in ["react", "component", "tsx", "jsx", "css", "tailwind"]):
        return "Frontend Dev"
    if any(w in all_text for w in ["api", "endpoint", "nestjs", "backend", "firestore"]):
        return "Backend Dev"
    return "General Dev"

def parse_ts(ts) -> datetime | None:
    if not ts:
        return None
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts / 1000 if ts > 1e10 else ts, tz=timezone.utc)
    if isinstance(ts, str):
        for fmt in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z"]:
            try:
                return datetime.strptime(ts, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                pass
    return None

# ── Main scan ─────────────────────────────────────────────────────────────────
def main():
    if not PROJECTS_DIR.exists():
        print(json.dumps({"error": f"Claude projects dir not found: {PROJECTS_DIR}"}))
        sys.exit(1)

    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=DAYS)
    
    sessions = []
    
    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        project_name = project_dir.name
        for jsonl_file in project_dir.glob("*.jsonl"):
            # Quick age check by file mtime first
            mtime = datetime.fromtimestamp(jsonl_file.stat().st_mtime, tz=timezone.utc)
            if mtime < cutoff:
                continue
            
            events = parse_jsonl_safe(jsonl_file)
            if not events:
                continue
            
            # Determine session timestamps
            timestamps = [parse_ts(e.get("timestamp") or e.get("ts")) for e in events]
            timestamps = [t for t in timestamps if t]
            
            session_start = min(timestamps) if timestamps else mtime
            session_end = max(timestamps) if timestamps else mtime
            
            if session_start < cutoff:
                continue
            
            duration_min = max(1, int((session_end - session_start).total_seconds() / 60))
            
            # Tool usage
            tool_counts = Counter()
            for e in events:
                for t in extract_tool_names(e):
                    tool_counts[t] += 1
            
            # Errors
            errors = []
            for e in events:
                err = extract_tool_error(e)
                if err:
                    errors.append(err)
            
            # Message count
            human_msgs = sum(1 for e in events if e.get("type") == "user" or e.get("role") == "user")
            assistant_msgs = sum(1 for e in events if e.get("type") == "assistant" or e.get("role") == "assistant")
            
            # Task category
            task_cat = classify_task(events)
            
            sessions.append({
                "session_id": jsonl_file.stem,
                "project": project_name,
                "start": session_start.isoformat(),
                "day": session_start.strftime("%a"),
                "hour": session_start.hour,
                "date": session_start.strftime("%Y-%m-%d"),
                "duration_min": duration_min,
                "tool_counts": dict(tool_counts),
                "error_count": len(errors),
                "errors_sample": errors[:3],
                "human_msgs": human_msgs,
                "assistant_msgs": assistant_msgs,
                "task_category": task_cat,
                "total_events": len(events),
            })
    
    if not sessions:
        print(json.dumps({"error": "No sessions found in the last 30 days. Check ~/.claude/projects/"}))
        sys.exit(0)
    
    # ── Aggregate stats ────────────────────────────────────────────────────────
    all_tools = Counter()
    for s in sessions:
        for t, c in s["tool_counts"].items():
            all_tools[t] += c
    
    task_dist = Counter(s["task_category"] for s in sessions)
    day_dist = Counter(s["day"] for s in sessions)
    hour_dist = Counter(s["hour"] for s in sessions)
    project_dist = Counter(s["project"] for s in sessions)
    
    total_errors = sum(s["error_count"] for s in sessions)
    avg_duration = sum(s["duration_min"] for s in sessions) / len(sessions)
    
    # Error patterns
    all_errors = []
    for s in sessions:
        all_errors.extend(s["errors_sample"])
    
    error_patterns = Counter()
    for err in all_errors:
        if "permission denied" in err.lower():
            error_patterns["Permission Denied"] += 1
        elif "command not found" in err.lower() or "not found" in err.lower():
            error_patterns["Command Not Found"] += 1
        elif "syntax" in err.lower() or "parse" in err.lower():
            error_patterns["Syntax / Parse Error"] += 1
        elif "timeout" in err.lower():
            error_patterns["Timeout"] += 1
        elif "no such file" in err.lower():
            error_patterns["Missing File"] += 1
        elif "module" in err.lower() or "import" in err.lower():
            error_patterns["Import / Module Error"] += 1
        else:
            error_patterns["Other"] += 1
    
    # Sessions over time (daily)
    daily_sessions = Counter(s["date"] for s in sessions)
    
    # Peak productivity window
    peak_hour = max(hour_dist, key=hour_dist.get) if hour_dist else 0
    peak_day = max(day_dist, key=day_dist.get) if day_dist else "Mon"
    
    # Skill usage inference
    skill_triggers = Counter()
    for s in sessions:
        tools = set(s["tool_counts"].keys())
        if "bash_tool" in tools and s["duration_min"] > 5:
            skill_triggers["phased-deploy"] += 1
        if s["task_category"] in ("Feature Dev", "Frontend Dev", "Backend Dev"):
            skill_triggers["frontend-design"] += 1
        if "web_fetch" in tools or "web_search" in tools:
            skill_triggers["source-scout"] += 1
    
    output = {
        "meta": {
            "days_analyzed": DAYS,
            "total_sessions": len(sessions),
            "total_tool_calls": sum(all_tools.values()),
            "total_errors": total_errors,
            "avg_duration_min": round(avg_duration, 1),
            "peak_hour": peak_hour,
            "peak_day": peak_day,
            "generated_at": datetime.now().isoformat(),
        },
        "tool_usage": all_tools.most_common(15),
        "task_distribution": task_dist.most_common(),
        "day_distribution": day_dist.most_common(),
        "hour_distribution": sorted(hour_dist.items()),
        "project_distribution": project_dist.most_common(10),
        "error_patterns": error_patterns.most_common(),
        "daily_sessions": sorted(daily_sessions.items()),
        "sessions": sorted(sessions, key=lambda x: x["start"], reverse=True)[:50],
        "skill_affinity": skill_triggers.most_common(),
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
