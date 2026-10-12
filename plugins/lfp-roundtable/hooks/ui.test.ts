import { expect, mock, test } from 'claude-code/testing'

for (const surface of ['terminal', 'desktop'] as const) {
  test(`an idle table shows four seats and the whole-table button on ${surface}`, async ($, on) => {
    mock.clock(on)
    const ui = await $.ui.mount({ plugin: 'lfp-roundtable', surface, component: 'Pane', requestId: 'roundtable', props: {} as never })
    expect(await ui.findAll({ type: 'Button' })).toHaveLength(5)
    expect(await ui.find({ key: 'all' })).toBeDefined()
  })
}

test('pressing a seat runs it, and "Llevar al chat" hands the answer to the chat', async ($, on) => {
  const clock = mock.clock(on)
  mock.env(on, { HOME: '/nowhere' })
  const sent: string[] = []
  on('model.fork', () => ({ value: { isAnswered: true as const, text: 'Opcion A, opcion B.', usage: { input_tokens: 1, output_tokens: 1, cache_creation_input_tokens: 0, cache_read_input_tokens: 0 } } }))
  on('prompt.submit', (_, e) => {
    sent.push(e.text)
    return { text: e.text }
  })
  const ui = await $.ui.mount({ plugin: 'lfp-roundtable', surface: 'desktop', component: 'Pane', requestId: 'roundtable', props: {} as never })

  await ui.press({ key: 'creative-call' })
  await clock.advance(1)
  await clock.settle()
  expect((await ui.find({ key: 'creative-text' }))?.text).toContain('Opcion A')

  await ui.press({ key: 'creative-chat' })
  await clock.advance(1)
  await clock.settle()
  expect(sent[0]).toContain('[Mesa de thinkers - Creative]')
  expect(sent[0]).toContain('Opcion A, opcion B.')
})

test('using a thinker skill in the chat raises the table with that seat working', async ($, on) => {
  mock.clock(on)
  const opened: string[] = []
  on('ui.open', (_, e) => {
    opened.push(e.id)
    return { value: { isPlaced: true as const } }
  })
  on('tool.call', { tool: 'Skill' }, () => ({ result: 'ok', text: 'ok' }) as never)

  await $.tool.call({ tool: 'Skill', skill: 'lfp-thinkers:logic-thinker' } as never)
  expect(opened).toEqual(['roundtable'])
  const ui = await $.ui.mount({ plugin: 'lfp-roundtable', surface: 'desktop', component: 'Pane', requestId: 'roundtable', props: {} as never })
  expect(JSON.stringify(await ui.drawn())).toContain('trabajando en el chat')

  await $.tool.call({ tool: 'Skill', skill: 'lfp-core:git-ops' } as never)
  expect(opened).toEqual(['roundtable'])
})
