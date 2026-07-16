import { useEffect, useRef } from 'react'
import { cn } from '@/lib/utils'
import type { ActivityData, HiringChatMessage } from '@/features/chat/types'
import { ActivityTrail } from '@/features/chat/components/activity-trail'

function MessageBubble({ message }: { message: HiringChatMessage }) {
  const isUser = message.role === 'user'

  const activity: ActivityData[] = []
  let text = ''
  for (const part of message.parts) {
    if (part.type === 'text') text += part.text
    else if (part.type === 'data-activity') activity.push(part.data)
  }

  return (
    <div className={cn('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={cn(
          'max-w-[85%] rounded-lg px-4 py-2.5 text-sm',
          isUser ? 'bg-primary text-primary-foreground' : 'bg-muted',
        )}
      >
        {!isUser && <ActivityTrail items={activity} />}
        {text ? (
          <div className="whitespace-pre-wrap break-words">{text}</div>
        ) : (
          !isUser && activity.length === 0 && (
            <span className="text-muted-foreground">Thinking…</span>
          )
        )}
      </div>
    </div>
  )
}

export function MessageList({
  messages,
  isStreaming,
}: {
  messages: HiringChatMessage[]
  isStreaming: boolean
}) {
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isStreaming])

  return (
    <div className="flex flex-col gap-4">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      <div ref={endRef} />
    </div>
  )
}
