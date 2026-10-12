import { expect, test } from 'claude-code/testing'

import { SEATS, convene, parse } from './register'

test('a seat becomes its skill command, blank topic falls back to the discussion', () => {
  expect(convene(SEATS[0]!, '  ')).toBe('Use the lfp-thinkers:critical-thinker skill on: the current discussion')
  expect(convene(SEATS[3]!, 'the publish loop')).toBe('Use the lfp-thinkers:loop-breaker skill on: the publish loop')
})

test('hotkeys are unique', () => {
  expect(new Set(SEATS.map(s => s.hotkey)).size).toBe(SEATS.length)
})

test('parse picks the seat by key and keeps the rest as the topic', () => {
  expect(parse('Logic the publish loop')).toEqual({ seat: SEATS[2]!, subject: 'the publish loop' })
  expect(parse('ceo')).toEqual({ seat: SEATS[4]!, subject: '' })
  expect(parse('nonsense here')).toBeUndefined()
})
