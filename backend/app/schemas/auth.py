from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=1, description="Full name is required")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ResetPassword(BaseModel):
    email: EmailStr

class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int

class UserProfile(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None

    class Config:
        from_attributes = True
