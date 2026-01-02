"""
설정 파일 - 앱의 모든 설정을 관리합니다
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 앱 기본 설정
    APP_NAME: str = "나의 커뮤니티"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 데이터베이스 설정
    DATABASE_URL: str = "sqlite:///./community.db"
    
    # JWT 토큰 설정 (로그인 유지에 사용)
    SECRET_KEY: str # 하드코딩된 키 제거
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24시간
    
    class Config:
        env_file = ".env"

# 설정 인스턴스 생성
settings = Settings()