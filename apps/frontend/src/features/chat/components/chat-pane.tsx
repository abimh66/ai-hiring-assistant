import { useHiringChat } from '@/features/chat/use-hiring-chat'
import { MessageList } from '@/features/chat/components/message-list'
import { Composer } from '@/features/chat/components/composer'

const EXAMPLE_PROMPTS = [
  'Which candidates have backend experience?',
  'Why was the top candidate shortlisted?',
  'Compare the two strongest candidates in detail.',
]

export function ChatPane({
  conversationId,
  hiringProjectId,
}: {
  conversationId: number | null
  hiringProjectId: number | null
}) {
  const { messages, sendMessage, stop, status, error } = useHiringChat({
    conversationId,
    hiringProjectId,
  })

  const isBusy = status === 'submitted' || status === 'streaming'

  function send(text: string) {
    void sendMessage({ text })
  }

  return (
    <div className="flex h-full flex-1 flex-col gap-4">
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
            <div>
              <h2 className="text-lg font-semibold">Hiring assistant</h2>
              <p className="text-sm text-muted-foreground">
                Ask about candidates, match analyses, and shortlists.
              </p>
            </div>
            <div className="flex flex-col gap-2">
              {EXAMPLE_PROMPTS.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  onClick={() => send(prompt)}
                  className="rounded-lg border px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <MessageList messages={messages} isStreaming={isBusy} />
        )}
      </div>

      {error && (
        <p className="text-sm text-destructive">
          Something went wrong: {error.message}
        </p>
      )}

      <Composer onSend={send} onStop={() => void stop()} isBusy={isBusy} />
    </div>
  )
}
