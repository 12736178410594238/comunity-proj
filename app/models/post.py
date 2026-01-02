"""
게시글 모델 - 커뮤니티 게시글을 저장합니다
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Post(Base):
    __tablename__ = "posts"
    
    # 기본 키
    id = Column(Integer, primary_key=True, index=True)
    
    # 게시글 내용
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    # 카테고리 (자유게시판, 질문게시판 등)
    category = Column(String(50), default="자유게시판")
    
    # 조회수, 좋아요
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    
    # 상태
    is_published = Column(Boolean, default=True)
    is_pinned = Column(Boolean, default=False)  # 공지사항 고정
    
    # 작성자 (외래 키)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 시간 정보
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Post {self.title}>"