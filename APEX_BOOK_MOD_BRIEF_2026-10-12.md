# Brief: APEX book mod (Claude Code mod, run on M1)

Paste this into a Claude Code session running ON M1 (LFP-M1, MacBook Air) in the
apex-ultra repo. Written 2026-10-12 from an M2 session that could not reach M1's disk.

## Goal

A Claude Code mod (plugin of function hooks) that shows the live APEX book in a pane:
full positions, the watchlist, and market signals. Plus a one-line status entry.
Read-only: it reads a file the APEX loop already writes. No Schwab, no orders, no network.

Load the `plugin-authoring` skill first; it says where to write the mod and how hot reload works.

## Data source (verify on M1 first)

`loop.py` writes `snapshot.json` every cycle: `SNAPSHOT_PATH = <repo>/snapshot.json`.
`dashboard.py` hard-codes `/Users/usuario/Documents/Claude/Projects/apex-ultra/snapshot.json`.
Confirm which path is live on M1 (`ls -la` both; newest mtime wins) before coding.
`loop.py` docstring also mentions `/tmp/apex-ultra-snapshot.json`; check it too.

Snapshot shape (from `loop.py` `_build_snapshot`, ~line 1093-1210):

- `generated_at` ISO ts; `dry_run` bool (show a DRY RUN badge when true)
- `market_state`: `banner` (one-line, render as-is), `phase` (premarket|intraday|eod|closed),
  `is_open`, `minutes_to_open`, `minutes_to_close`, `market_status`, `next_open_iso`;
  may instead be `{ error, now_utc }` when degraded
- `header`: `net_liq`, `cash_pct`, `day_pl_total` (numbers, or the string `"PENDING"`)
- `positions[]`: `ticker`, `position_type`, `quantity`, `avg_price`, `market_value`,
  `current_price` (number or `"PENDING"`), `price_source_ts`, `change_pct`, `asset_type`,
  `strike`, `expiry`, `put_call`, `conf`, `thesis_tag`, `stop`, `tp1`,
  `dist_to_tp1_pct`, `dist_to_stop_pct`, `naked` (bool), `day_pl`, `spcx` (bool)
- `watchlist[]`: `ticker`, `alarm_state` (FIRED|APPROACHING|pending), `alarm_price`,
  `current_price`, `price_source_ts`, `change_pct`, `dist_from_entry_pct`, `conf`,
  `rationale` (<=80 chars), `spcx`
- `recent_alerts[]` (last 10): `category`, `ticker`, `price`, `sent_at`, VELOCITY adds `move_pct`
- `naked_flags[]`: `ticker`, `position_type` (held with no stop: show prominently)

Council verdicts are separate: newest `masters_dayplans/council_tiers_<date>.json`
(`generated_at`, `tickers[]` with `ticker`, `tier` GO|NEAR-MISS|PASS, `score`, `action`).

## Design

- `/apex` command opens pane `apex-book`, titled "APEX Book".
- Pane sections, top to bottom:
  1. Market: `market_state.banner`, snapshot age, DRY RUN badge if `dry_run`.
  2. Header: net liq, cash %, day P/L total.
  3. NAKED warning row if `naked_flags` is non-empty.
  4. Positions: ticker, type/option leg, qty, price, change %, day P/L, dist to stop / TP1.
  5. Watchlist: FIRED first, then APPROACHING, then pending; price, change %, conf.
  6. Signals: `recent_alerts`, newest first.
- Status line (always on): `APEX <phase> | NL <net_liq> | day <day_pl_total> | <n> naked | snap <age>`.
- Refresh with `$.clock.every(30_000, ...)`; keep the parsed snapshot in `$.state` so the
  pane redraws on write. Flag STALE when the snapshot is older than ~10 min during market hours
  (dashboard.py uses the same idea).
- Treat `"PENDING"` as a value to display, not a number.

## Lessons from the M2 build (council-status + roundtable mods, Claude Code 2.1.293)

- `claude plugin validate` rejects the `read`/`update`/`atom` state helpers even in the bundled
  pane example. Use `$.state.get(ref)` / `$.state.set(ref, value)` directly, with
  `const ref = { plugin: '<mod>', key: '<key>' } as const`.
- `$.ui.open` returns `{ isPlaced, reason }`. Always report it: the desktop app may not place panes
  (seen: `/roundtable` said "opened" while nothing showed). If it is not placed, fall back to
  printing a compact text summary as the `/apex` command output.
- Mobile has no `Input` element: `'Input' in els ? els.Input : undefined`.
- `$.prompt.submit` cannot be called from a `command.run` hook (deadlock: hook skipped) and refuses
  text starting with `/`.
- Test through the engine, not just pure functions: `$.command.run({ command, args })` in a
  `*.test.ts`, mocking `ui.open` with `on('ui.open', () => ({ value: { isPlaced: false, reason } }))`
  and the clock with `mock.clock(on)`. Pure-function tests passed while the command was broken.
- Read files with `$.fs.list` / `$.fs.read` (4 MiB cap); pick newest dated files by NAME, not mtime.
- Type-check with the tsconfig from the header of the skill's `types/claude-code.d.ts`.

## Done when

- `claude plugin validate`, `claude plugin test`, `tsc` all clean.
- `/apex` on M1 shows the live snapshot (or prints why the pane is not placed, plus the text summary).
- The status line updates within 30 s of the loop writing a new snapshot.
