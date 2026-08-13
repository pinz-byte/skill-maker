---
name: apex-health
description: >-
  Read-only health sweep of the APEX Ultra runtime (M1) -- probes every surface
  (loop.py/snapshot, Schwab token, council_loop board, signal plans, scanner via watchdog,
  sa_news_feed, MASTERS, HERMES/Slack) and returns a verdict table with evidence, using a
  failure-signature library so known incidents are recognized in seconds. Use whenever the
  user says "system health check", "sweep the system", "is apex alive", "is everything
  running", "apex status", "estado del sistema", "is the loop up", "why is the board stale",
  "why no alerts today", "snapshot looks frozen", or asks ANY is-it-up / why-is-it-quiet /
  why-is-this-stale question about APEX Ultra, even casually mid-session. Also fire
  proactively before relaying a council verdict when data freshness is uncertain. Diagnoses
  and prescribes only -- never fixes (builder-handoff) and never deliberates (council-run).
  NOT carmatch-intel: that reads the CarMatch extractor pipeline.
metadata:
  intent: observe
---

# APEX Health — read-only runtime sweep

One skill, one question: **what is actually alive right now, and what is only pretending to be?** APEX has failed twice by looking dead while alive (token starvation) and alive while dead (stale board served silently). This skill exists so the diagnosis takes ~5 tool calls, not a 2-hour re-derivation.

## Stance (non-negotiable)

- **Read-only, verdict-only.** Never restart, reload, re-auth, or edit anything. Repair is a prescription; M1-side repair becomes a `builder-handoff` prompt. The moment a health check fixes things, it's a builder grading its own homework.
- **Sandbox is not M1 truth.** File mtimes through the mount are evidence; `launchctl` state is not reachable from here. Say UNVERIFIABLE where it applies — never guess it into a verdict. (The symbios `launchd_health` MCP tool covers `com.symbios.*` / `com.lattice.*` / `com.taskmaster.*` ONLY — it does NOT see `com.apex.*`.)
- **Worst finding wins.** 8 healthy surfaces + 1 dead core = system DOWN, not "mostly fine".
- **Timestamps:** the device_bash VM prints UTC. Lima = UTC−5 year-round; ET = UTC−4 (EDT) / UTC−5 (EST). Internal `generated_at` fields are UTC. Beware ET wall-times written with a `Z` suffix in older logs/notes — three clocks coexist in this repo.

## Output contract

Lead with the banner, always: `Lima HH:MM | ET HH:MM | Market OPEN/CLOSED | Snapshot age: X`.
Then a verdict table (HEALTHY / DEGRADED / DOWN / STALE / UNKNOWN per surface, worst-first), one evidence line per verdict, a prescribed repair path for anything non-healthy, and a **Not verified** list. For a formal saved report (`AUDIT_*.md` with evidence chains), run this sweep under the `auditor-general` output skeleton — apex-health supplies the probes and signatures; auditor-general supplies the report format.

## The surface map

Repo mount: the apex-ultra folder under the session's device mounts. Probe with ONE compound `device_bash` call where possible — mtimes before parses, one sample before full reads.

| # | Surface | Cheapest probe | Healthy looks like |
|---|---------|----------------|--------------------|
| 1 | **loop.py** (com.apex.ultra.loop, 5-min StartInterval) | `snapshot.json` mtime AND internal `generated_at` (they must match) | < ~10 min old during the active window (04:00–20:00 ET weekdays) |
| 2 | **Schwab token** | No direct probe from sandbox. Infer from #1 + #4 | Fresh snapshot with priced positions ⇒ token fine |
| 3 | **council_loop** (com.apex.masters.council_loop, calendar: premarket + EOD) | `masters_dayplans/council_tiers_<today>.json` exists + `logs/council_loop.stdout.log` mtime + fresh `logs/council_transcripts/` entries | Board by ~08:10 ET on trading days, WITH transcripts |
| 4 | **Signal plans** | Active-plan count (loop's "plans=N", plan feed file mtime) | N > 0 and feed < 30h old. N=1–2 across 50+ tickers = working but scarce (chronic condition, not an outage) |
| 5 | **scanner + plan_generator** | Slack: search "APEX feed watchdog" last 48h | Watchdog SILENT = feeds fresh. A STALE alert names the feed, its last write, and the launchctl label to check |
| 6 | **sa_news_feed** (launchd 06:50) | `pilot/reset/news_feed_<today>.json` exists | ~280 KB (full ~868-headline merge). ~5–8 KB = degraded partial feed |
| 7 | **MASTERS** (paper, fires 07:45/09:00/12:00/16:15 Lima) | `masters_books/*.json` mtimes vs the last scheduled fire | Books touched at the most recent fire time |
| 8 | **HERMES / Slack interface** | Slack: hermes digest (once/day) + tier-transition alerts | Digest present on trading days. Silence is only meaningful if #3 is healthy — HERMES is downstream |
| 9 | **launchd ground truth** (com.apex.*) | NONE from sandbox | Always list as "Not verified — needs `launchctl list \| grep apex` on M1" unless a builder session just reported it |

Adjacent, same host (report separately, out of APEX scope): symbios `launchd_health` MCP for the Symbios/LATTICE fleet.

## Failure-signature library

Match signatures BEFORE hypothesizing. Each of these cost real hours once; recognizing them is the point of this skill.

1. **Frozen snapshot + all feeds stale + processes "look dead" → Schwab token expiry (invalid_grant). RANK THIS FIRST.** The loop FATALs on `get_positions` BEFORE the snapshot write, so mtime freezes while the process ticks every 5 min. Scanner/plan_generator keep running with priceless quotes. Burned 2026-06-23 and again 2026-08-03 (the 08-03 audit wrongly called three agents DOWN). Discriminator (M1 only): `grep invalid_grant ~/Library/Logs/APEXUltra/loop.log`. Repair: re-auth via `schwab_oauth.py` in a LIVE terminal on M1 — relaying the OAuth callback URL through chat fails (sub-minute code TTL); self-heals next tick, no restarts.
2. **launchctl exit 78 + stdout frozen + stderr empty → spawn-layer failure, not a Python crash.** The process dies at the log-redirect open() before execve: script exits 0 by hand (Terminal's FDA masks it), zero bytes ever land in stdout/stderr. Killed the council board for 11 days (07-23→08-03). CONFIRMED mechanism (controlled /bin/date-agent test, ae3b267): a `com.apple.macl` xattr on the specific StandardOutPath file — per-FILE MAC label, leaves NO TCC.db rows, no prompts; a fresh file in the same directory spawns fine. When you hit this signature: `launchctl print` for the redirect paths, then `xattr -l` on those exact files. Standing rule: launchd logs go in `~/Library/Logs/APEXUltra/`, never ~/Documents. Related landmine (structural, from the same forensics): TCC grants pin exact Cellar-versioned interpreter paths — after any `brew upgrade python`, every LaunchAgent invoking `/opt/homebrew/bin/python*` that touches ~/Documents is silently orphaned from its grant; run this sweep after brew python bumps.
3. **Board exists but no transcripts and stdout untouched → unaccounted writer.** Usually a manual run by POPs (ask him first). A board with full votes but no `council_transcripts/` entries did not come from the calendar agent.
4. **`show_council.py` serves stale boards silently.** Always check its age line; > 1 trading day = artifact, say so before relaying any verdict.
5. **`bootstrap` fails with Input/output error on a valid plist → label is `disabled` in launchd's per-user DB.** Discriminator: `launchctl print-disabled`. Repair: `launchctl enable gui/$UID/<label>` then bootstrap. (Symbios agents, 2026-08-03.)
6. **Whole-board 0 GO / all PASS → usually plan scarcity, not a parser fault.** With 0–2 active plans, rr_term starves and discovery scores flatten. Check #4 before suspecting the Council.
7. **Board deliberated while token was dead = artifact.** A board generated during starvation used stale reference prices; treat its entries/stops as suspect and note the generation time vs the re-auth time.
8. **`day_pl` / `currentDayProfitLoss` figures are untrustworthy** (corrupt per-position field; no holiday gate). Never report day-P/L as a health signal.
9. **Frozen `[FATAL]`s in old log tails are not live incidents.** `stat` before `tail` — append-only logs preserve dead errors forever.

## Repair routing

- Anything requiring M1 (launchctl, ~/Library logs, OAuth, kickstart) → write a `BUILDER_PROMPT_*.md` via `builder-handoff`; never hand POPs a raw runbook.
- Formal audit deliverable → `auditor-general` skeleton, saved as `AUDIT_APEX-ULTRA_<date>.md` in the repo root, committed audit-file-only.
- Fresh verdict on a ticker → `council-run`. Displaying the board → `/council`. Neither is a health function.
- After any incident diagnosis or resolution: update project memory (the incident file + MEMORY.md index) in the same session — the signature library above only stays sharp if new burns are recorded.

## Verification of your own sweep

Close every sweep by naming the weakest verdict — the one resting on the thinnest evidence (usually an mtime-only inference or an unverifiable launchctl state). A health check that can't say what it couldn't see invites the exact false-confidence failure this skill was born from.
