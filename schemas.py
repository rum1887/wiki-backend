from pydantic import BaseModel, EmailStr
from typing import List, Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True

class UserInDB(UserResponse):
    hashed_password: str

class TagSchema(BaseModel):
    id: Optional[int] = None
    tag_name: str

    class Config:
        from_attributes = True

class WikiArticleSchema(BaseModel):
    id: Optional[int] = None  # Allow it to be optional for creation
    title: str
    url: str
    summary: str
    tags: Optional[List[TagSchema]] = [] 

    class Config:
        from_attributes = True

class SavedArticleSchema(BaseModel):
    id: Optional[int] = None 
    user_id: int  
    article: WikiArticleSchema 
    tags: Optional[List[TagSchema]] = []  

    class Config:
        from_attributes = True

    