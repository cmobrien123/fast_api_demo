from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from pydantic.types import conint

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id : int
    email: EmailStr
    
    class Config:
        orm_model=True

class UserLogin(BaseModel):
    email: EmailStr
    password: str



class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass



class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    class Config:
        orm_model=True

class PostOut(BaseModel):
    Post: Post
    votes: int


class Token(BaseModel):
    access_token: str
    token_type: str
 
class TokenData(BaseModel):
    id: Optional[str] = None

class vote(BaseModel):
    post_id: int
    dir: conint(le=1)