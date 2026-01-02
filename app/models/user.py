"""
사용자 모델 - 회원 정보를 저장합니다
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class User(Base):
    __tablename__ = "users"  # 테이블 이름
    
    # 기본 키 (자동 증가)
    id = Column(Integer, primary_key=True, index=True)
    
    # 사용자 정보
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # 프로필 정보
    nickname = Column(String(50), nullable=True)
    profile_image = Column(String(255), nullable=True)
    bio = Column(String(500), nullable=True)  # 자기소개
    
    # 계정 상태
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # 시간 정보
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정 (사용자가 작성한 게시글, 댓글)
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username}>"