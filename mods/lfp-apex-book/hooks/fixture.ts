import type { Snapshot } from '../types'

// Shaped like apex-ultra loop.py _build_snapshot output.
export const NOW = Date.parse('2026-10-12T15:00:00Z')

export const SNAPSHOT: Snapshot = {
  generated_at: '2026-10-12T14:58:00+00:00',
  dry_run: false,
  market_state: { banner: 'Mon 10:58 ET - intraday - closes in 302m', phase: 'intraday', is_open: true },
  header: { net_liq: 125430.5, cash_pct: 18.4, day_pl_total: -842.1 },
  positions: [
    { ticker: 'META', position_type: 'LONG', quantity: 1, current_price: 640.1, change_pct: 1.25, asset_type: 'OPTION',
      strike: 635, expiry: '2026-11-20', put_call: 'CALL', stop: 603.69, tp1: 667.36, dist_to_stop_pct: 6.0, dist_to_tp1_pct: -4.1, naked: false, day_pl: 310 },
    { ticker: 'IRDM', position_type: 'LONG', quantity: 200, current_price: 48.2, change_pct: -2.4, stop: null, tp1: null, naked: true, day_pl: -1152.1 },
  ],
  watchlist: [
    { ticker: 'NVDA', alarm_state: 'pending', current_price: 181.3, change_pct: 0.4, dist_from_entry_pct: 4.2, conf: 61, rationale: 'base breakout' },
    { ticker: 'GSAT', alarm_state: 'FIRED', current_price: 'PENDING', change_pct: null, dist_from_entry_pct: 0.3, conf: 70, rationale: 'alarm hit' },
    { ticker: 'AMZN', alarm_state: 'APPROACHING', current_price: 221.5, change_pct: -0.8, dist_from_entry_pct: 1.1, conf: 58 },
  ],
  recent_alerts: [
    { category: 'ALARM', ticker: 'GSAT', price: 9.81, sent_at: '2026-10-12T14:30:00Z' },
    { category: 'VELOCITY', ticker: 'IRDM', price: 48.2, sent_at: '2026-10-12T14:55:00Z', move_pct: -2.4 },
  ],
  naked_flags: [{ ticker: 'IRDM', position_type: 'LONG' }],
}
