import type { Register } from 'claude-code'

import type { Seat } from '../types'

const PANE = 'roundtable'
const topic = { plugin: 'lfp-roundtable', key: 'topic' } as const

export const SEATS: Seat[] = [
  { key: 'critical', label: 'Critical', skill: 'lfp-thinkers:critical-thinker', hotkey: '1' },
  { key: 'creative', label: 'Creative', skill: 'lfp-thinkers:creative-thinker', hotkey: '2' },
  { key: 'logic', label: 'Logic', skill: 'lfp-thinkers:logic-thinker', hotkey: '3' },
  { key: 'loop', label: 'Loop-breaker', skill: 'lfp-thinkers:loop-breaker', hotkey: '4' },
  { key: 'ceo', label: 'CEO planner', skill: 'lfp-thinkers:ceo-planner', hotkey: '5' },
  { key: 'toolbox', label: 'Toolbox', skill: 'lfp-thinkers:toolbox', hotkey: '6' },
]

// A plain prompt naming the skill: prompt.submit refuses text that starts with '/'.
export const convene = (seat: Seat, subject: string) =>
  `Use the ${seat.skill} skill on: ${subject.trim() || 'the current discussion'}`

const USAGE = `/roundtable <seat> [topic], seats: ${SEATS.map(s => s.key).join(', ')}`

// "/roundtable logic the publish loop" -> the logic seat on that topic; undefined when no seat matches.
export const parse = (args: string) => {
  const [word = '', ...rest] = args.trim().split(/\s+/)
  const seat = SEATS.find(s => s.key === word.toLowerCase())

  return seat && { seat, subject: rest.join(' ') }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'roundtable',
      description: 'Open the thinkers roundtable pane, or convene one seat directly',
      argumentHint: '[seat] [topic]',
    })

    return next(e)
  })

  on('command.run', { command: 'roundtable' }, async ($, e) => {
    if (e.args.trim()) {
      const picked = parse(e.args)
      if (!picked) return { text: `Unknown seat. ${USAGE}` }
      // Submitting from command.run would wait on the turn this hook holds; a timer runs it after.
      $.clock.after(0, () => $.prompt.submit({ text: convene(picked.seat, picked.subject) }))

      return { text: `Convening ${picked.seat.label}.` }
    }

    const opened = await $.ui.open({ id: PANE, title: 'Roundtable' })

    // Where it went: a session can be drawn on several surfaces (e.g. viewed from another machine).
    const surfaces = (await $.session.surfaces().catch(() => [])).join(', ') || 'none'
    const pane = (await $.ui.panes().catch(() => [])).find(p => p.id === PANE)

    return {
      text: opened.isPlaced
        ? `Roundtable pane opened (surfaces: ${surfaces}; shown: ${pane?.isShown ?? 'unknown'}). Or use ${USAGE}`
        : `Pane not shown here (${opened.reason}; surfaces: ${surfaces}). Use ${USAGE}`,
    }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const els = $.ui.resolve(e)
    const { Box, Button, Text } = els
    // Mobile has no Input: there the seats take the current discussion.
    const Input = 'Input' in els ? els.Input : undefined
    const { value: subject = '' } = await $.state.get(topic)
    const setTopic = (value: string) => $.state.set(topic, value)

    return (
      <Box flexDirection="column" gap={1}>
        {Input && (
          <Input
            key="topic"
            label="Topic"
            placeholder="blank = the current discussion"
            value={subject}
            onInput={setTopic}
            onSubmit={setTopic}
          />
        )}
        <Box flexDirection="column">
          {SEATS.map(seat => (
            <Button
              key={seat.key}
              label={seat.label}
              hotkey={seat.hotkey}
              onPress={async () => {
                const { value = '' } = await $.state.get(topic)
                await $.prompt.submit({ text: convene(seat, value) })
                $.ui.toast(`Roundtable: ${seat.label} convened`)
              }}
            />
          ))}
        </Box>
        <Text dimColor>Each seat runs as its own turn once Claude is idle.</Text>
      </Box>
    )
  })
}
