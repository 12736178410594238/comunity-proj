"""
댓글 모델 - 게시글의 댓글을 저장합니다
"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Comment(Base):
    __tablename__ = "comments"
    
    # 기본 키
    id = Column(Integer, primary_key=True, index=True)
    
    # 댓글 내용
    content = Column(Text, nullable=False)
    
    # 좋아요
    like_count = Column(Integer, default=0)
    
    # 삭제 여부 (soft delete)
    is_deleted = Column(Boolean, default=False)
    
    # 외래 키
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    
    # 대댓글을 위한 부모 댓글 ID (선택사항)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    
    # 시간 정보
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    
    # 대댓글 관계 (자기 참조)
    parent = relationship("Comment", remote_side=[id], backref="replies")
    
    def __repr__(self):
        return f"<Comment {self.id}>"