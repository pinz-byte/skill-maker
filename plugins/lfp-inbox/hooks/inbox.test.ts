import type { On } from 'claude-code'
import { expect, mock, test } from 'claude-code/testing'

import { INBOX_TEXT, REGISTRY_MD, fetchResult } from './fixture'

const world = (on: On, opts: { cwd: string; notion?: boolean }) => {
  const clock = mock.clock(on)
  mock.env(on, { HOME: '/Users/lfp' })
  mock.store(on)
  const statuses: (string | undefined)[] = []
  const sent: string[] = []
  const fetched: string[] = []
  on('session.cwd', () => ({ value: opts.cwd }))
  on('session.start', (_, e) => e as never)
  on('command.register', () => ({ value: undefined }) as never)
  on('fs.read', () => ({ value: REGISTRY_MD }))
  on('tool.list', () => ({ value: opts.notion === false ? [] : [{ name: 'mcp__notion-direct__notion-fetch', description: '', mcp: true }] as never }))
  on('mcp.call', (_, e) => {
    fetched.push(`${e.server}:${(e.args as { id: string }).id}`)
    return { value: fetchResult(INBOX_TEXT) as never }
  })
  on('ui.status', (_, e) => {
    statuses.push(e.text)
    return { value: undefined }
  })
  on('ui.open', () => ({ value: { isPlaced: true as const } }))
  on('prompt.submit', (_, e) => {
    sent.push(e.text)
    return { text: e.text }
  })
  return { clock, statuses, sent, fetched }
}

test('a builder sees its own inbox count on the status line', async ($, on) => {
  const w = world(on, { cwd: '/Users/lfp/Projects/SKILL MAKER' })
  await $.session.start({ source: 'startup', cwd: '/Users/lfp/Projects/SKILL MAKER' } as never)
  expect(w.fetched).toEqual(['notion-direct:360da327-abb1-8196-b98d-cfc86bbe0ec6'])
  expect(w.statuses.at(-1)).toBe('Inbox SKILL MAKER: 2 por leer (1 esperan respuesta)')
})

for (const surface of ['terminal', 'desktop'] as const) {
  test(`the pane lists unread mail and processes one on ${surface}`, async ($, on) => {
    const w = world(on, { cwd: '/Users/lfp/Projects/SKILL MAKER' })
    await $.session.start({ source: 'startup', cwd: '/Users/lfp/Projects/SKILL MAKER' } as never)
    expect((await $.command.run({ command: 'inbox', args: '' } as never)).text).toBe('Inbox de SKILL MAKER abierto.')

    const ui = await $.ui.mount({ plugin: 'lfp-inbox', surface, component: 'Pane', requestId: 'inbox', props: {} as never })
    const drawn = JSON.stringify(await ui.drawn())
    for (const piece of ['BUZON', 'SKILL MAKER', '2 por leer', 'Symbios Dispatcher', 'ESPERA RESPUESTA', '[ASK] package lfp-inbox', 'VMC', 'LEIDOS RECIENTES', 'Herald']) {
      expect(drawn).toContain(piece)
    }
    await ui.press({ key: 'process-0' })
    await w.clock.advance(1)
    await w.clock.settle()
    expect(w.sent[0]).toContain('lfp-core:agent-bridge')
    expect(w.sent[0]).toContain('Symbios Dispatcher')
  })
}

test('a project picks its inbox by hand when the folder does not match', async ($, on) => {
  const w = world(on, { cwd: '/Users/lfp/Dev/some-repo' })
  await $.session.start({ source: 'startup', cwd: '/Users/lfp/Dev/some-repo' } as never)
  expect(w.fetched).toEqual([])
  await $.command.run({ command: 'inbox', args: 'usar apex-ultra' } as never)
  expect(w.fetched.at(-1)).toBe('notion-direct:368da327-abb1-817e-9d0c-ce184ee0a69b')
})

test('without a Notion connector it says so', async ($, on) => {
  const w = world(on, { cwd: '/Users/lfp/Projects/SKILL MAKER', notion: false })
  await $.session.start({ source: 'startup', cwd: '/Users/lfp/Projects/SKILL MAKER' } as never)
  expect(w.statuses.at(-1)).toBe('Inbox SKILL MAKER: sin Notion')
})
