export type Seat = { key: string; label: string; skill: string; hotkey: string }

declare module 'claude-code' {
  interface PluginState {
    'lfp-roundtable': { topic: string }
  }
}
