import type { EngineInterface, Register } from 'claude-code'

import type { InboxEntry, Message } from '../types'

const PANE = 'inbox'
const POLL_MS = 5 * 60_000
const EXCERPT = 280

// ---------- parsing (pure, tested) ----------

// The generated table in agent-bridge/SKILL.md: | Project | Host | `uuid` |
export const parseRegistry = (md: string): InboxEntry[] =>
  md
    .split('\n')
    .map(line => line.match(/^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*`?([0-9a-f]{8}-[0-9a-f-]{27})`?\s*\|/i))
    .filter((m): m is RegExpMatchArray => !!m)
    .map(m => ({ project: m[1]!, host: m[2]!, uuid: m[3]! }))

const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9]/g, '')

// "SKILL MAKER" -> SKILL MAKER; "amorata-carta-natal-os" -> Carta Natal OS (longest name inside wins).
export const matchProject = (folder: string, registry: InboxEntry[]) => {
  const f = norm(folder)
  const hits = registry.filter(r => {
    const p = norm(r.project)
    return p.length > 2 && (f === p || f.includes(p) || p.includes(f))
  })

  return hits.sort((a, b) => (norm(a.project) === f ? -1 : norm(b.project) === f ? 1 : b.project.length - a.project.length))[0]
}

const field = (block: string, name: string) => {
  const m = block.match(new RegExp(`\\**${name}:\\**\\s*(.+)`, 'i'))
  return m ? m[1]!.replace(/\*+/g, '').trim() : undefined
}

// Strip Notion markup down to readable text for an excerpt.
const clean = (s: string) =>
  s
    .replace(/<mention-page[^>]*>([^<]*)<\/mention-page>/g, '$1')
    .replace(/<[^>]+>/g, '')
    .replace(/\\([[\]~*_`#()-])/g, '$1')
    .replace(/\*\*|__|`/g, '')
    .split('\n')
    .filter(line => !/^\s*-{3,}\s*$/.test(line))
    .join('\n')
    .replace(/[^\S\n]+/g, ' ')
    .replace(/\n{2,}/g, '\n')
    .trim()

// One message per "---"-separated block that names a sender. Newest first, as the inbox keeps them.
export const parseInbox = (text: string): Message[] =>
  text
    .split(/\n-{3,}\s*\n/)
    .filter(block => /FROM:/i.test(block))
    .map(block => {
      const status = field(block, 'STATUS') ?? ''
      const body = block
        .split('\n')
        .filter(l => !/^\s*\**\s*(FROM|TO|HOST|DATE|STATUS|RE|EXPECTS RESPONSE|REPLY TO|ATTACH):/i.test(l))
        .filter(l => !/NEW MESSAGE|RESPONSE\*{0,2}\s*$/i.test(l))
        .join('\n')
      const excerpt = clean(body)

      return {
        kind: /\bRESPONSE\b/.test(block.split('\n').slice(0, 3).join(' ')) ? ('response' as const) : ('message' as const),
        from: field(block, 'FROM') ?? '?',
        to: field(block, 'TO'),
        date: (field(block, 'DATE') ?? '').match(/\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2})?/)?.[0],
        re: (() => { const re = field(block, 'RE'); return re && clean(re) })(),
        isUnread: /UNREAD/i.test(status),
        expectsResponse: /^(yes|si|s\u00ed)/i.test(field(block, 'EXPECTS RESPONSE') ?? ''),
        excerpt: excerpt.length > EXCERPT ? `${excerpt.slice(0, EXCERPT).trimEnd()}...` : excerpt,
      }
    })

export const pageText = (result: { content: { type: string; text?: string }[] }) => {
  const raw = result.content.map(c => c.text ?? '').join('\n')
  try {
    const parsed = JSON.parse(raw) as { text?: string }
    return typeof parsed.text === 'string' ? parsed.text : raw
  } catch {
    return raw
  }
}

export const statusText = (project: string, unread: Message[]) => {
  if (unread.length === 0) return `Inbox ${project}: al dia`
  const waiting = unread.filter(m => m.expectsResponse).length

  return `Inbox ${project}: ${unread.length} por leer${waiting ? ` (${waiting} esperan respuesta)` : ''}`
}

export const ago = (date: string | undefined, now: number) => {
  if (!date) return ''
  const ms = now - Date.parse(date.replace(' ', 'T'))
  if (!Number.isFinite(ms)) return date
  const h = Math.round(ms / 3_600_000)
  if (h < 1) return 'hace un rato'
  return h < 48 ? `hace ${h}h` : `hace ${Math.round(h / 24)}d`
}

// ---------- session state ----------

let inbox: InboxEntry | undefined
let registry: InboxEntry[] = []
let messages: Message[] = []
let checkedAt: number | undefined
let problem: string | undefined
let notionServer: string | undefined

const unreadOf = () => messages.filter(m => m.isUnread)

const loadRegistry = async ($: EngineInterface) => {
  const home = (await $.env.get('HOME')) ?? ''
  const path = `${home}/.claude/plugins/marketplaces/lfp-skills/plugins/lfp-core/skills/agent-bridge/SKILL.md`
  try {
    registry = parseRegistry((await $.fs.read(path)) as string)
  } catch {
    registry = []
  }
}

const pickInbox = async ($: EngineInterface) => {
  const cwd = await $.session.cwd()
  const chosen = (await $.store.get(`project:${cwd}`)) as string | undefined
  const folder = cwd.replace(/\/+$/, '').split('/').pop() ?? cwd
  inbox = (chosen && registry.find(r => r.project === chosen)) || matchProject(folder, registry)
}

const findNotion = async ($: EngineInterface) => {
  if (notionServer) return notionServer
  const tools = await $.tool.list()
  const hit = tools.map(t => t.name.match(/^mcp__(.+)__notion-fetch$/)).find(Boolean)
  notionServer = hit?.[1]

  return notionServer
}

const check = async ($: EngineInterface) => {
  if (!inbox) {
    problem = 'Este proyecto no tiene inbox en el registro. Usa /inbox usar <Proyecto>.'
    $.ui.status(undefined)
    $.ui.invalidate('ui.render')
    return
  }
  const server = await findNotion($)
  if (!server) {
    problem = 'No hay conector de Notion en esta sesion.'
    $.ui.status(`Inbox ${inbox.project}: sin Notion`)
    $.ui.invalidate('ui.render')
    return
  }
  try {
    const result = await $.mcp.call(server, 'notion-fetch', { id: inbox.uuid })
    if (result.isError) throw new Error(pageText(result).slice(0, 200))
    const before = new Set(unreadOf().map(m => `${m.from}|${m.date}|${m.re}`))
    messages = parseInbox(pageText(result))
    const fresh = unreadOf().filter(m => !before.has(`${m.from}|${m.date}|${m.re}`))
    if (checkedAt !== undefined && fresh.length) $.ui.toast(`Inbox: nuevo mensaje de ${fresh[0]!.from}`)
    checkedAt = await $.clock.now()
    problem = undefined
  } catch (err) {
    problem = `No pude leer el inbox: ${err instanceof Error ? err.message : String(err)}`
  }
  $.ui.status(problem && checkedAt === undefined ? `Inbox ${inbox.project}: error` : statusText(inbox.project, unreadOf()))
  $.ui.invalidate('ui.render')
}

const ask = ($: EngineInterface, text: string) => {
  // From a press or command: a later dispatch submits once the session is idle.
  $.clock.after(0, () => $.prompt.submit({ text }))
}

// ---------- hooks ----------

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'inbox',
      description: 'Mesh inbox for this project: unread messages to process',
      argumentHint: '[usar <Proyecto>]',
    })
    await loadRegistry($)
    await pickInbox($)
    await check($)
    $.clock.every(POLL_MS, () => check($))

    return next(e)
  })

  on('command.run', { command: 'inbox' }, async ($, e) => {
    const use = e.args.trim().match(/^usar\s+(.+)$/i)
    if (use) {
      const entry = registry.find(r => norm(r.project) === norm(use[1]!))
      if (!entry) return { text: `No existe ese inbox. Proyectos: ${registry.map(r => r.project).join(', ')}` }
      await $.store.set(`project:${await $.session.cwd()}`, entry.project)
      inbox = entry
    }
    await check($)
    const opened = await $.ui.open({ id: PANE, title: 'Inbox' })
    if (!inbox) return { text: problem ?? 'Sin inbox.' }

    return { text: opened.isPlaced ? `Inbox de ${inbox.project} abierto.` : statusText(inbox.project, unreadOf()) }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Button, Link, Text } = $.ui.resolve(e)
    const now = await $.clock.now()
    const C = { bg: '#000000', card: '#1c1c1e', edge: '#2c2c2e', label: '#8e8e93', text: '#ffffff', up: '#30d158', down: '#ff453a', gold: '#f0b90b', blue: '#0a84ff' }
    const pill = (key: string, text: string, color: string, bg: string) => (
      <Text key={key} color={color} backgroundColor={bg} bold>
        {` ${text} `}
      </Text>
    )
    const unread = unreadOf()
    const recent = messages.filter(m => !m.isUnread).slice(0, 3)
    const url = inbox ? `https://www.notion.so/${inbox.uuid.replace(/-/g, '')}` : undefined

    return (
      <Box flexDirection="column" gap={1} paddingX={1} paddingY={1} backgroundColor={C.bg}>
        <Box justifyContent="space-between">
          <Box gap={1}>
            <Text bold color={C.text}>
              BUZON
            </Text>
            <Text color={C.blue} bold>
              {inbox?.project ?? 'sin proyecto'}
            </Text>
            {unread.length > 0 ? pill('count', `${unread.length} por leer`, '#000000', C.gold) : pill('count', 'al dia', C.up, C.edge)}
          </Box>
          <Text color={C.label}>{checkedAt ? `revisado ${ago(new Date(checkedAt).toISOString(), now) || 'ahora'}` : ''}</Text>
        </Box>
        {problem && (
          <Box backgroundColor="#5c1010" paddingX={1}>
            <Text color={C.text}>{problem}</Text>
          </Box>
        )}

        {unread.map((m, i) => (
          <Box key={`m-${i}`} flexDirection="column" gap={1} backgroundColor={C.card} borderStyle="round" borderColor={m.expectsResponse ? C.gold : C.edge} paddingX={1}>
            <Box justifyContent="space-between">
              <Box gap={1}>
                {pill('k', m.kind === 'response' ? 'RESPUESTA' : 'MENSAJE', C.text, C.edge)}
                <Text bold color={C.text}>
                  {m.from}
                </Text>
              </Box>
              <Box gap={1}>
                {m.expectsResponse && pill('exp', 'ESPERA RESPUESTA', '#000000', C.gold)}
                <Text color={C.label}>{ago(m.date, now)}</Text>
              </Box>
            </Box>
            {m.re && <Text color={C.gold}>{m.re}</Text>}
            {m.excerpt && <Text color={C.text}>{m.excerpt}</Text>}
            <Box gap={1}>
              <Button
                key={`process-${i}`}
                label="Procesar este"
                variant="primary"
                onPress={() =>
                  ask($, `Revisa tu inbox con la skill lfp-core:agent-bridge y procesa solo el mensaje de ${m.from}${m.date ? ` del ${m.date}` : ''}${m.re ? ` sobre "${m.re}"` : ''}: actua, marcalo READ y responde si lo espera.`)
                }
              />
            </Box>
          </Box>
        ))}

        <Box gap={1}>
          {unread.length > 0 && (
            <Button key="all" label={`Procesar los ${unread.length}`} variant="primary" hotkey="0" onPress={() => ask($, "you've got mail")} />
          )}
          <Button key="refresh" label="Revisar ahora" hotkey="r" onPress={() => check($)} />
          {url && <Link key="open" href={url} label="Abrir en Notion" />}
        </Box>

        {recent.length > 0 && (
          <Box flexDirection="column">
            <Text color={C.label} bold>
              LEIDOS RECIENTES
            </Text>
            {recent.map((m, i) => (
              <Box key={`r-${i}`} gap={1}>
                <Box width={10}>
                  <Text color={C.label}>{ago(m.date, now)}</Text>
                </Box>
                <Text color={C.label} wrap="truncate">
                  {m.from}
                  {m.re ? `  -  ${m.re}` : ''}
                </Text>
              </Box>
            ))}
          </Box>
        )}
      </Box>
    )
  })
}
