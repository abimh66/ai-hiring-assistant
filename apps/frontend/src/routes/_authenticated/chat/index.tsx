import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { ChatPane } from '@/features/chat/components/chat-pane'
import { ConversationSidebar } from '@/features/chat/components/conversation-sidebar'
import { ProjectScopePicker } from '@/features/chat/components/project-scope-picker'

interface ChatSearch {
  conversation?: number
  project?: number
}

export const Route = createFileRoute('/_authenticated/chat/')({
  validateSearch: (search: Record<string, unknown>): ChatSearch => ({
    conversation: typeof search.conversation === 'number' ? search.conversation : undefined,
    project: typeof search.project === 'number' ? search.project : undefined,
  }),
  component: ChatPage,
})

function ChatPage() {
  const { conversation, project } = Route.useSearch()
  const navigate = useNavigate()

  const conversationId = conversation ?? null
  const hiringProjectId = project ?? null

  function changeScope(next: number | null) {
    // Switching scope starts a fresh conversation so history stays project-consistent.
    void navigate({
      to: '/chat',
      search: { project: next ?? undefined, conversation: undefined },
    })
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      <ConversationSidebar hiringProjectId={hiringProjectId} activeConversationId={conversationId} />
      <div className="flex flex-1 flex-col gap-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold">Assistant</h1>
          <ProjectScopePicker value={hiringProjectId} onChange={changeScope} />
        </div>
        <ChatPane conversationId={conversationId} hiringProjectId={hiringProjectId} />
      </div>
    </div>
  )
}
