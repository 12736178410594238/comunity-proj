"""
댓글 라우터 - 댓글 CRUD
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from ..database import get_db
from ..models.user import User
from ..models.post import Post
from ..models.comment import Comment
from ..schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from ..services.auth import get_current_user

router = APIRouter(prefix="/api/posts/{post_id}/comments", tags=["댓글"])

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    댓글 작성
    """
    # 게시글 존재 확인
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다"
        )
    
    # 대댓글인 경우 부모 댓글 확인
    if comment_data.parent_id:
        parent_comment = db.query(Comment).filter(
            Comment.id == comment_data.parent_id,
            Comment.post_id == post_id
        ).first()
        if not parent_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="부모 댓글을 찾을 수 없습니다"
            )
    
    new_comment = Comment(
        content=comment_data.content,
        author_id=current_user.id,
        post_id=post_id,
        parent_id=comment_data.parent_id
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    # author 정보 로드
    db.refresh(new_comment, ["author"])
    
    return new_comment

@router.get("/", response_model=List[CommentResponse])
async def get_comments(
    post_id: int,
    db: Session = Depends(get_db)
):
    """
    게시글의 댓글 목록 조회
    """
    # 게시글 존재 확인
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다"
        )
    
    # 최상위 댓글만 가져오기 (대댓글은 replies로 포함됨)
    comments = db.query(Comment).options(
        joinedload(Comment.author),
        joinedload(Comment.replies).joinedload(Comment.author)
    ).filter(
        Comment.post_id == post_id,
        Comment.parent_id == None
    ).order_by(Comment.created_at).all()
    
    return comments

@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    post_id: int,
    comment_id: int,
    comment_update: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    댓글 수정
    """
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.post_id == post_id
    ).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="댓글을 찾을 수 없습니다"
        )
    
    # 작성자 본인만 수정 가능
    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="수정 권한이 없습니다"
        )
    
    comment.content = comment_update.content
    db.commit()
    db.refresh(comment)
    
    return comment

@router.delete("/{comment_id}")
async def delete_comment(
    post_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    댓글 삭제 (soft delete)
    """
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.post_id == post_id
    ).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="댓글을 찾을 수 없습니다"
        )
    
    # 작성자 본인 또는 관리자만 삭제 가능
    if comment.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="삭제 권한이 없습니다"
        )
    
    # Soft delete
    comment.is_deleted = True
    comment.content = "삭제된 댓글입니다."
    db.commit()
    
    return {"message": "댓글이 삭제되었습니다"}

@router.post("/{comment_id}/like")
async def like_comment(
    post_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    댓글 좋아요
    """
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.post_id == post_id
    ).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="댓글을 찾을 수 없습니다"
        )
    
    comment.like_count += 1
    db.commit()
    
    return {"message": "좋아요!", "like_count": comment.like_count}