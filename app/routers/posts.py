"""
게시판 페이지 및 데이터 라우터
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func
from typing import List, Optional

from ..database import get_db
from ..models.user import User
from ..models.post import Post
from ..models.comment import Comment
from ..schemas.post import PostCreate, PostUpdate
from ..services.auth import get_current_user, get_current_user_optional

# --- HTML 페이지 렌더링을 위한 설정 ---
templates = Jinja2Templates(directory="app/templates")
# 페이지를 서빙하는 라우터
page_router = APIRouter(tags=["게시판 페이지"])
# 기존 API 기능을 위한 라우터
api_router = APIRouter(prefix="/api/posts", tags=["게시글 API"])

# --- 페이지 렌더링 라우트 ---

@page_router.get("/")
async def render_home_page(request: Request, db: Session = Depends(get_db)):
    """
    메인 홈페이지 렌더링 (최신글 포함)
    """
    recent_posts = db.query(Post).filter(Post.is_published == True)\
                                 .order_by(desc(Post.is_pinned), desc(Post.created_at))\
                                 .options(joinedload(Post.author))\
                                 .limit(5).all()
    
    for post in recent_posts:
        post.comment_count = db.query(func.count(Comment.id)).filter(
            Comment.post_id == post.id, Comment.is_deleted == False
        ).scalar() or 0

    return templates.TemplateResponse("index.html", {
        "request": request,
        "posts": recent_posts,
        "current_user": getattr(request.state, "user", None)
    })
    
@page_router.get("/posts")
async def render_posts_page(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    게시글 목록 페이지 렌더링
    """
    query = db.query(Post).filter(Post.is_published == True)
    if category:
        query = query.filter(Post.category == category)
    if search:
        query = query.filter(
            (Post.title.contains(search)) | (Post.content.contains(search))
        )
    
    posts = query.order_by(desc(Post.is_pinned), desc(Post.created_at))\
                 .options(joinedload(Post.author))\
                 .offset(skip).limit(limit).all()

    for post in posts:
        post.comment_count = db.query(func.count(Comment.id)).filter(
            Comment.post_id == post.id, Comment.is_deleted == False
        ).scalar() or 0

    return templates.TemplateResponse("post.html", {
        "request": request,
        "posts": posts,
        "current_user": request.state.user  # 미들웨어에서 설정된 사용자 정보
    })

@page_router.get("/posts/new")
async def render_create_post_form(request: Request, current_user: User = Depends(get_current_user)):
    """
    게시글 작성 폼 페이지
    """
    return templates.TemplateResponse("creat_post.html", {"request": request, "current_user": current_user})

@page_router.get("/posts/{post_id}")
async def render_post_detail_page(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db)
):
    """
    게시글 상세 페이지 렌더링
    """
    post = db.query(Post).options(joinedload(Post.author)).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    # 비공개 글 처리
    if not post.is_published and (not request.state.user or post.author_id != request.state.user.id):
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    # 조회수 증가
    post.view_count += 1
    db.commit()

    # 댓글 로드
    comments = db.query(Comment).options(joinedload(Comment.author))\
                                .filter(Comment.post_id == post_id, Comment.is_deleted == False)\
                                .order_by(Comment.created_at.asc()).all()

    return templates.TemplateResponse("post_detail.html", {
        "request": request,
        "post": post,
        "comments": comments,
        "current_user": request.state.user
    })

# --- 데이터 처리 API 라우트 ---

@api_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form("자유게시판"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    게시글 작성 (폼 제출)
    """
    new_post = Post(
        title=title,
        content=content,
        category=category,
        author_id=current_user.id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    # 생성 후 상세 페이지로 리다이렉트
    return RedirectResponse(url=f"/posts/{new_post.id}", status_code=status.HTTP_303_SEE_OTHER)

@api_router.put("/{post_id}")
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # (이하 로직은 기존과 유사하게 유지)
    ...

@api_router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # (이하 로직은 기존과 유사하게 유지)
    ...
    
# 라우터를 main.py에서 가져올 수 있도록 변수명 통일
# 여기서는 라우터 두 개를 모두 main.py에 등록해야 함
# 편의상 하나의 파일에서 관리하지만, 실제로는 파일을 분리하는 것이 더 나을 수 있음
# main.py에서 auth_router, users_router, posts_router, comments_router 를 가져오므로
# posts_router 라는 이름의 변수가 있어야 함. 두 라우터를 합쳐서 보내거나, 
# main.py에서 임포트 구문을 수정해야 함.
# 여기서는 posts_router 라는 이름으로 page_router를 사용하고, api_router는 별도로 등록.
posts_router = page_router
posts_api_router = api_router