from pydantic import BaseModel, Field
from datetime import datetime

class TagResponse(BaseModel):
    id: int
    name: str

class NewsResponse(BaseModel):
    id: int
    title: str
    subtitle: str | None = None
    text: str
    image_path: str | None = None
    author: "UserResponse"
    tags: list[TagResponse]
    created_at: datetime
    comments_count: int = Field(default=0)

class Body_create_news_api_news_post(BaseModel):
    title: str
    subtitle: str | None = None
    text: str
    tags: str | None = None
    image: str | None = None

