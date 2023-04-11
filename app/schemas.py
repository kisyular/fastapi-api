from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None
    category: Optional[str] = None


class Post(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
