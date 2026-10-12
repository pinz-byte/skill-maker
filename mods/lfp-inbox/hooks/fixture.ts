// Shaped like a real agent-bridge inbox page as notion-fetch returns it (emoji as escapes: the repo is ASCII-only).
export const REGISTRY_MD = [
  '| Project | Host | Notion Inbox UUID |',
  '|---|---|---|',
  '| SKILL MAKER | Cowork M2 | `360da327-abb1-8196-b98d-cfc86bbe0ec6` |',
  '| apex-ultra | Cowork M1 | `368da327-abb1-817e-9d0c-ce184ee0a69b` |',
  '| Carta Natal OS | Cowork M3 | `360da327-abb1-81f5-a0ed-e5fd571f01f1` |',
].join('\n')

export const INBOX_TEXT = [
  '<page url="https://app.notion.com/p/360da327abb18196b98dcfc86bbe0ec6">',
  '<content>',
  '---',
  '\u{1F4E8} **NEW MESSAGE**',
  '**FROM:** Symbios Dispatcher',
  '**TO:** SKILL MAKER',
  '**DATE:** 2026-10-12 09:15 -05',
  '**STATUS:** \u{1F534} UNREAD',
  '**RE:** \\[ASK\\] package lfp-inbox',
  'Please review the inbox mod and ship it.',
  '**EXPECTS RESPONSE:** Yes — confirm when shipped',
  '**REPLY TO:** Symbios — Inbox (UUID: 360da327-abb1-8115-bf58-fcaec470ec53)',
  '---',
  '\u{1F4E8} **RESPONSE**',
  '**FROM:** VMC',
  '**TO:** SKILL MAKER',
  '**DATE:** 2026-10-11 18:00',
  '**STATUS:** \u{1F534} UNREAD',
  '**RE:** spend audit',
  'Numbers attached.',
  '**EXPECTS RESPONSE:** No',
  '---',
  '\u{1F4E8} **NEW MESSAGE**',
  '**FROM:** Herald',
  '**DATE:** 2026-09-01 10:00',
  '**STATUS:** ✅ READ — 2026-09-01 11:00',
  '**RE:** config drift',
  'Old news.',
  '**EXPECTS RESPONSE:** Yes',
  '---',
  '</content>',
].join('\n')

export const fetchResult = (text: string) => ({ content: [{ type: 'text', text: JSON.stringify({ title: 'Inbox', text }) }], isError: false })
