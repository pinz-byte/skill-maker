import { expect, mock, test } from 'claude-code/testing'

test('a seat argument answers, then submits the skill prompt', async ($, on) => {
  const clock = mock.clock(on)
  const sent: string[] = []
  on('prompt.submit', (_, e) => {
    sent.push(e.text)
    return { text: e.text }
  })

  const out = await $.command.run({ command: 'roundtable', args: 'critical x' } as Parameters<typeof $.command.run>[0])
  expect(out.text).toBe('Convening Critical.')

  await clock.advance(1)
  expect(sent).toEqual(['Use the lfp-thinkers:critical-thinker skill on: x'])
})

test('no argument reports why the pane is not shown', async ($, on) => {
  on('ui.open', () => ({ value: { isPlaced: false, reason: 'no surface places panes' } }))

  const out = await $.command.run({ command: 'roundtable', args: '' } as Parameters<typeof $.command.run>[0])
  expect(out.text).toContain('Pane not shown here (no surface places panes; surfaces: none)')
})
