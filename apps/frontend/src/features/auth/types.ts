export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface UserRead {
  id: number
  email: string
  full_name: string
  is_active: boolean
  is_pending: boolean
  created_at: string
}
