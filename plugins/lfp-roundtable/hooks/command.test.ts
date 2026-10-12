import { expect, mock, test } from 'claude-code/testing'


const placed = () => ({ value: { isPlaced: true as const } })

test('a seat called from the chat thinks in the pane and lands its answer', async ($, on) => {
  const clock = mock.clock(on)
  mock.env(on, { HOME: '/nowhere' })
  const prompts: string[] = []
  on('ui.open', placed)
  on('model.fork', (_, e) => {
    prompts.push(e.prompt)
    return { value: { isAnswered: true as const, text: 'La tesis es falsa.', usage: { input_tokens: 1, output_tokens: 1, cache_creation_input_tokens: 0, cache_read_input_tokens: 0 } } }
  })

  const out = await $.command.run({ command: 'roundtable', args: 'critical el recordatorio' } as Parameters<typeof $.command.run>[0])
  expect(out.text).toBe('Critical trabajando en el panel.')

  await clock.advance(1)
  await clock.settle()
  expect(prompts).toHaveLength(1)
  expect(prompts[0]).toContain('el recordatorio')
  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ plugin: 'lfp-roundtable', surface, component: 'Pane', requestId: 'roundtable', props: {} as never })
    expect((await ui.find({ key: 'critical-text' }))?.text).toContain('La tesis es falsa.')
    expect(await ui.find({ key: 'critical-chat' })).toBeDefined()
    expect(await ui.find({ key: 'logic-call' })).toBeDefined()
    await ui.unmount()
  }
})

test('the whole table runs every seat', async ($, on) => {
  const clock = mock.clock(on)
  mock.env(on, { HOME: '/nowhere' })
  on('ui.open', placed)
  let calls = 0
  on('model.fork', () => {
    calls += 1
    return { value: { isAnswered: true as const, text: 'ok', usage: { input_tokens: 1, output_tokens: 1, cache_creation_input_tokens: 0, cache_read_input_tokens: 0 } } }
  })

  const out = await $.command.run({ command: 'roundtable', args: 'todos' } as Parameters<typeof $.command.run>[0])
  expect(out.text).toBe('Critical, Logic, Creative, Loop-breaker trabajando en el panel.')
  await clock.advance(1)
  await clock.settle()
  expect(calls).toBe(4)
})

test('an unplaced pane says why', async ($, on) => {
  on('ui.open', () => ({ value: { isPlaced: false as const, reason: 'no surface' } }))
  const out = await $.command.run({ command: 'roundtable', args: '' } as Parameters<typeof $.command.run>[0])
  expect(out.text).toContain('panel no visible aqui: no surface')
})

test('a failed fork marks the seat as failed instead of thinking forever', async ($, on) => {
  const clock = mock.clock(on)
  mock.env(on, { HOME: '/nowhere' })
  on('ui.open', placed)
  on('model.fork', () => ({ value: { isAnswered: false as const, reason: 'nothing-to-fork' as const } }))

  await $.command.run({ command: 'roundtable', args: 'logic' } as Parameters<typeof $.command.run>[0])
  await clock.advance(1)
  await clock.settle()
  const ui = await $.ui.mount({ plugin: 'lfp-roundtable', surface: 'desktop', component: 'Pane', requestId: 'roundtable', props: {} as never })
  expect((await ui.find({ key: 'logic-text' }))?.text).toContain('Todavia no hay conversacion')
  expect(await ui.find({ key: 'logic-call' })).toBeDefined()
})
