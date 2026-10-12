export type Seat = {
  key: string
  label: string
  skill: string
  role: string
  color: string
  hotkey: string
}

// working/done/error: the seat ran in the pane. chat/chat-done: Claude used the skill in the chat.
export type RunStatus = 'working' | 'done' | 'error' | 'chat' | 'chat-done'

export type Run = {
  status: RunStatus
  startedAt: number
  endedAt?: number
  text?: string
  focus?: string
}
