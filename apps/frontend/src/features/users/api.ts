import { apiDelete, apiGet, apiPost } from '@/lib/api-client'
import type { InviteUserInput, InviteUserResponse, UserRead } from '@/features/users/types'

export function listUsers(): Promise<UserRead[]> {
  return apiGet<UserRead[]>('/users')
}

export function inviteUser(input: InviteUserInput): Promise<InviteUserResponse> {
  return apiPost<InviteUserResponse>('/users/invite', input)
}

export function deactivateUser(id: number): Promise<UserRead> {
  return apiDelete<UserRead>(`/users/${id}`)
}
