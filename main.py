"""
메인 애플리케이션 파일
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import engine, Base
from .routers import auth_router, users_router, posts_router, comments_router

# 앱 시작/종료 시 실행될 함수
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시: 데이터베이스 테이블 생성
    print("🚀 서버 시작 중...")
    Base.metadata.create_all(bind=engine)
    print("✅ 데이터베이스 테이블 생성 완료!")
    yield
    # 종료 시
    print("👋 서버 종료 중...")

# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="FastAPI로 만든 커뮤니티 웹사이트",
    lifespan=lifespan
)

# CORS 설정 (프론트엔드와 통신 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시에는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 설정 (CSS, JS, 이미지 등)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 템플릿 설정
templates = Jinja2Templates(directory="app/templates")

# API 라우터 등록
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(posts_router)
app.include_router(comments_router)

# 기본 페이지 라우트
@app.get("/")
async def home(request: Request):
    """메인 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    """로그인 페이지"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    """회원가입 페이지"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/posts")
async def posts_page(request: Request):
    """게시글 목록 페이지"""
    return templates.TemplateResponse("posts.html", {"request": request})

@app.get("/posts/new")
async def create_post_page(request: Request):
    """게시글 작성 페이지"""
    return templates.TemplateResponse("create_post.html", {"request": request})

@app.get("/posts/{post_id}")
async def post_detail_page(request: Request, post_id: int):
    """게시글 상세 페이지"""
    return templates.TemplateResponse("post_detail.html", {"request": request, "post_id": post_id})

# API 상태 확인
@app.get("/api/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy", "app": settings.APP_NAME}