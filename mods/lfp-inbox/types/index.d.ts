export type InboxEntry = { project: string; host: string; uuid: string }

export type Message = {
  kind: 'message' | 'response'
  from: string
  to?: string
  date?: string
  re?: string
  isUnread: boolean
  expectsResponse: boolean
  excerpt: string
}
