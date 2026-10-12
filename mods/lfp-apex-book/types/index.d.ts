// The slice of apex-ultra's snapshot.json (loop.py _build_snapshot) this mod reads.
// Money and prices are numbers, or the string "PENDING" while Schwab has not answered.
export type Pending = number | 'PENDING' | null

export type MarketState = {
  banner?: string
  phase?: string
  is_open?: boolean
  minutes_to_open?: number | null
  minutes_to_close?: number | null
  error?: string
}

export type Position = {
  ticker: string
  position_type?: string
  quantity: number
  avg_price?: number
  market_value?: number | null
  current_price: Pending
  change_pct?: number | null
  asset_type?: string | null
  strike?: number | null
  expiry?: string | null
  put_call?: string | null
  conf?: number | null
  stop?: number | null
  tp1?: number | null
  dist_to_tp1_pct?: number | null
  dist_to_stop_pct?: number | null
  naked?: boolean
  day_pl?: number | null
}

export type WatchItem = {
  ticker: string
  alarm_state: 'FIRED' | 'APPROACHING' | 'pending'
  alarm_price?: number | null
  current_price: Pending
  change_pct?: number | null
  dist_from_entry_pct?: number | null
  conf?: number | null
  rationale?: string | null
}

export type Alert = {
  category: string
  ticker: string
  price: number
  sent_at: string
  move_pct?: number
}

export type Snapshot = {
  generated_at: string
  dry_run?: boolean
  market_state?: MarketState
  header: { net_liq: Pending; cash_pct: Pending; day_pl_total: number | null }
  positions: Position[]
  watchlist: WatchItem[]
  recent_alerts?: Alert[]
  naked_flags?: { ticker: string; position_type: string }[]
}
