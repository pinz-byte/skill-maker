import { expect, test } from 'claude-code/testing'

import { NOW, SNAPSHOT } from './fixture'
import { ago, isStale, legLabel, money, pct, rangeBar, signedMoney, sortPositions, sortWatchlist, summarize } from './register'

test('money and percents read like a blotter', () => {
  expect(money(125430.5)).toBe('$125,431')
  expect(money('PENDING')).toBe('pendiente')
  expect(signedMoney(-842.1)).toBe('-$842')
  expect(signedMoney(310)).toBe('+$310')
  expect(pct(1.25)).toBe('+1.25%')
  expect(pct(null)).toBe('-')
})

test('ages, legs and order', () => {
  expect(ago('2026-10-12T14:58:00Z', NOW)).toBe('hace 2m')
  expect(legLabel(SNAPSHOT.positions[0]!)).toBe('C 635 11-20')
  expect(legLabel(SNAPSHOT.positions[1]!)).toBe('long')
  expect(sortPositions(SNAPSHOT.positions)[0]!.ticker).toBe('IRDM')
  expect(sortWatchlist(SNAPSHOT.watchlist).map(w => w.ticker)).toEqual(['GSAT', 'AMZN', 'NVDA'])
})

test('range bar places price between stop and TP1', () => {
  expect(rangeBar(SNAPSHOT.positions[0]!)).toEqual({ text: 'S[-----#----]T', color: undefined })
  expect(rangeBar(SNAPSHOT.positions[1]!)).toBeUndefined()
})

test('status line and staleness', () => {
  expect(summarize(SNAPSHOT, NOW)).toBe('APEX intraday | NL $125,431 | dia -$842 | 2 pos | 1 sin stop | hace 2m')
  expect(isStale(SNAPSHOT, NOW)).toBe(false)
  expect(isStale(SNAPSHOT, NOW + 30 * 60_000)).toBe(true)
})
