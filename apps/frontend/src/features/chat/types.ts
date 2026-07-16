import type { UIMessage } from 'ai'

/** Assistant "activity" events surfaced inline, mirroring the backend SSE protocol. */
export type ActivityData =
  | { kind: 'tool_call'; tool: string }
  | { kind: 'specialist'; topic: string }
  | { kind: 'tool_result'; tool: string; status: string }

/** Custom data-part map for our UI messages (rendered as `data-activity` parts). */
export type ChatDataParts = {
  activity: ActivityData
}

/** Per-message metadata carried on the `start` chunk. */
export type ChatMetadata = {
  conversationId?: number
}

export type HiringChatMessage = UIMessage<ChatMetadata, ChatDataParts>

// --- REST projections (mirror agent-backend app/modules/chat/schemas.py) ---

export type ChatRole = 'user' | 'assistant'

export interface ConversationListItem {
  id: number
  hiring_project_id: number | null
  title: string
  created_at: string
  updated_at: string
}

/** Persisted activity entry: the SSE event data with a `type` discriminator. */
export interface StoredActivity {
  type: 'tool_call' | 'specialist_spawned' | 'tool_result'
  tool?: string
  topic?: string
  status?: string
}

export interface ChatMessageRead {
  id: number
  role: ChatRole
  content: string
  activity: StoredActivity[] | null
  created_at: string
}

export interface ConversationDetail extends ConversationListItem {
  messages: ChatMessageRead[]
}
