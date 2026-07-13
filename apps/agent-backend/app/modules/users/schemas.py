from pydantic import BaseModel, EmailStr

from app.modules.auth.schemas import UserRead


class InviteUserRequest(BaseModel):
    email: EmailStr
    full_name: str


class InviteUserResponse(BaseModel):
    user: UserRead
    invite_token: str
