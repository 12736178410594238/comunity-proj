"""
게시글 스키마
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# 게시글 작성
class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="제목")
    content: str = Field(..., min_length=1, description="내용")
    category: str = Field(default="자유게시판", description="카테고리")

# 게시글 수정
class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = None

# 작성자 정보 (게시글에 포함)
class AuthorInfo(BaseModel):
    id: int
    username: str
    nickname: Optional[str]
    
    class Config:
        from_attributes = True

# 게시글 응답
class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    view_count: int
    like_count: int
    is_published: bool
    is_pinned: bool
    author_id: int
    author: AuthorInfo
    created_at: datetime
    updated_at: datetime
    comment_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

# 게시글 목록 (간단한 정보만)
class PostList(BaseModel):
    id: int
    title: str
    category: str
    view_count: int
    like_count: int
    author: AuthorInfo
    created_at: datetime
    comment_count: int = 0
    
    class Config:
        from_attributes = True