from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    UploadFile
)
from datetime import datetime
class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: str | None
    password: str = Field(min_length=6)

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone: str | None
    photo_path: str | None
    created_at: datetime

class UserUpdate(BaseModel):
    email: EmailStr | None
    first_name: str | None
    last_name: str | None
    phone: str | None
    password: str | None

class Body_upload_photo_api_users_me_photo_post(BaseModel):
    photo: UploadFile