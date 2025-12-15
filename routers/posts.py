"""
게시글 라우터 - 게시글 CRUD
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func
from typing import List, Optional

from ..database import get_db
from ..models.user import User
from ..models.post import Post
from ..models.comment import Comment
from ..schemas.post import PostCreate, PostUpdate, PostResponse, PostList
from ..services.auth import get_current_user, get_current_user_optional

router = APIRouter(prefix="/api/posts", tags=["게시글"])

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    게시글 작성
    """
    new_post = Post(
        title=post_data.title,
        content=post_data.content,
        category=post_data.category,
        author_id=current_user.id
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    # 댓글 수 추가
    new_post.comment_count = 0
    
    return new_post

@router.get("/", response_model=List[PostList])
async def get_posts(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(20, ge=1, le=100, description="가져올 개수"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    search: Optional[str] = Query(None, description="검색어 (제목, 내용)"),
    db: Session = Depends(get_db)
):
    """
    게시글 목록 조회
    
    - skip: 페이지네이션 (건너뛸 개수)
    - limit: 한 페이지에 가져올 개수
    - category: 카테고리 필터
    - search: 제목/내용 검색
    """
    query = db.query(Post).filter(Post.is_published == True)
    
    # 카테고리 필터
    if category:
        query = query.filter(Post.category == category)
    
    # 검색
    if search:
        query = query.filter(
            (Post.title.contains(search)) | (Post.content.contains(search))
        )
    
    # 공지사항 먼저, 그 다음 최신순
    query = query.order_by(desc(Post.is_pinned), desc(Post.created_at))
    
    posts = query.options(joinedload(Post.author)).offset(skip).limit(limit).all()
    
    # 댓글 수 추가
    for post in posts:
        post.comment_count = db.query(func.count(Comment.id)).filter(
            Comment.post_id == post.id,
            Comment.is_deleted == False
        ).scalar()
    
    return posts

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    게시글 상세 조회
    """
    post = db.query(Post).options(joinedload(Post.author)).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다"
        )
    
    if not post.is_published and (not current_user or post.author_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다"
        )
    
    # 조회수 증가
    post.view_count += 1
    db.commit()
    
    # 댓글 수 추가
    post.comment_count = db.query(func.count(Comment.id)).filter(
        Comment.post_id == post.id,
        Comment.is_deleted == False
    ).scalar()
    
    return post

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    게시글 수정
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다"
        )
    
    # 작성자 본인 또는 관리자만 수정 가능
    if post.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="수정 권한이 없습니다"
        )
    
    # 업데이트
    if post_update.title is not None:
        post.title = post_update.title
    if post_update.content is not None:
        post.content = post_update.content
    if post_update.category is not None:
        post.category = post_update.category
    
    db.commit()
    db.refresh(post)
    
    return post

@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    게시글 삭제
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다"
        )
    
    # 작성자 본인 또는 관리자만 삭제 가능
    if post.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="삭제 권한이 없습니다"
        )
    
    db.delete(post)
    db.commit()
    
    return {"message": "게시글이 삭제되었습니다"}

@router.post("/{post_id}/like")
async def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    게시글 좋아요
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다"
        )
    
    post.like_count += 1
    db.commit()
    
    return {"message": "좋아요!", "like_count": post.like_count}

@router.get("/categories/list")
async def get_categories():
    """
    카테고리 목록
    """
    return {
        "categories": [
            "자유게시판",
            "질문게시판",
            "정보공유",
            "후기/리뷰",
            "공지사항"
        ]
    }