"""
데이터베이스 스키마 설정
SQLAlchemy를 사용한 데이터베이스 연결 및 세션 관리
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 데이터베이스 파일 경로
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{DATA_DIR / 'write.db'}"

# SQLAlchemy 엔진 생성
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},  # SQLite 멀티스레드 지원
    echo=False  # SQL 로깅 (디버깅 시 True로 설정)
)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 베이스 클래스
Base = declarative_base()


def get_db():
    """
    데이터베이스 세션 생성 (FastAPI Depends용)
    
    사용 예시:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    데이터베이스 세션 컨텍스트 매니저 (스크립트용)
    
    사용 예시:
        with get_db_context() as db:
            projects = db.query(ProjectModel).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    데이터베이스 초기화 - 모든 테이블 생성
    
    사용 예시:
        from models.database import init_db
        init_db()
    """
    # 모델 임포트 (테이블 생성을 위해 필요)
    from . import models  # noqa: F401
    
    Base.metadata.create_all(bind=engine)
    print(f"데이터베이스 초기화 완료: {DATABASE_URL}")


def reset_db():
    """
    데이터베이스 리셋 - 모든 테이블 삭제 후 재생성
    주의: 모든 데이터가 삭제됩니다!
    """
    from . import models  # noqa: F401
    
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("데이터베이스 리셋 완료")

