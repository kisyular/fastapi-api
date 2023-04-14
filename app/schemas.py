from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from pydantic.types import conint


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    category: Optional[str] = None


class Post(PostBase):
    pass


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class PostResponse(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserResponse
    votes = []

    class Config:
        orm_mode = True


class PostWithVotes(BaseModel):
    votes: int
    Post: PostResponse

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserWithPostsResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    posts: List[PostResponse]

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    user_id: Optional[int] = None


class DeletedPostResponse(PostBase):
    id: int
    deleted_at: datetime
    owner_id: int
    owner: UserResponse

    class Config:
        orm_mode = True


# Voting Schema
class Vote(BaseModel):
    post_id: int
    # dir please restrict to 1 or 0
    dir: conint(ge=0, le=1)
