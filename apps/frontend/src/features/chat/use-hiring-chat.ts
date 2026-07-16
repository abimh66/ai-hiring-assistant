import { useEffect, useMemo, useRef } from 'react'
import { useChat } from '@ai-sdk/react'
import { useNavigate } from '@tanstack/react-router'
import { useQueryClient } from '@tanstack/react-query'
import { getConversation } from '@/features/chat/api'
import { HiringChatTransport } from '@/features/chat/transport'
import type {
  ActivityData,
  ChatMessageRead,
  HiringChatMessage,
  StoredActivity,
} from '@/features/chat/types'

function storedToActivity(entry: StoredActivity): ActivityData {
  if (entry.type === 'specialist_spawned') {
    return { kind: 'specialist', topic: entry.topic ?? 'specialist' }
  }
  if (entry.type === 'tool_result') {
    return { kind: 'tool_result', tool: entry.tool ?? 'tool', status: entry.status ?? 'ok' }
  }
  return { kind: 'tool_call', tool: entry.tool ?? 'tool' }
}

function toUIMessage(message: ChatMessageRead): HiringChatMessage {
  return {
    id: String(message.id),
    role: message.role,
    parts: [
      ...(message.activity ?? []).map((entry) => ({
        type: 'data-activity' as const,
        data: storedToActivity(entry),
      })),
      ...(message.content ? [{ type: 'text' as const, text: message.content }] : []),
    ],
  }
}

interface UseHiringChatOptions {
  /** Conversation to continue (from the URL), or null for a fresh chat. */
  conversationId: number | null
  /** Hiring project scope, or null for global. */
  hiringProjectId: number | null
}

export function useHiringChat({ conversationId, hiringProjectId }: UseHiringChatOptions) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const conversationIdRef = useRef<number | null>(conversationId)
  const hiringProjectIdRef = useRef<number | null>(hiringProjectId)
  hiringProjectIdRef.current = hiringProjectId

  const transport = useMemo(
    () =>
      new HiringChatTransport(
        () => ({
          conversationId: conversationIdRef.current,
          hiringProjectId: hiringProjectIdRef.current,
        }),
        (id) => {
          const wasNew = conversationIdRef.current == null
          conversationIdRef.current = id
          queryClient.invalidateQueries({ queryKey: ['chat', 'conversations'] })
          if (wasNew) {
            void navigate({
              to: '/chat',
              search: (prev) => ({ ...prev, conversation: id }),
              replace: true,
            })
          }
        },
      ),
    // Reads current values through refs, so it never needs to be rebuilt.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  )

  const chat = useChat<HiringChatMessage>({ transport })
  const { status, setMessages } = chat

  // Load (or clear) messages when the selected conversation changes externally
  // — e.g. picking one in the sidebar or hitting "New chat". Never while a turn
  // is in flight, so a just-created conversation's stream is not clobbered.
  useEffect(() => {
    if (conversationId === conversationIdRef.current) return
    if (status === 'streaming' || status === 'submitted') return

    if (conversationId == null) {
      conversationIdRef.current = null
      setMessages([])
      return
    }

    let cancelled = false
    getConversation(conversationId)
      .then((detail) => {
        if (cancelled) return
        conversationIdRef.current = conversationId
        setMessages(detail.messages.map(toUIMessage))
      })
      .catch(() => {})
    return () => {
      cancelled = true
    }
  }, [conversationId, status, setMessages])

  return chat
}
