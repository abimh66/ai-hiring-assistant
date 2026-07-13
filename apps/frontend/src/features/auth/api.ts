import { apiGet, apiPost } from '@/lib/api-client'
import type { TokenResponse, UserRead } from '@/features/auth/types'

export function login(email: string, password: string): Promise<TokenResponse> {
  return apiPost<TokenResponse>('/auth/login', { email, password })
}

export function getCurrentUser(): Promise<UserRead> {
  return apiGet<UserRead>('/auth/me')
}
