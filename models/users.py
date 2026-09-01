from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)
from datetime import datetime
class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: str | None = None
    password: str = Field(min_length=6)

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone: str | None = None
    photo_path: str | None = None
    created_at: datetime

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    password: str | None = None