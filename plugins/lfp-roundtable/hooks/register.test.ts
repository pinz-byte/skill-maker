import { expect, test } from 'claude-code/testing'

import { SEATS, clip, parse, seatPrompt, statusLabel, stripFrontmatter } from './register'

test('parse picks one seat, or the whole table, and keeps the focus', () => {
  expect(parse('Logic el plan de deploy')).toEqual({ seats: [SEATS[1]!], focus: 'el plan de deploy' })
  expect(parse('todos')?.seats).toHaveLength(4)
  expect(parse('nadie aqui')).toBeUndefined()
})

test('status reads as the card shows it', () => {
  expect(statusLabel(undefined, 0)).toBe('en espera')
  expect(statusLabel({ status: 'working', startedAt: 0 }, 64_000)).toBe('pensando 1:04')
  expect(statusLabel({ status: 'done', startedAt: 0, endedAt: 12_000 }, 99_000)).toBe('listo 0:12')
  expect(statusLabel({ status: 'chat', startedAt: 0 }, 5_000)).toBe('trabajando en el chat')
})

test('long answers are clipped on a line break, short ones are whole', () => {
  expect(clip('corto')).toEqual({ text: 'corto', isClipped: false })
  const long = Array.from({ length: 40 }, (_, i) => `linea ${i} ${'x'.repeat(20)}`).join('\n')
  const cut = clip(long)
  expect(cut.isClipped).toBe(true)
  expect(cut.text.length).toBeLessThan(long.length)
})

test('the seat prompt carries the skill body and the focus', () => {
  const body = stripFrontmatter('---\nname: x\n---\n\n# Critical\nAtaca.')
  expect(body).toBe('# Critical\nAtaca.')
  const prompt = seatPrompt(SEATS[0]!, body, 'el recordatorio')
  expect(prompt).toContain('# Critical\nAtaca.')
  expect(prompt).toContain('el recordatorio')
})
