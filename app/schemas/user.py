"""
사용자 스키마 - API 요청/응답 데이터 검증
"""
from typing import Optional, Annotated
from pydantic import BaseModel, EmailStr, Field
from fastapi import Form
from datetime import datetime

# 회원가입 요청
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="사용자 ID")
    email: EmailStr = Field(..., description="이메일 주소")
    password: str = Field(..., min_length=6, description="비밀번호 (최소 6자)")
    nickname: Optional[str] = Field(None, max_length=50, description="닉네임")

    @classmethod
    def as_form(
        cls,
        username: str = Form(...),
        email: EmailStr = Form(...),
        password: str = Form(...),
        nickname: Optional[str] = Form(None),
    ):
        return cls(username=username, email=email, password=password, nickname=nickname)

# 로그인 요청
class UserLogin(BaseModel):
    username: str
    password: str

# 사용자 정보 수정
class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None

# 사용자 정보 응답
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    nickname: Optional[str]
    bio: Optional[str]
    profile_image: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # ORM 모드 활성화

# 토큰 응답
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# 토큰 데이터 (내부 사용)
class TokenData(BaseModel):
    username: Optional[str] = None