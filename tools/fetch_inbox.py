#!/usr/bin/env python3
"""fetch_inbox.py — TASKMASTER session-open hook.

Fetches the SKILL MAKER Notion inbox, extracts active [DISPATCH] messages,
and writes DISPATCH_INBOX.md to the project root so CLAUDE.md loads it
as context automatically at session start.

Run by the Claude Code session-start hook — not manually.
"""
from __future__ import annotations
import argparse, os, re, sys
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / "secrets" / "apex-desk-v3" / ".env")

NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "")
SKILL_MAKER_INBOX_ID = "360da327-abb1-8196-b98d-cfc86bbe0ec6"  # 📬 SKILL MAKER — Inbox
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "DISPATCH_INBOX.md"


def fetch_blocks(page_id: str) -> list[dict]:
    import urllib.request, json
    url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
    })
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read())["results"]


def extract_text(block: dict) -> str:
    btype = block.get("type", "")
    return "".join(r.get("plain_text","") for r in block.get(btype,{}).get("rich_text",[]))


def parse_dispatches(blocks: list[dict]) -> list[dict]:
    dispatches, current = [], None
    for block in blocks:
        text = extract_text(block).strip()
        if "[DISPATCH]" in text:
            if current: dispatches.append(current)
            current = {"raw_lines": ["[DISPATCH]"]}
        elif current is not None:
            if text.startswith("---") and current["raw_lines"]:
                dispatches.append(current); current = None
            elif text:
                current["raw_lines"].append(text)
    if current and current["raw_lines"]: dispatches.append(current)
    parsed = []
    for d in dispatches:
        fields: dict[str, str] = {}
        for line in d["raw_lines"]:
            for key in ("Task ID","Task","SLA","Expects"):
                if re.match(rf"\*?\*?{re.escape(key)}:\*?\*?", line):
                    fields[key] = re.sub(rf"^\*?\*?{re.escape(key)}:\*?\*?\s*","",line).strip()
        if fields.get("Task ID"):
            fields["_raw"] = "\n".join(d["raw_lines"]); parsed.append(fields)
    return parsed


def build_md(dispatches: list[dict], fetched_at: str) -> str:
    lines = ["# DISPATCH_INBOX — SKILL MAKER",
             f"> Auto-generated: {fetched_at}", ""]
    if not dispatches:
        lines += ["## No active dispatches.", "", "Continue with normal session."]
        return "\n".join(lines)
    lines += [f"## {len(dispatches)} active dispatch(es) — ACK each before any other work","",
              "Send [ACK] to Symbios — Inbox: https://www.notion.so/360da327abb18115bf58fcaec470ec53","","---",""]
    for d in dispatches:
        lines += [f"### {d.get('Task ID','?')}",
                  f"**Task:** {d.get('Task','—')}",
                  f"**SLA:** {d.get('SLA','—')}",
                  f"**Expects:** {d.get('Expects','—')}","","---",""]
    lines += ["**At session close:** send [REPORT] to Symbios — Inbox.",
              "Protocol: https://www.notion.so/372da327abb181d3aa9cf0cd6061dc4e"]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if not NOTION_API_KEY:
        msg = "# DISPATCH_INBOX\n\n> Skipped — NOTION_API_KEY not set.\n"
        if not args.dry_run: OUTPUT_PATH.write_text(msg)
        else: print(msg)
        return 0
    try:
        blocks = fetch_blocks(SKILL_MAKER_INBOX_ID)
        dispatches = parse_dispatches(blocks)
        md = build_md(dispatches, fetched_at)
    except Exception as e:
        msg = f"# DISPATCH_INBOX\n\n> Fetch failed: {e}\n> Check inbox manually.\n"
        if not args.dry_run: OUTPUT_PATH.write_text(msg)
        else: print(msg)
        return 0
    if args.dry_run: print(md); return 0
    OUTPUT_PATH.write_text(md)
    print(f"[fetch_inbox] {len(dispatches)} dispatch(es) → DISPATCH_INBOX.md")
    return 0

if __name__ == "__main__": sys.exit(main())
