import type { EngineInterface, Register, RenderChildren } from 'claude-code'

import type { Pending, Position, Snapshot, WatchItem } from '../types'

const PANE = 'apex-book'
const REFRESH_MS = 30_000
const STALE_MS = 10 * 60_000
const APEX_SKILLS = ['council', 'council-run', 'council-call', 'council-debate', 'council-global', 'apex-health', 'apex-ultra-council', 'apex-builder-gate']

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

  // Using an APEX skill (council, council-run, apex-health, ...) raises the desk with a fresh read.
  on('tool.call', { tool: 'Skill' }, async ($, e, next) => {
    const name = e.skill.split(':').pop() ?? e.skill
    if (APEX_SKILLS.includes(name)) {
      await refresh($)
      if (snap) await $.ui.open({ id: PANE, title: 'APEX Book' }).catch(() => undefined)
    }

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

    // Desk palette (thinkorswim / Binance dark): fixed, so the desk reads the same in any app theme.
    const C = {
      bg: '#000000',
      card: '#1c1c1e',
      label: '#8e8e93',
      text: '#ffffff',
      up: '#30d158',
      down: '#ff453a',
      amber: '#ff9f0a',
      gold: '#f0b90b',
      chip: '#2b2f36',
      alert: '#5c1010',
    }
    const dir = (v: number | null | undefined) => (typeof v !== 'number' || v === 0 ? C.text : v > 0 ? C.up : C.down)

    if (!snap) {
      return (
        <Box flexDirection="column" gap={1} paddingX={1} paddingY={1} backgroundColor={C.bg}>
          <Text bold color={C.text}>
            APEX BOOK
          </Text>
          <Box backgroundColor={C.alert} paddingX={1}>
            <Text color={C.text}>{problem ?? 'Leyendo snapshot...'}</Text>
          </Box>
        </Box>
      )
    }

    const s = snap
    const stale = isStale(s, now)
    const naked = s.naked_flags ?? []

    // One table cell: a main line and an optional second line beneath it, thinkorswim style.
    const cell = (
      key: string,
      width: number,
      main: string,
      opts: { color?: string; bold?: boolean; right?: boolean; sub?: string; subColor?: string } = {},
    ) => (
      <Box key={key} width={width} flexDirection="column" alignItems={opts.right ? 'flex-end' : 'flex-start'} paddingRight={1}>
        <Text color={opts.color ?? C.text} bold={opts.bold} wrap="truncate">
          {main}
        </Text>
        {opts.sub !== undefined && (
          <Text color={opts.subColor ?? C.label} wrap="truncate">
            {opts.sub}
          </Text>
        )}
      </Box>
    )
    const label = (key: string, width: number, text: string, right?: boolean) => (
      <Box key={key} width={width} justifyContent={right ? 'flex-end' : 'flex-start'} paddingRight={1}>
        <Text color={C.label}>{text}</Text>
      </Box>
    )
    const card = (key: string, title: string, count: number, body: RenderChildren) => (
      <Box key={key} flexDirection="column" backgroundColor={C.card} paddingX={1} paddingY={1}>
        <Box justifyContent="space-between">
          <Text bold color={C.text}>
            {title}
          </Text>
          <Text color={C.label}>{count}</Text>
        </Box>
        {body}
      </Box>
    )
    const kpi = (key: string, name: string, value: string, color?: string) => (
      <Box key={key} flexDirection="column" backgroundColor={C.card} paddingX={1} flexGrow={1}>
        <Text color={C.label}>{name}</Text>
        <Text bold color={color ?? C.text}>
          {value}
        </Text>
      </Box>
    )
    const chip = (key: string, text: string, color: string, bg: string = C.chip) => (
      <Text key={key} color={color} backgroundColor={bg}>
        {` ${text} `}
      </Text>
    )

    return (
      <Box flexDirection="column" gap={1} paddingX={1} paddingY={1} backgroundColor={C.bg}>
        <Box justifyContent="space-between">
          <Box gap={1}>
            <Text bold color={C.text}>
              APEX BOOK
            </Text>
            {s.dry_run && chip('dry', 'DRY RUN', '#000000', C.gold)}
          </Box>
          <Box gap={1}>
            <Text color={C.label}>{s.market_state?.phase ?? ''}</Text>
            {stale ? chip('stale', `DESACTUALIZADO ${ago(s.generated_at, now)}`, C.text, C.alert) : <Text color={C.label}>{ago(s.generated_at, now)}</Text>}
          </Box>
        </Box>
        {s.market_state?.banner && <Text color={C.label}>{s.market_state.banner}</Text>}

        {s.positions.length > 0 && (
          <Box flexWrap="wrap" columnGap={2}>
            {sortPositions(s.positions).map((p, i) => (
              <Text key={`tape-${p.ticker}-${i}`}>
                <Text bold color={C.text}>
                  {p.ticker}
                </Text>{' '}
                <Text color={dir(p.change_pct)}>{pct(p.change_pct)}</Text>
              </Text>
            ))}
          </Box>
        )}

        {naked.map((n, i) => (
          <Box key={`naked-${n.ticker}-${i}`} backgroundColor={C.alert} paddingX={1}>
            <Text bold color={C.text}>
              SIN STOP  {n.ticker} {n.position_type}  -  decision manual
            </Text>
          </Box>
        ))}

        <Box gap={1}>
          {kpi('nl', 'Net Liq', money(s.header.net_liq))}
          {kpi('cash', 'Cash', typeof s.header.cash_pct === 'number' ? `${s.header.cash_pct.toFixed(1)}%` : 'pendiente')}
          {kpi('pl', 'P/L del dia', signedMoney(s.header.day_pl_total), dir(s.header.day_pl_total))}
          {kpi('naked', 'Sin stop', String(naked.length), naked.length ? C.down : C.text)}
        </Box>

        {card(
          'positions',
          'POSICIONES',
          s.positions.length,
          <Box flexDirection="column" gap={1}>
            <Box>
              {label('h1', 14, 'Symbol')}
              {label('h2', 11, 'Last', true)}
              {label('h3', 7, 'Qty', true)}
              {label('h4', 11, 'P/L dia', true)}
              {isWide && label('h5', 9, 'A stop', true)}
              {isWide && label('h6', 16, 'Stop > TP1', true)}
            </Box>
            {s.positions.length === 0 && <Text color={C.label}>Sin posiciones.</Text>}
            {sortPositions(s.positions).map((p, i) => {
              const bar = rangeBar(p)
              return (
                <Box key={`p-${p.ticker}-${i}`}>
                  {cell('sym', 14, `${p.naked ? '! ' : ''}${p.ticker}`, { bold: true, color: p.naked ? C.down : C.text, sub: legLabel(p), subColor: C.amber })}
                  {cell('last', 11, price(p.current_price), { right: true, color: dir(p.change_pct), sub: pct(p.change_pct), subColor: dir(p.change_pct) })}
                  {cell('qty', 7, String(p.quantity), { right: true })}
                  {cell('pl', 11, signedMoney(p.day_pl), { right: true, bold: true, color: dir(p.day_pl) })}
                  {isWide && cell('stop', 9, p.naked ? 'sin stop' : pct(p.dist_to_stop_pct, 1), { right: true, color: p.naked ? C.down : C.label })}
                  {isWide && cell('bar', 16, bar?.text ?? '-', { right: true, color: bar?.color === 'error' ? C.down : bar?.color === 'success' ? C.up : C.label })}
                </Box>
              )
            })}
          </Box>,
        )}

        {card(
          'watchlist',
          'WATCHLIST',
          s.watchlist.length,
          <Box flexDirection="column">
            {s.watchlist.length === 0 && <Text color={C.label}>Watchlist vacia.</Text>}
            {sortWatchlist(s.watchlist).map((w, i) => (
              <Box key={`w-${w.ticker}-${i}`} justifyContent="space-between">
                <Box gap={1}>
                  <Box width={8}>
                    <Text bold color={C.text}>
                      {w.ticker}
                    </Text>
                  </Box>
                  <Box width={9} justifyContent="flex-end">
                    <Text color={dir(w.change_pct)}>{price(w.current_price)}</Text>
                  </Box>
                  {chip('dist', `${pct(w.dist_from_entry_pct, 1)} ent.`, C.gold)}
                  {isWide && w.rationale && <Text color={C.label} wrap="truncate">{w.rationale}</Text>}
                </Box>
                <Box gap={1}>
                  {w.conf != null && <Text color={C.up}>{w.conf}%</Text>}
                  {w.alarm_state === 'FIRED'
                    ? chip('st', 'DISPARO', '#000000', C.gold)
                    : w.alarm_state === 'APPROACHING'
                      ? chip('st', 'CERCA', C.gold)
                      : chip('st', 'espera', C.label)}
                </Box>
              </Box>
            ))}
          </Box>,
        )}

        {card(
          'signals',
          'SENALES',
          s.recent_alerts?.length ?? 0,
          <Box flexDirection="column">
            {(s.recent_alerts ?? []).length === 0 && <Text color={C.label}>Sin alertas recientes.</Text>}
            {[...(s.recent_alerts ?? [])].reverse().map((a, i) => (
              <Box key={`a-${i}`} gap={1}>
                <Box width={9}>
                  <Text color={C.label}>{ago(a.sent_at, now)}</Text>
                </Box>
                {chip('k', a.category, a.category === 'VELOCITY' ? C.amber : C.gold)}
                <Box width={7}>
                  <Text bold color={C.text}>
                    {a.ticker}
                  </Text>
                </Box>
                <Text color={C.text}>{a.price.toFixed(2)}</Text>
                {a.move_pct != null && <Text color={dir(a.move_pct)}>{pct(a.move_pct)}</Text>}
              </Box>
            ))}
          </Box>,
        )}

        <Text color={C.label} wrap="truncate">
          {source} | refresca cada 30 s
        </Text>
      </Box>
    )
  })
}
