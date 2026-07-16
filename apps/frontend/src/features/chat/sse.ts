import type { UIMessageChunk } from 'ai'
import type { ChatDataParts, ChatMetadata } from '@/features/chat/types'

export type Chunk = UIMessageChunk<ChatMetadata, ChatDataParts>

const TEXT_ID = 'response'

/**
 * Stateful translator from the agent-backend SSE protocol to AI SDK
 * `UIMessageChunk`s. Kept free of app imports so it can be unit-tested directly.
 *
 * Usage: feed raw decoded text via `push()` (any chunking is fine — it buffers
 * across `\n\n` frame boundaries), then call `flush()` once the stream ends.
 */
export function createSseTranslator(onConversationStart: (id: number) => void) {
  let buffer = ''
  let textOpen = false

  function handleFrame(frame: string, out: Chunk[]) {
    let event = ''
    let dataLine = ''
    for (const line of frame.split('\n')) {
      if (line.startsWith('event:')) event = line.slice(6).trim()
      else if (line.startsWith('data:')) dataLine += line.slice(5).trim()
    }
    if (!event) return

    let data: Record<string, unknown> = {}
    if (dataLine) {
      try {
        data = JSON.parse(dataLine)
      } catch {
        return // skip malformed frame rather than killing the turn
      }
    }

    switch (event) {
      case 'message_start': {
        const id = data.conversation_id
        if (typeof id === 'number') onConversationStart(id)
        out.push({
          type: 'start',
          messageMetadata: typeof id === 'number' ? { conversationId: id } : undefined,
        })
        break
      }
      case 'text_delta': {
        if (!textOpen) {
          out.push({ type: 'text-start', id: TEXT_ID })
          textOpen = true
        }
        out.push({ type: 'text-delta', id: TEXT_ID, delta: String(data.text ?? '') })
        break
      }
      case 'tool_call':
        out.push({ type: 'data-activity', data: { kind: 'tool_call', tool: String(data.tool ?? 'tool') } })
        break
      case 'specialist_spawned':
        out.push({ type: 'data-activity', data: { kind: 'specialist', topic: String(data.topic ?? 'specialist') } })
        break
      case 'tool_result':
        out.push({
          type: 'data-activity',
          data: {
            kind: 'tool_result',
            tool: String(data.tool ?? 'tool'),
            status: String(data.status ?? 'ok'),
          },
        })
        break
      case 'error':
        out.push({ type: 'error', errorText: String(data.message ?? 'Assistant error') })
        break
      case 'done':
        if (textOpen) {
          out.push({ type: 'text-end', id: TEXT_ID })
          textOpen = false
        }
        out.push({ type: 'finish' })
        break
    }
  }

  return {
    /** Feed decoded text; returns any chunks completed by full frames so far. */
    push(text: string): Chunk[] {
      buffer += text
      const frames = buffer.split('\n\n')
      buffer = frames.pop() ?? ''
      const out: Chunk[] = []
      for (const frame of frames) {
        if (frame.trim()) handleFrame(frame, out)
      }
      return out
    },
    /** Call once the stream ends: flushes a trailing frame and closes open text. */
    flush(): Chunk[] {
      const out: Chunk[] = []
      if (buffer.trim()) handleFrame(buffer, out)
      buffer = ''
      if (textOpen) {
        out.push({ type: 'text-end', id: TEXT_ID })
        textOpen = false
      }
      return out
    },
  }
}
