"""
댓글 스키마
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# 댓글 작성
class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="댓글 내용")
    parent_id: Optional[int] = Field(None, description="대댓글인 경우 부모 댓글 ID")

# 댓글 수정
class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

# 댓글 작성자 정보
class CommentAuthor(BaseModel):
    id: int
    username: str
    nickname: Optional[str]
    
    class Config:
        from_attributes = True

# 댓글 응답
class CommentResponse(BaseModel):
    id: int
    content: str
    like_count: int
    is_deleted: bool
    author_id: int
    post_id: int
    parent_id: Optional[int]
    author: CommentAuthor
    created_at: datetime
    updated_at: datetime
    replies: List["CommentResponse"] = []
    
    class Config:
        from_attributes = True

# 순환 참조 해결
CommentResponse.model_rebuild()