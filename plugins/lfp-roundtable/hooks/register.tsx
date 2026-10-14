import type { EngineInterface, Register } from 'claude-code'

// A seat is one lfp-thinkers skill. The table has no state of its own: each
// /roundtable call is one task -- a focus in, one verdict message out.
export type Seat = { key: string; label: string; skill: string; role: string }

export const SEATS: Seat[] = [
  { key: 'critical', label: 'Critical', skill: 'critical-thinker', role: 'Ataca la idea' },
  { key: 'logic', label: 'Logic', skill: 'logic-thinker', role: 'Expone la cadena de razonamiento' },
  { key: 'creative', label: 'Creative', skill: 'creative-thinker', role: 'Genera opciones' },
  { key: 'loop', label: 'Loop-breaker', skill: 'loop-breaker', role: 'Saca de un ciclo atascado' },
]

const ALL = ['todos', 'all', 'mesa']
export const USAGE = `/roundtable [${SEATS.map(s => s.key).join('|')}|todos] <foco>`

// "/roundtable logic el plan de deploy" -> the logic seat on that focus; "todos ..." -> every seat.
// The focus may come back empty: the command refuses it, the table never picks its own topic.
export const parse = (args: string) => {
  const [word = '', ...rest] = args.trim().split(/\s+/)
  const focus = rest.join(' ').trim()
  if (ALL.includes(word.toLowerCase())) return { seats: SEATS, focus }
  const seat = SEATS.find(s => s.key === word.toLowerCase())

  return seat && { seats: [seat], focus }
}

export const stripFrontmatter = (md: string) =>
  md.startsWith('---') ? md.split('---').slice(2).join('---').trim() : md.trim()

export const seatPrompt = (seat: Seat, body: string, focus: string) =>
  [
    `Pausa la tarea en curso. Ahora hablas como el asiento ${seat.label} de la mesa de thinkers (lfp-thinkers:${seat.skill}).`,
    'Sigue estas instrucciones de su skill:',
    '',
    body,
    '',
    `Aplicalo a esto, dentro del contexto de esta conversacion: ${focus}`,
    'Responde en el idioma de la conversacion. Maximo 250 palabras. Sin preambulo.',
  ].join('\n')

export type Verdict = { seat: Seat; text: string }

// One message for the chat: every seat under the one focus, then what to do with it.
export const digest = (focus: string, verdicts: Verdict[]) =>
  [
    `[Mesa de thinkers] Foco: ${focus}`,
    '',
    ...verdicts.flatMap(v => [`## ${v.seat.label} -- ${v.seat.role}`, v.text, '']),
    'Integra estos veredictos en la tarea en curso: con cual coincides, con cual discrepas y por que, y que cambia en el siguiente paso.',
  ].join('\n')

const skillBody = async ($: EngineInterface, seat: Seat) => {
  const home = (await $.env.get('HOME')) ?? ''
  const path = `${home}/.claude/plugins/marketplaces/lfp-skills/plugins/lfp-thinkers/skills/${seat.skill}/SKILL.md`
  try {
    return stripFrontmatter((await $.fs.read(path)) as string)
  } catch {
    return `Actua como ${seat.label}: ${seat.role}. Se directo y concreto.`
  }
}

const convene = async ($: EngineInterface, seat: Seat, focus: string): Promise<Verdict> => {
  try {
    const answer = await $.model.fork({ prompt: seatPrompt(seat, await skillBody($, seat), focus) })
    if (answer.isAnswered) return { seat, text: answer.text }

    return { seat, text: answer.reason === 'nothing-to-fork' ? 'Todavia no hay conversacion que leer.' : `No respondio (${answer.reason}).` }
  } catch (err) {
    // A refused request lands in the digest like any other answer; it never blocks the table.
    return { seat, text: `No respondio (${err instanceof Error ? err.message : String(err)}).` }
  }
}

// Runs outside the command hook: the command answers at once, the verdicts arrive as one turn.
const table = async ($: EngineInterface, seats: Seat[], focus: string) => {
  $.ui.status(`Mesa: ${seats.map(s => s.label).join(', ')} pensando sobre "${focus}"`)
  try {
    const verdicts = await Promise.all(seats.map(seat => convene($, seat, focus)))
    void $.prompt.submit({ text: digest(focus, verdicts) })
  } finally {
    $.ui.status(undefined)
  }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'roundtable',
      description: 'Mesa de thinkers: un asiento o la mesa completa sobre un foco; el veredicto llega al chat como un solo mensaje',
      argumentHint: '[critical|logic|creative|loop|todos] <foco>',
    })

    return next(e)
  })

  on('command.run', { command: 'roundtable' }, async ($, e) => {
    const picked = parse(e.args)
    if (!picked) return { text: `Asiento desconocido. Usa ${USAGE}` }
    if (!picked.focus) return { text: `Falta el foco -- la mesa no elige su propio tema. Usa ${USAGE}` }
    const { seats, focus } = picked
    $.clock.after(0, () => table($, seats, focus))

    return { text: `${seats.map(s => s.label).join(', ')} pensando sobre "${focus}". El veredicto llega al chat como un solo mensaje.` }
  })
}
