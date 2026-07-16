import { useState } from 'react'
import { Link, useNavigate } from '@tanstack/react-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { deleteConversation, listConversations } from '@/features/chat/api'

export function ConversationSidebar({
  hiringProjectId,
  activeConversationId,
}: {
  hiringProjectId: number | null
  activeConversationId: number | null
}) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [pendingDelete, setPendingDelete] = useState<number | null>(null)

  const { data: conversations } = useQuery({
    queryKey: ['chat', 'conversations', hiringProjectId ?? 'all'],
    queryFn: () => listConversations(hiringProjectId),
  })

  const removeMutation = useMutation({
    mutationFn: (id: number) => deleteConversation(id),
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: ['chat', 'conversations'] })
      setPendingDelete(null)
      if (id === activeConversationId) {
        void navigate({ to: '/chat', search: (prev) => ({ ...prev, conversation: undefined }) })
      }
    },
  })

  return (
    <div className="flex w-60 shrink-0 flex-col gap-2 border-r pr-4">
      <Button
        variant="outline"
        size="sm"
        className="justify-start"
        render={
          <Link to="/chat" search={(prev) => ({ ...prev, conversation: undefined })}>
            <Plus />
            <span>New chat</span>
          </Link>
        }
      />

      <div className="flex flex-col gap-0.5 overflow-y-auto">
        {conversations?.length === 0 && (
          <p className="px-2 py-4 text-xs text-muted-foreground">No conversations yet.</p>
        )}
        {conversations?.map((conversation) => (
          <div
            key={conversation.id}
            className={cn(
              'group flex items-center gap-1 rounded-md px-2 py-1.5 text-sm hover:bg-accent',
              conversation.id === activeConversationId && 'bg-accent',
            )}
          >
            <Link
              to="/chat"
              search={(prev) => ({ ...prev, conversation: conversation.id })}
              className="line-clamp-1 flex-1"
              title={conversation.title}
            >
              {conversation.title}
            </Link>
            <button
              type="button"
              onClick={() => setPendingDelete(conversation.id)}
              className="shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100 hover:text-destructive"
              aria-label="Delete conversation"
            >
              <Trash2 className="size-3.5" />
            </button>
          </div>
        ))}
      </div>

      <Dialog open={pendingDelete !== null} onOpenChange={(open) => !open && setPendingDelete(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete conversation?</DialogTitle>
            <DialogDescription>This permanently removes the conversation and its messages.</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setPendingDelete(null)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              disabled={removeMutation.isPending}
              onClick={() => pendingDelete !== null && removeMutation.mutate(pendingDelete)}
            >
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
