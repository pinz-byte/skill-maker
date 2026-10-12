import type { EngineInterface, Register } from 'claude-code'

import type { Run, Seat } from '../types'

const PANE = 'roundtable'
// Session-only: a seat's run lives until the session ends (or the mod reloads).
const runs: Record<string, Run> = {}
let expanded: string[] = []

const CLIP = 700

export const SEATS: Seat[] = [
  { key: 'critical', label: 'Critical', skill: 'critical-thinker', role: 'Ataca la idea', color: 'error', hotkey: '1' },
  { key: 'logic', label: 'Logic', skill: 'logic-thinker', role: 'Expone la cadena de razonamiento', color: 'suggestion', hotkey: '2' },
  { key: 'creative', label: 'Creative', skill: 'creative-thinker', role: 'Genera opciones', color: 'success', hotkey: '3' },
  { key: 'loop', label: 'Loop-breaker', skill: 'loop-breaker', role: 'Saca de un ciclo atascado', color: 'warning', hotkey: '4' },
]

const ALL = ['todos', 'all', 'mesa']
const USAGE = `/roundtable [${SEATS.map(s => s.key).join('|')}|todos] [foco]`

// "/roundtable logic el plan de deploy" -> the logic seat with that focus; "todos" -> every seat.
export const parse = (args: string) => {
  const [word = '', ...rest] = args.trim().split(/\s+/)
  const focus = rest.join(' ')
  if (ALL.includes(word.toLowerCase())) return { seats: SEATS, focus }
  const seat = SEATS.find(s => s.key === word.toLowerCase())

  return seat && { seats: [seat], focus }
}

export const stripFrontmatter = (md: string) =>
  md.startsWith('---') ? md.split('---').slice(2).join('---').trim() : md.trim()

export const seatPrompt = (seat: Seat, body: string, focus?: string) =>
  [
    `Pausa la tarea en curso. Ahora hablas como el asiento ${seat.label} de la mesa de thinkers (lfp-thinkers:${seat.skill}).`,
    'Sigue estas instrucciones de su skill:',
    '',
    body,
    '',
    focus
      ? `Aplicalo a esto, dentro del contexto de esta conversacion: ${focus}`
      : 'Aplicalo a lo que se esta discutiendo ahora en esta conversacion: la ultima decision, plan o afirmacion que importa.',
    'Responde en el idioma de la conversacion. Maximo 250 palabras. Sin preambulo.',
  ].join('\n')

const mmss = (ms: number) => {
  const s = Math.max(0, Math.round(ms / 1000))
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
}

export const statusLabel = (run: Run | undefined, now: number) => {
  if (!run) return 'en espera'
  if (run.status === 'working') return `pensando ${mmss(now - run.startedAt)}`
  if (run.status === 'done') return `listo ${mmss((run.endedAt ?? now) - run.startedAt)}`
  if (run.status === 'chat') return 'trabajando en el chat'
  if (run.status === 'chat-done') return 'respondio en el chat'

  return 'fallo'
}

export const clip = (text: string) => {
  if (text.length <= CLIP) return { text, isClipped: false }
  const cut = text.lastIndexOf('\n', CLIP)

  return { text: `${text.slice(0, cut > CLIP / 2 ? cut : CLIP)}\n\n...`, isClipped: true }
}

const setRun = ($: EngineInterface, key: string, run: Run) => {
  runs[key] = run
  $.ui.invalidate('ui.render')
}

const skillBody = async ($: EngineInterface, seat: Seat) => {
  const home = (await $.env.get('HOME')) ?? ''
  const path = `${home}/.claude/plugins/marketplaces/lfp-skills/plugins/lfp-thinkers/skills/${seat.skill}/SKILL.md`
  try {
    return stripFrontmatter((await $.fs.read(path)) as string)
  } catch {
    return `Actua como ${seat.label}: ${seat.role}. Se directo y concreto.`
  }
}

let ticker: { cancel: () => void } | undefined

// Redraws the elapsed time once a second while any seat is thinking, then stops.
const startTicker = ($: EngineInterface) => {
  if (ticker) return
  ticker = $.clock.every(1000, () => {
    if (Object.values(runs).some(run => run.status === 'working')) return $.ui.invalidate('ui.render')
    ticker?.cancel()
    ticker = undefined
  })
}

const convene = async ($: EngineInterface, seat: Seat, focus?: string) => {
  const startedAt = await $.clock.now()
  setRun($, seat.key, { status: 'working', startedAt, focus })
  startTicker($)
  let isAnswered = false
  let text: string
  try {
    const answer = await $.model.fork({ prompt: seatPrompt(seat, await skillBody($, seat), focus) })
    isAnswered = answer.isAnswered
    text = answer.isAnswered
      ? answer.text
      : answer.reason === 'nothing-to-fork'
        ? 'Todavia no hay conversacion que leer.'
        : `No respondio (${answer.reason}).`
  } catch (err) {
    // A refused request must not leave the card thinking forever.
    text = `No respondio (${err instanceof Error ? err.message : String(err)}).`
  }
  setRun($, seat.key, { status: isAnswered ? 'done' : 'error', startedAt, endedAt: await $.clock.now(), text, focus })
}

// Runs outside the calling hook: a command or press must not wait on the model.
const conveneLater = ($: EngineInterface, seats: Seat[], focus?: string) =>
  $.clock.after(0, () => Promise.all(seats.map(seat => convene($, seat, focus))))

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'roundtable',
      description: 'Thinkers panel: call a seat, or the whole table, on this conversation',
      argumentHint: '[critical|logic|creative|loop|todos] [foco]',
    })

    return next(e)
  })

  on('command.run', { command: 'roundtable' }, async ($, e) => {
    const opened = await $.ui.open({ id: PANE, title: 'Roundtable' })
    const where = opened.isPlaced ? 'en el panel' : `(panel no visible aqui: ${opened.reason})`
    if (!e.args.trim()) return { text: opened.isPlaced ? 'Roundtable abierto.' : `Roundtable ${where}. Usa ${USAGE}` }

    const picked = parse(e.args)
    if (!picked) return { text: `Asiento desconocido. Usa ${USAGE}` }
    conveneLater($, picked.seats, picked.focus || undefined)

    return { text: `${picked.seats.map(s => s.label).join(', ')} trabajando ${where}.` }
  })

  // Claude calling a thinker skill in the chat shows on its card too.
  on('tool.call', { tool: 'Skill' }, async ($, e, next) => {
    const seat = SEATS.find(s => e.skill === s.skill || e.skill.endsWith(`:${s.skill}`))
    if (seat) setRun($, seat.key, { status: 'chat', startedAt: await $.clock.now() })

    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    const now = await $.clock.now()
    for (const [key, run] of Object.entries(runs)) {
      if (run.status === 'chat') setRun($, key, { ...run, status: 'chat-done', endedAt: now })
    }

    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Button, Markdown, Text } = $.ui.resolve(e)
    const now = await $.clock.now()
    const open = expanded
    const isBusy = Object.values(runs).some(run => run.status === 'working')
    const toggle = (key: string) => {
      expanded = open.includes(key) ? open.filter(k => k !== key) : [...open, key]
      $.ui.invalidate('ui.render')
    }

    return (
      <Box flexDirection="column" gap={1}>
        <Box justifyContent="space-between">
          <Text bold>MESA DE THINKERS</Text>
          <Text dimColor>leen: este chat</Text>
        </Box>
        {SEATS.map(seat => {
          const run = runs[seat.key]
          const isWorking = run?.status === 'working' || run?.status === 'chat'
          const shown = run?.text ? (open.includes(seat.key) ? { text: run.text, isClipped: false } : clip(run.text)) : undefined

          return (
            <Box
              key={seat.key}
              flexDirection="column"
              borderStyle="round"
              borderColor={isWorking ? seat.color : 'subtle'}
              paddingX={1}
            >
              <Box justifyContent="space-between">
                <Text bold color={seat.color}>
                  {seat.label.toUpperCase()}
                </Text>
                <Text color={isWorking ? seat.color : undefined} dimColor={!isWorking}>
                  {statusLabel(run, now)}
                </Text>
              </Box>
              <Text dimColor>
                {seat.role}
                {run?.focus ? `  |  foco: ${run.focus}` : ''}
              </Text>
              {shown && <Markdown key={`${seat.key}-text`} text={shown.text} />}
              {!isWorking && (
                <Box gap={1}>
                  {run?.status === 'done' ? (
                    <>
                      <Button
                        key={`${seat.key}-chat`}
                        label="Llevar al chat"
                        variant="primary"
                        onPress={() => {
                          $.clock.after(0, () =>
                            $.prompt.submit({
                              text: `[Mesa de thinkers - ${seat.label}]\n\n${run.text}\n\nToma en cuenta este analisis del asiento ${seat.label}.`,
                            }),
                          )
                        }}
                      />
                      <Button key={`${seat.key}-again`} label="Otra vez" hotkey={seat.hotkey} onPress={() => conveneLater($, [seat])} />
                      {(shown?.isClipped || open.includes(seat.key)) && (
                        <Button
                          key={`${seat.key}-more`}
                          label={open.includes(seat.key) ? 'Ver menos' : 'Ver todo'}
                          dimColor
                          onPress={() => toggle(seat.key)}
                        />
                      )}
                    </>
                  ) : (
                    <Button key={`${seat.key}-call`} label="Llamar" hotkey={seat.hotkey} onPress={() => conveneLater($, [seat])} />
                  )}
                </Box>
              )}
            </Box>
          )
        })}
        {!isBusy && (
          <Button key="all" label="Mesa completa: llamar a los 4" variant="primary" hotkey="0" onPress={() => conveneLater($, SEATS)} />
        )}
      </Box>
    )
  })
}
