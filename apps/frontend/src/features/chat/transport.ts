import type { ChatTransport } from 'ai'
import { API_BASE_URL } from '@/lib/api-client'
import { getAccessToken } from '@/lib/auth'
import type { HiringChatMessage } from '@/features/chat/types'
import { createSseTranslator, type Chunk } from '@/features/chat/sse'

export interface ChatRequestContext {
  /** Existing conversation to continue, or null to create a new one. */
  conversationId: number | null
  /** Narrow the chat to one hiring project, or null for global scope. */
  hiringProjectId: number | null
}

/** Pull the plain text out of a UI message (concatenate its text parts). */
function messageText(message: HiringChatMessage | undefined): string {
  if (!message) return ''
  return message.parts
    .filter((part): part is { type: 'text'; text: string } => part.type === 'text')
    .map((part) => part.text)
    .join('')
}

/**
 * Bridges the agent-backend's custom SSE protocol (`text_delta`, `tool_call`,
 * `specialist_spawned`, `tool_result`, `error`, `done`) into the AI SDK's
 * `UIMessageChunk` stream. The backend keys history by `conversation_id`, so we
 * send only the latest user turn — never the whole message array.
 */
export class HiringChatTransport implements ChatTransport<HiringChatMessage> {
  private readonly getContext: () => ChatRequestContext
  private readonly onConversationStart: (id: number) => void

  constructor(
    getContext: () => ChatRequestContext,
    onConversationStart: (id: number) => void,
  ) {
    this.getContext = getContext
    this.onConversationStart = onConversationStart
  }

  async sendMessages(
    options: Parameters<ChatTransport<HiringChatMessage>['sendMessages']>[0],
  ): Promise<ReadableStream<Chunk>> {
    const { messages, abortSignal } = options
    const lastUser = [...messages].reverse().find((m) => m.role === 'user')
    const context = this.getContext()

    const token = getAccessToken()
    let response: Response
    try {
      response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          message: messageText(lastUser),
          conversation_id: context.conversationId ?? undefined,
          hiring_project_id: context.hiringProjectId ?? undefined,
        }),
        signal: abortSignal,
      })
    } catch (error) {
      return errorStream(error instanceof Error ? error.message : 'Network error')
    }

    if (!response.ok || !response.body) {
      const detail = await response.text().catch(() => '')
      return errorStream(`Request failed (${response.status})${detail ? `: ${detail}` : ''}`)
    }

    return this.parseSse(response.body, abortSignal)
  }

  // No server-side resume support; the client always starts a fresh stream.
  async reconnectToStream(): Promise<ReadableStream<Chunk> | null> {
    return null
  }

  private parseSse(
    body: ReadableStream<Uint8Array>,
    abortSignal: AbortSignal | undefined,
  ): ReadableStream<Chunk> {
    const reader = body.getReader()
    const decoder = new TextDecoder()
    const translator = createSseTranslator(this.onConversationStart)

    return new ReadableStream<Chunk>({
      async start(controller) {
        try {
          for (;;) {
            const { done, value } = await reader.read()
            if (done) break
            for (const chunk of translator.push(decoder.decode(value, { stream: true }))) {
              controller.enqueue(chunk)
            }
          }
        } catch (error) {
          // A user-initiated stop aborts the fetch; that is not a real error.
          if (!abortSignal?.aborted) {
            const message = error instanceof Error ? error.message : 'Stream failed'
            controller.enqueue({ type: 'error', errorText: message })
          }
        } finally {
          for (const chunk of translator.flush()) controller.enqueue(chunk)
          controller.close()
        }
      },
      cancel() {
        reader.cancel().catch(() => {})
      },
    })
  }
}

function errorStream(message: string): ReadableStream<Chunk> {
  return new ReadableStream<Chunk>({
    start(controller) {
      controller.enqueue({ type: 'start' })
      controller.enqueue({ type: 'error', errorText: message })
      controller.enqueue({ type: 'finish' })
      controller.close()
    },
  })
}
