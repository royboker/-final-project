from pydantic import BaseModel, EmailStr, Field

from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    created_at: datetime
