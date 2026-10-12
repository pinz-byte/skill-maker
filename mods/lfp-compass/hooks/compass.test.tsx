import type { On } from 'claude-code'
import { expect, mock, test } from 'claude-code/testing'

import { compassLine, contextPercent, shortMachine } from './register'

test('machine, line and context percent', () => {
  expect(shortMachine('LFP-M2')).toBe('M2')
  expect(shortMachine('LFP-M1.local')).toBe('M1')
  expect(shortMachine('Fernandos-Mac')).toBe('Fernandos-Mac')
  expect(contextPercent({ percent: 42, window: 1 })).toBe(42)
  expect(contextPercent({ tokens: 140_000, window: 200_000 })).toBe(70)
  expect(compassLine({ machine: 'M2', project: 'SKILL MAKER', branch: 'main', pct: 68.4 })).toBe('M2 | SKILL MAKER | main | contexto 68%')
  expect(compassLine({ project: 'x' })).toBe('x')
})

const world = (on: On, percent: number) => {
  const clock = mock.clock(on)
  const statuses: (string | undefined)[] = []
  const sent: string[] = []
  on('process.run', (_, e) => ({
    value: { exitCode: 0, stdout: e.argv[0] === 'scutil' ? 'LFP-M2\n' : 'main\n', stderr: '', isStdoutTruncated: false, isStderrTruncated: false },
  }))
  on('session.cwd', () => ({ value: '/Users/lfp/Projects/SKILL MAKER' }))
  on('session.start', (_, e) => e as never)
  on('session.usage', () => ({ value: { startedAt: 0, context: { window: 200_000, percent }, rateLimits: [] } as never }))
  on('ui.status', (_, e) => {
    statuses.push(e.text)
    return { value: undefined }
  })
  on('prompt.submit', (_, e) => {
    sent.push(e.text)
    return { text: e.text }
  })
  // The engine's own (empty) band beneath the plugin.
  on('ui.render', { component: 'AbovePrompt' }, (t$, e) => {
    const { Box } = t$.ui.resolve(e)
    return <Box key="engine-band" />
  })
  return { statuses, sent, clock }
}

test('the status line names the real machine, project, branch and context', async ($, on) => {
  const { statuses } = world(on, 42)
  await $.session.start({ source: 'startup', cwd: '/Users/lfp/Projects/SKILL MAKER' } as never)
  expect(statuses.at(-1)).toBe('M2 | SKILL MAKER | main | contexto 42%')
})

test('below 70% the band stays out of the way', async ($, on) => {
  world(on, 42)
  await $.session.start({ source: 'startup', cwd: '/Users/lfp/Projects/SKILL MAKER' } as never)
  const ui = await $.ui.mount({ plugin: 'lfp-compass', surface: 'terminal', component: 'AbovePrompt', props: { hasSurvey: false, isWorking: false } as never })
  expect(await ui.find({ key: 'seed' })).toBeUndefined()
})

for (const surface of ['terminal', 'desktop'] as const) {
  test(`at 70% the band offers the seed, and the button asks for it on ${surface}`, async ($, on) => {
    const { sent, clock } = world(on, 71)
    await $.session.start({ source: 'startup', cwd: '/Users/lfp/Projects/SKILL MAKER' } as never)
    const ui = await $.ui.mount({ plugin: 'lfp-compass', surface, component: 'AbovePrompt', props: { hasSurvey: false, isWorking: false } as never })
    expect(await ui.find({ key: 'seed' })).toBeDefined()

    await ui.press({ key: 'seed' })
    await clock.advance(1)
    await clock.settle()
    expect(sent[0]).toContain('lfp-core:continuity-seed')
    expect(await ui.find({ key: 'seed' })).toBeUndefined()
  })
}
