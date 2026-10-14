import { expect, mock, test } from 'claude-code/testing'

import { SEATS, digest, parse, seatPrompt, stripFrontmatter } from './register'

const answered = (text: string) => ({
  value: { isAnswered: true as const, text, usage: { input_tokens: 1, output_tokens: 1, cache_creation_input_tokens: 0, cache_read_input_tokens: 0 } },
})

test('parse picks one seat or the whole table and keeps the focus; no focus comes back empty', () => {
  expect(parse('Logic el plan de deploy')).toEqual({ seats: [SEATS[1]!], focus: 'el plan de deploy' })
  expect(parse('todos el plan')?.seats).toHaveLength(4)
  expect(parse('todos')?.focus).toBe('')
  expect(parse('nadie aqui')).toBeUndefined()
})

test('the seat prompt carries the skill body and the focus', () => {
  const body = stripFrontmatter('---\nname: x\n---\n\n# Critical\nAtaca.')
  expect(body).toBe('# Critical\nAtaca.')
  const prompt = seatPrompt(SEATS[0]!, body, 'el recordatorio')
  expect(prompt).toContain('# Critical\nAtaca.')
  expect(prompt).toContain('el recordatorio')
})

test('the digest puts every seat under the one focus and ends with the integration ask', () => {
  const text = digest('el plan', [
    { seat: SEATS[0]!, text: 'La tesis es falsa.' },
    { seat: SEATS[1]!, text: 'Premisa 1 no se sostiene.' },
  ])
  expect(text.startsWith('[Mesa de thinkers] Foco: el plan')).toBe(true)
  expect(text).toContain('## Critical -- Ataca la idea\nLa tesis es falsa.')
  expect(text).toContain('## Logic -- Expone la cadena de razonamiento\nPremisa 1 no se sostiene.')
  expect(text).toContain('Integra estos veredictos')
})

test('a call without a focus is refused and forks nothing', async ($, on) => {
  const clock = mock.clock(on)
  let forks = 0
  on('model.fork', () => {
    forks += 1
    return answered('ok')
  })

  const out = await $.command.run({ command: 'roundtable', args: 'todos' } as Parameters<typeof $.command.run>[0])
  expect(out.text).toContain('Falta el foco')
  await clock.advance(1)
  await clock.settle()
  expect(forks).toBe(0)
})

test('an unknown seat says so', async ($) => {
  const out = await $.command.run({ command: 'roundtable', args: 'nadie el plan' } as Parameters<typeof $.command.run>[0])
  expect(out.text).toContain('Asiento desconocido')
})

test('the whole table forks every seat on the focus and lands ONE message in the chat', async ($, on) => {
  const clock = mock.clock(on)
  mock.env(on, { HOME: '/nowhere' })
  const prompts: string[] = []
  const sent: string[] = []
  on('model.fork', (_, e) => {
    prompts.push(e.prompt)
    return answered(`veredicto ${prompts.length}`)
  })
  on('prompt.submit', (_, e) => {
    sent.push(e.text)
    return { text: e.text }
  })

  const out = await $.command.run({ command: 'roundtable', args: 'todos el plan de deploy' } as Parameters<typeof $.command.run>[0])
  expect(out.text).toBe('Critical, Logic, Creative, Loop-breaker pensando sobre "el plan de deploy". El veredicto llega al chat como un solo mensaje.')

  await clock.advance(1)
  await clock.settle()
  expect(prompts).toHaveLength(4)
  for (const p of prompts) expect(p).toContain('el plan de deploy')
  expect(sent).toHaveLength(1)
  expect(sent[0]).toContain('[Mesa de thinkers] Foco: el plan de deploy')
  for (const seat of SEATS) expect(sent[0]).toContain(`## ${seat.label} -- ${seat.role}`)
  expect(sent[0]).toContain('veredicto 1')
  expect(sent[0]).toContain('veredicto 4')
})

test('one seat called alone lands its own message', async ($, on) => {
  const clock = mock.clock(on)
  mock.env(on, { HOME: '/nowhere' })
  const sent: string[] = []
  on('model.fork', () => answered('La tesis es falsa.'))
  on('prompt.submit', (_, e) => {
    sent.push(e.text)
    return { text: e.text }
  })

  await $.command.run({ command: 'roundtable', args: 'critical el recordatorio' } as Parameters<typeof $.command.run>[0])
  await clock.advance(1)
  await clock.settle()
  expect(sent).toHaveLength(1)
  expect(sent[0]).toContain('## Critical -- Ataca la idea\nLa tesis es falsa.')
  expect(sent[0]).not.toContain('## Logic')
})

test('a failed fork is reported inside the digest instead of blocking the table', async ($, on) => {
  const clock = mock.clock(on)
  mock.env(on, { HOME: '/nowhere' })
  const sent: string[] = []
  on('model.fork', () => ({ value: { isAnswered: false as const, reason: 'nothing-to-fork' as const } }))
  on('prompt.submit', (_, e) => {
    sent.push(e.text)
    return { text: e.text }
  })

  await $.command.run({ command: 'roundtable', args: 'logic el plan' } as Parameters<typeof $.command.run>[0])
  await clock.advance(1)
  await clock.settle()
  expect(sent).toHaveLength(1)
  expect(sent[0]).toContain('Todavia no hay conversacion que leer.')
})
