export interface UserRead {
  id: number
  email: string
  full_name: string
  is_active: boolean
  is_pending: boolean
  created_at: string
}

export interface InviteUserInput {
  email: string
  full_name: string
}

export interface InviteUserResponse {
  user: UserRead
  invite_token: string
}
