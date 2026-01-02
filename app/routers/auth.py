"""
인증 라우터 - 회원가입, 로그인, 로그아웃 (SSR 버전)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta

from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserResponse
from ..services.auth import AuthService, get_current_user
from ..config import settings

# --- 라우터 및 템플릿 설정 ---
templates = Jinja2Templates(directory="app/templates")
page_router = APIRouter(tags=["인증 페이지"])
api_router = APIRouter(prefix="/api/auth", tags=["인증 API"])


# --- 페이지 렌더링 라우트 ---

@page_router.get("/register")
async def render_register_page(request: Request):
    """회원가입 페이지 렌더링"""
    return templates.TemplateResponse("register.html", {"request": request})

@page_router.get("/login")
async def render_login_page(request: Request):
    """로그인 페이지 렌더링"""
    return templates.TemplateResponse("login.html", {"request": request})

@page_router.get("/logout")
async def logout_and_redirect(response: Response):
    """로그아웃 (쿠키 삭제 후 홈으로 리디렉션)"""
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response


# --- 데이터 처리 API 라우트 ---

@api_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    response: Response,
    user_data: UserCreate = Depends(UserCreate.as_form), # Use UserCreate.as_form for validation
    db: Session = Depends(get_db)
):
    """회원가입 처리 (폼 제출)"""
    # user_data is already validated by Depends(UserCreate.as_form)
    
    # 중복 확인
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="이미 사용 중인 아이디입니다")
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다")

    # 사용자 생성
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=AuthService.get_password_hash(user_data.password),
        nickname=user_data.nickname or user_data.username
    )
    db.add(new_user)
    db.commit()

    # 회원가입 후 바로 로그인 처리
    access_token = AuthService.create_access_token(data={"sub": new_user.username})
    
    # 쿠키에 토큰 저장 후 리디렉션
    redirect_response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    redirect_response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=int(timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds()),
        samesite="lax"
    )
    return redirect_response

@api_router.post("/login")
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """로그인 처리 (폼 제출) 및 토큰 발급"""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not AuthService.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다",
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="비활성화된 계정입니다")

    access_token = AuthService.create_access_token(data={"sub": user.username})
    
    # 쿠키에 토큰 저장 후 리디렉션
    redirect_response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    redirect_response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=int(timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds()),
        samesite="lax"
    )
    return redirect_response

@api_router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """현재 로그인한 사용자 정보 조회 (API용)"""
    return current_user

# main.py에서 임포트할 라우터 변수
auth_router = page_router
auth_api_router = api_router