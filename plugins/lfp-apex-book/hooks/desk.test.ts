import type { On } from 'claude-code'
import { expect, mock, test } from 'claude-code/testing'

import { NOW, SNAPSHOT } from './fixture'

const world = (on: On, files: Record<string, string>) => {
  const clock = mock.clock(on, { now: NOW } as never)
  mock.env(on, { HOME: '/Users/usuario' })
  on('session.cwd', () => ({ value: '/Users/usuario/Documents/Claude/Projects/apex-ultra' }))
  on('fs.stat', (_, e) =>
    e.path in files ? { value: { kind: 'file' as const, size: 1, mtimeMs: 1, isLink: false } } : { deny: 'ENOENT' },
  )
  on('fs.read', (_, e) => (e.path in files ? { value: files[e.path]! } : { deny: 'ENOENT' }))
  const opened: string[] = []
  on('ui.open', (_, e) => {
    opened.push(e.id)
    return { value: { isPlaced: true as const } }
  })
  return { clock, opened }
}

const run = ($: { command: { run: (input: never) => Promise<{ text?: string }> } }) =>
  $.command.run({ command: 'apex', args: '' } as never)

for (const surface of ['terminal', 'desktop'] as const) {
  test(`the desk draws the book on ${surface}`, async ($, on) => {
    world(on, { '/Users/usuario/Documents/Claude/Projects/apex-ultra/snapshot.json': JSON.stringify(SNAPSHOT) })
    expect((await run($)).text).toBe('APEX Book abierto.')

    const ui = await $.ui.mount({ plugin: 'lfp-apex-book', surface, component: 'Pane', requestId: 'apex-book', props: {} as never })
    const text = JSON.stringify(await ui.drawn())
    for (const piece of ['APEX BOOK', 'Net Liq', '$125,431', '-$842', 'SIN STOP', 'POSICIONES', 'META', 'C 635 11-20', 'WATCHLIST', 'DISPARO', 'CERCA', 'SENALES', 'VELOCITY']) {
      expect(text).toContain(piece)
    }
  })
}

test('outside apex-ultra it says where to run, and keeps quiet', async ($, on) => {
  world(on, {})
  expect((await run($)).text).toContain('No encuentro snapshot.json')
})

test('using an APEX skill raises the desk; other skills do not', async ($, on) => {
  const { opened } = world(on, { '/Users/usuario/Documents/Claude/Projects/apex-ultra/snapshot.json': JSON.stringify(SNAPSHOT) })
  on('tool.call', { tool: 'Skill' }, () => ({ result: 'ok', text: 'ok' }) as never)

  await ($ as never as { tool: { call: (i: never) => Promise<unknown> } }).tool.call({ tool: 'Skill', skill: 'lfp-apex:council' } as never)
  expect(opened).toEqual(['apex-book'])
  await ($ as never as { tool: { call: (i: never) => Promise<unknown> } }).tool.call({ tool: 'Skill', skill: 'lfp-core:git-ops' } as never)
  expect(opened).toEqual(['apex-book'])
})
