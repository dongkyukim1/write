"""
FastAPI 메인 애플리케이션
대본 작성 도우미 API 서버
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from models.database import init_db

# 라우터 임포트
from api.routers import projects, episodes, scenes, characters, evaluations


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행"""
    # 시작 시: 데이터베이스 초기화
    init_db()
    print("데이터베이스 초기화 완료")
    yield
    # 종료 시: 정리 작업
    print("서버 종료")


app = FastAPI(
    title="대본 작성 도우미 API",
    description="""
## 대본 작성 AI 시스템 API

Cursor + Git + MCP + OpenAPI 기반의 대본 작성 도우미 시스템입니다.

### 주요 기능

- **프로젝트 관리**: 대본 시리즈/프로젝트 단위 관리
- **에피소드 관리**: 에피소드별 대본 관리
- **장면 관리**: 구조화된 메타데이터와 함께 장면 저장
- **캐릭터 관리**: 캐릭터 설정 및 상태 관리
- **AI 평가**: 창의성, 클리셰, 감정 강도 평가

### 데이터 구조

```
Project
├── Episodes
│   └── Scenes (with Evaluation)
└── Characters
```
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS 설정 (개발용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(episodes.router, prefix="/api/episodes", tags=["Episodes"])
app.include_router(scenes.router, prefix="/api/scenes", tags=["Scenes"])
app.include_router(characters.router, prefix="/api/characters", tags=["Characters"])
app.include_router(evaluations.router, prefix="/api/evaluations", tags=["Evaluations"])


@app.get("/", tags=["Health"])
async def root():
    """API 서버 상태 확인"""
    return {
        "status": "ok",
        "message": "대본 작성 도우미 API 서버가 실행 중입니다.",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """헬스 체크"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )

