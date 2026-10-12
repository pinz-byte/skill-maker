import { expect, test } from 'claude-code/testing'

import { INBOX_TEXT, REGISTRY_MD, fetchResult } from './fixture'
import { matchProject, pageText, parseInbox, parseRegistry, statusText } from './register'

test('registry and project matching', () => {
  const reg = parseRegistry(REGISTRY_MD)
  expect(reg).toHaveLength(3)
  expect(matchProject('SKILL MAKER', reg)?.project).toBe('SKILL MAKER')
  expect(matchProject('amorata-carta-natal-os', reg)?.project).toBe('Carta Natal OS')
  expect(matchProject('random', reg)).toBeUndefined()
})

test('inbox messages: unread, expects response, kind and clean text', () => {
  const msgs = parseInbox(pageText(fetchResult(INBOX_TEXT)))
  expect(msgs).toHaveLength(3)
  expect(msgs[0]).toMatchObject({ kind: 'message', from: 'Symbios Dispatcher', isUnread: true, expectsResponse: true, re: '[ASK] package lfp-inbox', date: '2026-10-12 09:15' })
  expect(msgs[0]!.excerpt).toBe('Please review the inbox mod and ship it.')
  expect(msgs[1]).toMatchObject({ kind: 'response', from: 'VMC', isUnread: true, expectsResponse: false })
  expect(msgs[2]).toMatchObject({ from: 'Herald', isUnread: false })
  expect(statusText('SKILL MAKER', msgs.filter(m => m.isUnread))).toBe('Inbox SKILL MAKER: 2 por leer (1 esperan respuesta)')
  expect(statusText('SKILL MAKER', [])).toBe('Inbox SKILL MAKER: al dia')
})
