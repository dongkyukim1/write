# 송우진 프로젝트 (Script Studio)

**AI가 계속 성장하는 대본 작성 시스템**

> Cursor + Git + MCP + OpenAPI 기반 — AI는 즉흥적으로 쓰고, 인간은 구조를 설계하며, 시스템은 기억하고 진화한다

---

## 📋 목차

1. [빠른 시작](#-빠른-시작)
2. [주요 기능](#-주요-기능)
3. [웹 UI 사용법](#-웹-ui-사용법)
4. [AI 생성 원리](#-ai-생성-원리)
5. [시스템 구조](#-시스템-구조)
6. [API 레퍼런스](#-api-레퍼런스)
7. [개발 가이드](#-개발-가이드)

---

## 🚀 빠른 시작

### 1단계: 설치

```powershell
# 의존성 설치
pip install -r requirements.txt
```

### 2단계: 환경변수 설정

`.env` 파일 생성:
```env
OPENAI_API_KEY=sk-your-api-key-here
```

### 3단계: 서버 실행

```powershell
cd api
python -m uvicorn main:app --reload --port 8000
```

### 4단계: 웹 접속

```
http://localhost:8000
```

### (선택) 샘플 데이터 생성

```powershell
python scripts/seed_data.py
```

---

## ✨ 주요 기능

### 🎬 프로젝트 관리
| 기능 | 설명 |
|------|------|
| 프로젝트 생성 | 토크쇼, 드라마, 영화 등 타입 선택 |
| 세계관 설정 | 배경, 규칙, 금지사항 정의 |
| 스타일 가이드 | AI가 따를 문체/톤 지정 |

### 👥 캐릭터 관리
| 기능 | 설명 |
|------|------|
| 캐릭터 생성 | 이름, 역할, 성격 정의 |
| 말투 설정 | 대사 스타일 지정 |
| 금지 설정 | 캐릭터가 하면 안 되는 것 |
| 상태 추적 | 현재 캐릭터 상태 관리 |

### 📺 에피소드/장면 관리
| 기능 | 설명 |
|------|------|
| 에피소드 생성 | 번호, 제목, 주제 설정 |
| 장면 생성 | 목표, 감정곡선, 갈등유형 정의 |
| 메타데이터 | 구조화된 장면 정보 저장 |

### 🤖 AI 대본 생성
| 기능 | 설명 |
|------|------|
| 컨텍스트 학습 | 기존 대본/평가에서 패턴 학습 |
| 자동 생성 | 캐릭터, 세계관 반영한 대본 생성 |
| 자동 평가 | 생성 즉시 품질 평가 |
| 진화 | 피드백 반영하여 품질 향상 |

### 📊 평가 시스템
| 점수 | 설명 |
|------|------|
| 창의성 | 신선함, 예측불가 정도 |
| 일관성 | 캐릭터/세계관 유지 |
| 감정 | 감정 전달력 |
| 페이싱 | 리듬감, 템포 |
| 대화 | 자연스러움 |

---

## 🖥️ 웹 UI 사용법

### 메인 화면 구성

```
┌─────────────────────────────────────────────────────────┐
│ 송우진 프로젝트                                          │
├──────────┬──────────────────────────────────────────────┤
│ 사이드바  │                  메인 영역                   │
│          │                                              │
│ 프로젝트  │  [프로젝트] [캐릭터] [에피소드] [AI생성] [대본] │
│ 목록     │                                              │
│          │              탭별 컨텐츠                      │
│          │                                              │
└──────────┴──────────────────────────────────────────────┘
```

### 탭별 기능

#### 1️⃣ 프로젝트 탭
- **새 프로젝트 생성**: 제목, 타입, 세계관, 스타일 입력
- **프로젝트 선택**: 사이드바에서 클릭

#### 2️⃣ 캐릭터 탭
- **캐릭터 추가**: 이름, 역할, 성격, 말투 입력
- **캐릭터 목록**: 프로젝트별 캐릭터 확인

#### 3️⃣ 에피소드 탭
- **에피소드 생성**: 번호, 제목, 주제 입력
- **에피소드 목록**: 장면 수, 글자 수 확인

#### 4️⃣ AI 생성 탭 ⭐
```
1. 에피소드 선택
2. 장면 번호 입력
3. 장면 목표 작성 (상세할수록 좋음)
4. 장면 타입 선택 (오프닝, 대화, 하이라이트 등)
5. 갈등 유형 선택
6. 참여 캐릭터 체크
7. [AI 대본 생성] 클릭
```

#### 5️⃣ 생성된 대본 탭
- **장면 목록**: 모든 생성된 장면 확인
- **대본 내용**: 클릭하면 전체 대본 표시
- **평가 결과**: 점수, 강점, 제안 확인

---

## 🧠 AI 생성 원리

### 학습 컨텍스트 구축

```
[기존 대본/평가]
       ↓
┌─────────────────────────┐
│  학습 컨텍스트 빌더      │
│  - 베스트 장면 분석      │
│  - 캐릭터 말투 패턴      │
│  - 강점/약점 추출        │
└─────────────────────────┘
       ↓
[새 장면 생성 시 반영]
```

### 생성 → 평가 → 학습 사이클

```
1. 사용자 입력 (목표, 캐릭터)
       ↓
2. 컨텍스트 로드 (세계관, 기존 패턴)
       ↓
3. OpenAI API 호출 (프롬프트 + 컨텍스트)
       ↓
4. 대본 생성
       ↓
5. 자동 평가 (점수 + 피드백)
       ↓
6. DB 저장 (다음 생성 시 학습에 활용)
```

### 품질이 올라가는 이유

| 요소 | 동작 |
|------|------|
| 강점 유지 | 높은 점수 받은 요소를 다음 생성에 반영 |
| 약점 회피 | 지적받은 문제를 피하도록 지시 |
| 캐릭터 일관성 | 기존 대사 패턴을 학습하여 유지 |
| 스타일 유지 | 프로젝트 스타일 가이드 자동 적용 |

---

## 🏗️ 시스템 구조

### 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    송우진 프로젝트                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   웹 UI     │  │  FastAPI    │  │    OpenAI API       │ │
│  │ (브라우저)   │→│  (REST API) │→│  (대본 생성/평가)     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│         │               │                    │              │
│         └───────────────┼────────────────────┘              │
│                         ↓                                   │
│              ┌─────────────────────┐                        │
│              │   SQLite Database   │                        │
│              │   (data/write.db)   │                        │
│              └─────────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### 폴더 구조

```
write/
├── api/                      # FastAPI 서버
│   ├── main.py              # 앱 진입점
│   ├── routers/             # API 라우터
│   │   ├── projects.py      # 프로젝트 API
│   │   ├── characters.py    # 캐릭터 API
│   │   ├── episodes.py      # 에피소드 API
│   │   ├── scenes.py        # 장면 API
│   │   ├── evaluations.py   # 평가 API
│   │   └── generate.py      # AI 생성 API ⭐
│   └── static/              # 웹 UI
│       ├── index.html       # 메인 HTML
│       ├── style.css        # 스타일
│       └── app.js           # 프론트엔드 로직
│
├── models/
│   ├── database/            # 데이터베이스
│   │   ├── models.py        # SQLAlchemy 모델
│   │   ├── crud.py          # CRUD 함수
│   │   └── schema.py        # DB 스키마
│   └── schemas/             # Pydantic 스키마
│       ├── project.py
│       ├── character.py
│       ├── episode.py
│       ├── scene.py
│       └── evaluation.py
│
├── services/                # 비즈니스 로직
│   ├── evaluator.py         # 평가 서비스
│   ├── generator.py         # 생성 서비스
│   └── context_builder.py   # 컨텍스트 빌더
│
├── mcp_server/              # MCP 서버 (AI 컨텍스트)
├── scripts/                 # 유틸리티 스크립트
│   └── seed_data.py         # 샘플 데이터 생성
├── data/                    # 데이터베이스 파일
├── config/                  # 설정 파일
└── .env                     # 환경변수 (Git 제외)
```

---

## 📚 API 레퍼런스

### 프로젝트 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/projects/` | 프로젝트 목록 |
| POST | `/api/projects/` | 프로젝트 생성 |
| GET | `/api/projects/{id}` | 프로젝트 상세 |
| PUT | `/api/projects/{id}` | 프로젝트 수정 |
| DELETE | `/api/projects/{id}` | 프로젝트 삭제 |

### 캐릭터 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/characters/` | 캐릭터 생성 |
| GET | `/api/characters/{id}` | 캐릭터 상세 |
| GET | `/api/characters/by-project/{project_id}` | 프로젝트별 캐릭터 |
| GET | `/api/characters/{id}/context` | MCP용 컨텍스트 |

### 에피소드 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/episodes/` | 에피소드 생성 |
| GET | `/api/episodes/{id}` | 에피소드 상세 |
| GET | `/api/episodes/by-project/{project_id}` | 프로젝트별 에피소드 |
| GET | `/api/episodes/{id}/full-script` | 전체 대본 내보내기 |

### 장면 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/scenes/` | 장면 생성 |
| GET | `/api/scenes/{id}` | 장면 상세 |
| PUT | `/api/scenes/{id}` | 장면 수정 |
| DELETE | `/api/scenes/{id}` | 장면 삭제 |

### AI 생성 API ⭐

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/generate/scene` | AI 대본 생성 |
| GET | `/api/generate/context/{project_id}` | 학습 컨텍스트 조회 |

**요청 예시:**
```json
{
  "scene_id": 1,
  "goal": "시청자 흥미 유발 및 오늘 주제 소개",
  "scene_type": "opening",
  "conflict_type": "none",
  "character_ids": [1, 2, 3]
}
```

### 평가 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/evaluations/` | 평가 생성 |
| GET | `/api/evaluations/by-scene/{scene_id}` | 장면 평가 조회 |

---

## 🛠️ 개발 가이드

### 새 라우터 추가

```python
# api/routers/my_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import get_db

router = APIRouter()

@router.get("/")
async def list_items(db: Session = Depends(get_db)):
    return {"items": []}
```

```python
# api/main.py에 추가
from api.routers import my_router
app.include_router(my_router.router, prefix="/api/my", tags=["My"])
```

### 새 모델 추가

```python
# models/database/models.py
class MyModel(Base):
    __tablename__ = "my_table"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 환경변수 설정

```env
# .env
OPENAI_API_KEY=sk-...          # OpenAI API 키
DATABASE_URL=sqlite:///data/write.db  # DB 경로
```

---

## 📝 기술 스택

| 영역 | 기술 |
|------|------|
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Database | SQLite |
| Frontend | Vanilla JS, CSS (Apple-inspired) |
| AI | OpenAI API (GPT-4o, GPT-4o-mini) |
| Version Control | Git |

---

## ❓ 문제 해결

### 서버가 안 켜져요
```powershell
# 포트 사용 중인 프로세스 종료
Get-Process -Name python | Stop-Process -Force
```

### OpenAI API 에러
- `.env` 파일에 `OPENAI_API_KEY` 확인
- API 키가 유효한지 확인
- 크레딧 잔액 확인

### 장면 생성이 안 돼요
- 에피소드가 먼저 생성되어 있어야 함
- 캐릭터가 최소 1명 이상 있어야 함
- 장면 목표를 상세히 작성

---

## 📄 라이선스

MIT License

---

## 📞 문의

GitHub Issues를 통해 문의해 주세요.

---

**Made with ❤️ by 송우진**
