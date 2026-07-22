# Rule: Inbox Registry & Bridge Conventions

## UUID is the only reliable identifier

Name search (Notion semantic search) fails across environments.
Always use page UUIDs when routing bridge messages.

## Current inbox registry

| Project | Host | UUID |
|---|---|---|
| SKILL MAKER | Cowork M2 | 360da327-abb1-8196-b98d-cfc86bbe0ec6 |
| Herald | Cowork M3 | 360da327-abb1-819d-850b-e86dc3293e94 |
| Push Notifier | Cowork M3 | 360da327-abb1-81ab-96a9-f83bdb93acc0 |
| Subastop | Cowork M1 | 360da327-abb1-81a1-825b-ddf7555604ee |
| CarMatch | Cowork M2 | 360da327-abb1-815c-8975-d044371bf23c |
| Sensei | Cowork M1/M2 | 360da327-abb1-81a8-8df0-f1321e578d4d |
| Symbios | Claude.ai Chat | 360da327-abb1-8115-bf58-fcaec470ec53 |
| APEX DESK | Claude.ai Chat | 360da327-abb1-816c-8df5-e02f45e3bbde |
| Life Archive | Claude.ai Chat | 360da327-abb1-8180-8894-e65c44b1ad83 |
| Second Self | Claude.ai Chat | 360da327-abb1-81a7-b342-c1f2f4f35495 |
| AVT CarMatch | Cowork M2 | 360da327-abb1-81a8-828f-db2745d30667 |
| Extractor | Cowork M2 | 360da327-abb1-8139-9b22-f98155a3b600 |
| VMC | Cowork M3 | 360da327-abb1-81bf-80d5-d910c59b9476 |
| Agency | Cowork M3 | 360da327-abb1-8169-9ca2-cb6ef0d0d04d |
| Echo Chamber | Cowork M3 | 360da327-abb1-8131-b1df-d35f9d395a91 |
| Carta Natal OS | Cowork M3 | 360da327-abb1-81f5-a0ed-e5fd571f01f1 |
| Tenant Farm | Cowork M3 | 360da327-abb1-819a-9206-ce785d2d6547 |
| Subascars | Cowork M3 | 360da327-abb1-81f1-82ac-ca47d195312f |
| apex-ultra | Cowork M1 | 368da327-abb1-817e-9d0c-ce184ee0a69b |
| Symbios Builder | Cowork M1 | 397da327-abb1-8111-8df3-d0298eee9784 |
| ChatGPT | ChatGPT (web) | 397da327-abb1-81da-9512-c7785c3c9974 |
| Digital Edge | Cowork M-DigitalEdge | 392da327-abb1-81b4-b772-c929c756bc45 |

## DB-mode inboxes (autonomous agent processing)

Some inboxes are DATABASES, not flat pages. Messages to them are created as DB rows
(pages in the data source), NOT prepended blocks. A Notion Claude External Agent
("Symbios Courier") triggers on page-added and processes autonomously — no
"you've got mail" needed on the receiving side.

| Project | DB page ID | Data source ID | Since |
|---|---|---|---|
| Symbios | 1ed6e797-bcd8-4d99-8de0-51e82b0f2983 | fad1c35d-0143-473b-b119-439aa643640a | 2026-07-20 |

SEND to a DB-mode inbox: create a page in the data source with properties
Name (subject), From, Host (select), Status=UNREAD, Expects Response (checkbox),
Reply To UUID (your inbox UUID); full message body as page content.
The legacy Symbios flat-page inbox (360da327-abb1-8115-bf58-fcaec470ec53) remains
as archive and manual fallback until cutover completes (3 consecutive clean
processings — see PLAN_SYMBIOS_EXTERNAL_AGENT_2026-07-20.md).

## When adding a new project

1. Create the Notion inbox page
2. Add the row to the table above -- this file is the SINGLE SOURCE OF TRUTH
3. Run `python3 gen-inbox-registry.py` (or `./publish.sh`) to regenerate
   agent-bridge/SKILL.md's table -- never hand-edit that table; it is generated
4. Rebuild and deploy via `./publish.sh`

## Bridge message minimum fields

FROM, HOST, TO, DATE, STATUS, message body, EXPECTS RESPONSE, REPLY TO (with UUID)
