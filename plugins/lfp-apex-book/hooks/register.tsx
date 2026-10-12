import type { EngineInterface, Register } from 'claude-code'

import type { Pending, Position, Snapshot, WatchItem } from '../types'

const PANE = 'apex-book'
const REFRESH_MS = 30_000
const STALE_MS = 10 * 60_000

// Read-only view of the APEX loop's snapshot. Session-scoped: refilled on load.
let snap: Snapshot | undefined
let source: string | undefined
let mtime = 0
let problem: string | undefined

// ---------- formatting (pure, tested) ----------

const group = (n: number) => Math.round(Math.abs(n)).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')

export const money = (v: Pending | undefined) => (typeof v === 'number' ? `${v < 0 ? '-' : ''}$${group(v)}` : 'pendiente')

export const signedMoney = (v: number | null | undefined) =>
  typeof v === 'number' ? `${v > 0 ? '+' : v < 0 ? '-' : ''}$${group(v)}` : '-'

export const pct = (v: number | null | undefined, digits = 2) =>
  typeof v === 'number' ? `${v > 0 ? '+' : ''}${v.toFixed(digits)}%` : '-'

export const price = (v: Pending | undefined) => (typeof v === 'number' ? v.toFixed(2) : 'pend.')

export const tone = (v: number | null | undefined) =>
  typeof v !== 'number' || v === 0 ? undefined : v > 0 ? 'success' : 'error'

export const ago = (iso: string, now: number) => {
  const ms = now - Date.parse(iso)
  if (!Number.isFinite(ms)) return '?'
  const m = Math.max(0, Math.round(ms / 60_000))
  if (m < 1) return 'ahora'
  if (m < 60) return `hace ${m}m`
  const h = Math.round(m / 60)
  return h < 48 ? `hace ${h}h` : `hace ${Math.round(h / 24)}d`
}

export const legLabel = (p: Position) => {
  if (p.strike != null && p.put_call) {
    const side = p.put_call.toUpperCase().startsWith('P') ? 'P' : 'C'
    return `${side} ${p.strike} ${(p.expiry ?? '').slice(5, 10)}`.trim()
  }
  return (p.position_type ?? 'acc').toLowerCase()
}

// Where price sits between stop (left) and TP1 (right): "S[---#------]T".
export const rangeBar = (p: Position, width = 10) => {
  if (typeof p.current_price !== 'number' || p.stop == null || p.tp1 == null || p.tp1 === p.stop) return undefined
  const f = Math.min(1, Math.max(0, (p.current_price - p.stop) / (p.tp1 - p.stop)))
  const at = Math.round(f * (width - 1))
  const track = Array.from({ length: width }, (_, i) => (i === at ? '#' : '-')).join('')

  return { text: `S[${track}]T`, color: f < 0.2 ? 'error' : f > 0.8 ? 'success' : undefined }
}

const ALARM_RANK = { FIRED: 0, APPROACHING: 1, pending: 2 } as const

export const sortWatchlist = (items: WatchItem[]) =>
  [...items].sort(
    (a, b) =>
      ALARM_RANK[a.alarm_state] - ALARM_RANK[b.alarm_state] ||
      Math.abs(a.dist_from_entry_pct ?? 999) - Math.abs(b.dist_from_entry_pct ?? 999),
  )

export const sortPositions = (items: Position[]) =>
  [...items].sort((a, b) => Number(!!b.naked) - Number(!!a.naked) || Math.abs(b.day_pl ?? 0) - Math.abs(a.day_pl ?? 0))

export const isStale = (s: Snapshot, now: number) =>
  !!s.market_state?.is_open && now - Date.parse(s.generated_at) > STALE_MS

export const summarize = (s: Snapshot, now: number) => {
  const naked = s.naked_flags?.length ?? 0
  const parts = [
    `APEX ${s.market_state?.phase ?? '?'}${s.dry_run ? ' DRY' : ''}`,
    `NL ${money(s.header.net_liq)}`,
    `dia ${signedMoney(s.header.day_pl_total)}`,
    `${s.positions.length} pos`,
  ]
  if (naked) parts.push(`${naked} sin stop`)
  parts.push(`${isStale(s, now) ? 'DESACTUALIZADO ' : ''}${ago(s.generated_at, now)}`)

  return parts.join(' | ')
}

// ---------- reading the snapshot ----------

const snapshotPaths = async ($: EngineInterface) => {
  const cwd = await $.session.cwd()
  const home = (await $.env.get('HOME')) ?? ''

  return [`${cwd}/snapshot.json`, `${home}/Documents/Claude/Projects/apex-ultra/snapshot.json`, '/tmp/apex-ultra-snapshot.json']
}

const refresh = async ($: EngineInterface) => {
  let best: { path: string; mtimeMs: number } | undefined
  for (const path of await snapshotPaths($)) {
    try {
      const st = await $.fs.stat(path)
      if (st.kind === 'file' && (!best || st.mtimeMs > best.mtimeMs)) best = { path, mtimeMs: st.mtimeMs }
    } catch {
      // not there: try the next place the loop may write it
    }
  }

  if (!best) {
    snap = undefined
    problem = 'No encuentro snapshot.json. Abre la sesion en la carpeta apex-ultra de M1.'
  } else if (best.path !== source || best.mtimeMs !== mtime) {
    try {
      snap = JSON.parse((await $.fs.read(best.path)) as string) as Snapshot
      source = best.path
      mtime = best.mtimeMs
      problem = undefined
    } catch (err) {
      problem = `snapshot.json ilegible: ${err instanceof Error ? err.message : String(err)}`
    }
  }

  // Outside apex-ultra there is nothing to say: keep the status line clean.
  $.ui.status(snap ? summarize(snap, await $.clock.now()) : undefined)
  $.ui.invalidate('ui.render')
}

// ---------- hooks ----------

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'apex', description: 'APEX book: positions, watchlist and market signals' })
    await refresh($)
    $.clock.every(REFRESH_MS, () => refresh($))

    return next(e)
  })

  on('command.run', { command: 'apex' }, async $ => {
    await refresh($)
    const opened = await $.ui.open({ id: PANE, title: 'APEX Book' })
    if (opened.isPlaced) return { text: snap ? 'APEX Book abierto.' : `APEX Book abierto. ${problem ?? ''}` }

    return { text: snap ? summarize(snap, await $.clock.now()) : (problem ?? 'Sin datos.') }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const now = await $.clock.now()
    const isWide = (e.viewport?.columns ?? 100) >= 78

    if (!snap) {
      return (
        <Box flexDirection="column" gap={1} paddingX={1}>
          <Text bold>APEX BOOK</Text>
          <Text color="warning">{problem ?? 'Leyendo snapshot...'}</Text>
        </Box>
      )
    }

    const s = snap
    const stale = isStale(s, now)
    const naked = s.naked_flags ?? []

    const cell = (key: string, width: number, text: string, opts: { color?: string; bold?: boolean; dim?: boolean; right?: boolean } = {}) => (
      <Box key={key} width={width} justifyContent={opts.right ? 'flex-end' : 'flex-start'} paddingRight={1}>
        <Text color={opts.color} bold={opts.bold} dimColor={opts.dim} wrap="truncate">
          {text}
        </Text>
      </Box>
    )
    const heading = (title: string, count?: number) => (
      <Box key={`h-${title}`} justifyContent="space-between">
        <Text bold>{title}</Text>
        {count !== undefined && <Text dimColor>{count}</Text>}
      </Box>
    )
    const tile = (key: string, label: string, value: string, color?: string) => (
      <Box key={key} flexDirection="column" borderStyle="round" borderColor={color ?? 'subtle'} paddingX={1} flexGrow={1}>
        <Text dimColor>{label}</Text>
        <Text bold color={color}>
          {value}
        </Text>
      </Box>
    )

    return (
      <Box flexDirection="column" gap={1} paddingX={1}>
        <Box justifyContent="space-between">
          <Text bold>
            APEX BOOK{s.dry_run ? '  ' : ''}
            {s.dry_run && (
              <Text color="warning" inverse>
                {' DRY RUN '}
              </Text>
            )}
          </Text>
          <Text color={stale ? 'warning' : undefined} dimColor={!stale}>
            {stale ? 'DESACTUALIZADO  ' : ''}
            {ago(s.generated_at, now)}
          </Text>
        </Box>
        {s.market_state?.banner && <Text dimColor>{s.market_state.banner}</Text>}
        {s.positions.length > 0 && (
          <Box flexWrap="wrap" columnGap={3}>
            {sortPositions(s.positions).map((p, i) => (
              <Text key={`tape-${p.ticker}-${i}`}>
                <Text bold>{p.ticker}</Text> <Text color={tone(p.change_pct)}>{pct(p.change_pct)}</Text>
              </Text>
            ))}
          </Box>
        )}

        <Box gap={1}>
          {tile('nl', 'NET LIQ', money(s.header.net_liq))}
          {tile('cash', 'CASH', typeof s.header.cash_pct === 'number' ? `${s.header.cash_pct.toFixed(1)}%` : 'pendiente')}
          {tile('pl', 'P/L DEL DIA', signedMoney(s.header.day_pl_total), tone(s.header.day_pl_total))}
          {naked.length > 0 && tile('naked', 'SIN STOP', String(naked.length), 'warning')}
        </Box>

        <Box flexDirection="column">
          {heading('POSICIONES', s.positions.length)}
          <Box>
            {cell('h1', 9, 'TICKER', { dim: true })}
            {cell('h2', 13, 'TIPO', { dim: true })}
            {cell('h3', 7, 'CANT', { dim: true, right: true })}
            {cell('h4', 10, 'PRECIO', { dim: true, right: true })}
            {cell('h5', 9, 'HOY', { dim: true, right: true })}
            {cell('h6', 11, 'P/L DIA', { dim: true, right: true })}
            {isWide && cell('h7', 10, 'A STOP', { dim: true, right: true })}
            {isWide && cell('h8', 16, 'STOP > TP1', { dim: true, right: true })}
          </Box>
          {s.positions.length === 0 && <Text dimColor>Sin posiciones.</Text>}
          {sortPositions(s.positions).map((p, i) => (
            <Box key={`p-${p.ticker}-${i}`}>
              {cell('t', 9, `${p.naked ? '! ' : ''}${p.ticker}`, { bold: true, color: p.naked ? 'warning' : undefined })}
              {cell('l', 13, legLabel(p), { dim: true })}
              {cell('q', 7, String(p.quantity), { right: true })}
              {cell('c', 10, price(p.current_price), { right: true })}
              {cell('d', 9, pct(p.change_pct), { right: true, color: tone(p.change_pct) })}
              {cell('pl', 11, signedMoney(p.day_pl), { right: true, color: tone(p.day_pl) })}
              {isWide && cell('s', 10, p.naked ? 'sin stop' : pct(p.dist_to_stop_pct, 1), { right: true, color: p.naked ? 'warning' : undefined, dim: !p.naked })}
              {isWide && cell('tp', 16, rangeBar(p)?.text ?? '-', { right: true, color: rangeBar(p)?.color, dim: !rangeBar(p) })}
            </Box>
          ))}
        </Box>

        <Box flexDirection="column">
          {heading('WATCHLIST', s.watchlist.length)}
          {s.watchlist.length === 0 && <Text dimColor>Watchlist vacia.</Text>}
          {sortWatchlist(s.watchlist).map((w, i) => (
            <Box key={`w-${w.ticker}-${i}`}>
              <Box width={10} paddingRight={1}>
                {w.alarm_state === 'FIRED' ? (
                  <Text color="error" inverse bold>
                    {' DISPARO '}
                  </Text>
                ) : w.alarm_state === 'APPROACHING' ? (
                  <Text color="warning" inverse>
                    {' CERCA '}
                  </Text>
                ) : (
                  <Text dimColor>espera</Text>
                )}
              </Box>
              {cell('t', 8, w.ticker, { bold: true })}
              {cell('c', 10, price(w.current_price), { right: true })}
              {cell('d', 9, pct(w.change_pct), { right: true, color: tone(w.change_pct) })}
              {cell('e', 12, `${pct(w.dist_from_entry_pct, 1)} ent.`, { right: true, dim: true })}
              {cell('f', 9, w.conf != null ? `conf ${w.conf}` : '', { right: true, dim: true })}
              {isWide && w.rationale && cell('r', 30, w.rationale, { dim: true })}
            </Box>
          ))}
        </Box>

        <Box flexDirection="column">
          {heading('SENALES', s.recent_alerts?.length ?? 0)}
          {(s.recent_alerts ?? []).length === 0 && <Text dimColor>Sin alertas recientes.</Text>}
          {[...(s.recent_alerts ?? [])].reverse().map((a, i) => (
            <Box key={`a-${i}`}>
              {cell('w', 10, ago(a.sent_at, now), { dim: true })}
              {cell('k', 14, a.category, { color: a.category === 'VELOCITY' ? 'warning' : 'suggestion', bold: true })}
              {cell('t', 8, a.ticker, { bold: true })}
              {cell('p', 10, a.price.toFixed(2), { right: true })}
              {a.move_pct != null && cell('m', 9, pct(a.move_pct), { right: true, color: tone(a.move_pct) })}
            </Box>
          ))}
        </Box>

        <Text dimColor wrap="truncate">
          {source} | se refresca cada 30 s
        </Text>
      </Box>
    )
  })
}
