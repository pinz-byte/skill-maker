import type { EngineInterface, Register } from 'claude-code'

// CLAUDE.md "auto seed" rule: at ~70% context, generate a continuity seed without being asked.
export const WARN_AT = 70
const SNOOZE_STEP = 15

let machine: string | undefined
let project = ''
let branch: string | undefined
let pct: number | undefined
let warnAt = WARN_AT

// "LFP-M2" -> "M2"; any other name is shown as it is.
export const shortMachine = (name: string) => {
  const m = name.match(/(?:^|[^A-Za-z0-9])M(\d)(?![0-9])/i)
  return m ? `M${m[1]}` : name.trim()
}

export const basename = (path: string) => path.replace(/\/+$/, '').split('/').pop() ?? path

export const contextPercent = (context: { percent?: number; tokens?: number; window: number }) =>
  context.percent ?? (context.tokens != null && context.window > 0 ? (context.tokens / context.window) * 100 : undefined)

export const compassLine = (parts: { machine?: string; project: string; branch?: string; pct?: number }) =>
  [parts.machine, parts.project, parts.branch, parts.pct != null ? `contexto ${Math.round(parts.pct)}%` : undefined]
    .filter(Boolean)
    .join(' | ')

const run = async ($: EngineInterface, argv: string[]) => {
  try {
    const out = await $.process.run(argv, { timeoutMs: 5000 })
    return out.exitCode === 0 ? out.stdout.trim() || undefined : undefined
  } catch {
    return undefined
  }
}

const refresh = async ($: EngineInterface) => {
  const usage = await $.session.usage().catch(() => undefined)
  pct = usage ? contextPercent(usage.context) : pct
  branch = await run($, ['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
  $.ui.status(compassLine({ machine, project, branch, pct }))
  $.ui.invalidate('ui.render')
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const name = (await run($, ['scutil', '--get', 'ComputerName'])) ?? (await run($, ['hostname', '-s']))
    machine = name ? shortMachine(name) : undefined
    project = basename(await $.session.cwd())
    await refresh($)

    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    await refresh($)

    return result
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey || pct == null || pct < warnAt) return next(e)
    const { Box, Button, Text } = $.ui.resolve(e)
    const snooze = () => {
      warnAt = Math.min(100, Math.max(warnAt, Math.round(pct ?? 0)) + SNOOZE_STEP)
      $.ui.invalidate('ui.render')
    }

    return (
      <Box backgroundColor="#1c1c1e" paddingX={1} justifyContent="space-between" alignItems="center">
        <Text color="#f0b90b" bold>
          Contexto al {Math.round(pct)}%: guarda la continuity seed antes de seguir.
        </Text>
        <Box gap={1}>
          <Button
            key="seed"
            label="Generar seed"
            variant="primary"
            hotkey="s"
            onPress={() => {
              snooze()
              $.clock.after(0, () =>
                $.prompt.submit({
                  text: 'Genera ahora la continuity seed de esta sesion con la skill lfp-core:continuity-seed, incluido el Mount Manifest, y dime donde quedo guardada.',
                }),
              )
            }}
          />
          <Button key="later" label="Mas tarde" dimColor onPress={snooze} />
        </Box>
      </Box>
    )
  })
}
