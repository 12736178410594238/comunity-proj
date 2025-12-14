"""
데이터베이스 연결 설정
SQLAlchemy를 사용하여 SQLite 데이터베이스와 연결합니다
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# 데이터베이스 엔진 생성
# check_same_thread=False는 SQLite에서 멀티스레드 사용을 위해 필요
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# 세션 팩토리 생성
# autocommit=False: 수동으로 commit 해야 함
# autoflush=False: 수동으로 flush 해야 함
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모든 모델의 기본 클래스
Base = declarative_base()

# 데이터베이스 세션을 가져오는 의존성 함수
def get_db():
    """
    데이터베이스 세션을 생성하고 반환합니다.
    요청이 끝나면 자동으로 세션을 닫습니다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()