"""
메인 애플리케이션 파일
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import SessionLocal
from .models.user import User
from .services.auth import AuthService

# 라우터 임포트
from .routers.auth import auth_router, auth_api_router
from .routers.posts import posts_router, posts_api_router
from .routers.users import router as users_router
from .routers.comments import router as comments_router

# 앱 시작/종료 시 실행될 함수
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 서버 시작 중...")
    yield
    print("👋 서버 종료 중...")

# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="FastAPI로 만든 커뮤니티 웹사이트",
    lifespan=lifespan
)

# --- 미들웨어 설정 ---

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 사용자 정보 로드 미들웨어
@app.middleware("http")
async def load_user_middleware(request: Request, call_next):
    """
    모든 요청에 대해 쿠키에서 토큰을 읽어 사용자 정보를 로드합니다.
    로딩된 사용자는 request.state.user 에 저장되어 템플릿에서 접근할 수 있습니다.
    """
    request.state.user = None
    token = request.cookies.get("access_token")
    if token:
        db = SessionLocal()
        try:
            payload = AuthService.decode_token(token)
            if payload and payload.get("sub"):
                username = payload.get("sub")
                user = db.query(User).filter(User.username == username, User.is_active == True).first()
                request.state.user = user
        finally:
            db.close()
    
    response = await call_next(request)
    return response

# --- 정적 파일 및 라우터 설정 ---

# 정적 파일 설정
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 라우터 등록
app.include_router(posts_router)      # / 및 /posts/* 페이지
app.include_router(posts_api_router)  # /api/posts/* API
app.include_router(auth_router)       # /login, /register, /logout 페이지
app.include_router(auth_api_router)   # /api/auth/* API
app.include_router(users_router)      # /api/users/* API
app.include_router(comments_router)   # /api/comments/* API

# API 상태 확인
@app.get("/api/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy", "app": settings.APP_NAME}