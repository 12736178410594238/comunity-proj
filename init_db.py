# init_db.py
from app.database import engine, Base
# 아래 임포트는 SQLAlchemy가 모델을 인식하게 하기 위해 필요합니다.
from app.models import user, post, comment 

def init_db():
    """데이터베이스 테이블 생성"""
    print("데이터베이스 테이블을 생성합니다...")
    # 모든 테이블을 삭제하고 다시 생성 (개발용)
    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("테이블 생성이 완료되었습니다.")

if __name__ == "__main__":
    init_db()
