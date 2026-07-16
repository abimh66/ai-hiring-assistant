import { apiDelete, apiGet } from '@/lib/api-client'
import type { ConversationDetail, ConversationListItem } from '@/features/chat/types'

export function listConversations(hiringProjectId?: number | null): Promise<ConversationListItem[]> {
  const query = hiringProjectId != null ? `?hiring_project_id=${hiringProjectId}` : ''
  return apiGet<ConversationListItem[]>(`/chat/conversations${query}`)
}

export function getConversation(id: number): Promise<ConversationDetail> {
  return apiGet<ConversationDetail>(`/chat/conversations/${id}`)
}

export function deleteConversation(id: number): Promise<void> {
  return apiDelete<void>(`/chat/conversations/${id}`)
}
