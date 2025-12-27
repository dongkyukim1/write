# 대본 작성 AI 시스템

**Cursor + Git + MCP + OpenAPI** 기반의 완벽한 대본 작성 도우미 시스템입니다.

## 핵심 철학

> **AI는 즉흥적으로 쓰고, 인간은 구조를 설계하며, 시스템은 기억하고 진화한다**

## 주요 기능

### 1. 구조화된 데이터 저장
- 텍스트만 저장하는 것이 아닌 **메타데이터** 함께 저장
- 감정 곡선, 갈등 유형, 대화 밀도 등 구조화된 정보
- "이런 장면 다시 만들어줘" 기능 가능

### 2. 평가 AI 시스템
- **생성 AI ≠ 평가 AI** (분리된 시스템)
- 창의성 점수, 클리셰 감지, 감정 강도 평가
- 자동 개선 제안

### 3. 컨텍스트 관리 (MCP)
- 세계관 규칙 자동 적용
- 캐릭터 성격/말투 일관성 유지
- 금지 설정으로 설정 붕괴 방지

### 4. Git 통합
- 버전 관리 + 변경 히스토리
- AI 생성/인간 수정 구분
- 학습 데이터로 재활용 가능

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                      Cursor IDE                              │
│                   (작가의 협업 공간)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
         ┌────────────┴────────────┐
         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│   MCP Server    │       │  FastAPI Server │
│ (컨텍스트 제공) │       │   (OpenAPI)     │
└────────┬────────┘       └────────┬────────┘
         │                         │
         └────────────┬────────────┘
                      ▼
              ┌───────────────┐
              │   SQLite DB   │
              │ (구조화 저장) │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │     Git       │
              │ (버전 관리)   │
              └───────────────┘
```

## 빠른 시작

### 1. 설치

```bash
# 저장소 클론
git clone https://github.com/dongkyukim1/write.git
cd write

# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 설정

```bash
# .env 파일 생성
copy .env.example .env

# API 키 설정
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
```

### 3. 서버 실행

```bash
# FastAPI 서버 (포트 8000)
cd api
uvicorn main:app --reload

# MCP 서버 (포트 8001) - 별도 터미널
python mcp_server/mcp_server.py
```

### 4. API 문서 확인

- OpenAPI 문서: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 폴더 구조

```
write/
├── api/                    # FastAPI 서버
│   ├── main.py
│   └── routers/           # API 라우터
├── models/
│   ├── schemas/           # Pydantic 스키마
│   ├── database/          # SQLAlchemy 모델
│   └── providers/         # LLM 프로바이더
├── services/              # 비즈니스 로직
│   ├── evaluator.py       # 평가 AI
│   ├── generator.py       # 대본 생성
│   └── context_builder.py # 컨텍스트 빌더
├── mcp_server/            # MCP 서버
├── utils/                 # 유틸리티
│   ├── git_manager.py     # Git 자동화
│   ├── notion/            # Notion 연동
│   └── rag/               # RAG 시스템
├── prompts/               # 프롬프트 템플릿
├── templates/             # 대본 템플릿
└── data/                  # 데이터 저장소
```

## API 엔드포인트

### Projects
- `POST /api/projects/` - 프로젝트 생성
- `GET /api/projects/` - 프로젝트 목록
- `GET /api/projects/{id}` - 프로젝트 상세
- `GET /api/projects/{id}/context` - MCP용 컨텍스트

### Episodes
- `POST /api/episodes/` - 에피소드 생성
- `GET /api/episodes/by-project/{project_id}` - 에피소드 목록
- `GET /api/episodes/{id}/full-script` - 전체 대본

### Scenes
- `POST /api/scenes/` - 장면 생성 (메타데이터 포함)
- `GET /api/scenes/{id}` - 장면 상세 + 평가
- `GET /api/scenes/search/by-metadata` - 메타데이터로 검색

### Characters
- `POST /api/characters/` - 캐릭터 생성
- `GET /api/characters/{id}/context` - MCP용 컨텍스트
- `PUT /api/characters/{id}/state` - 상태 업데이트

### Evaluations
- `POST /api/evaluations/` - 평가 저장
- `GET /api/evaluations/by-scene/{scene_id}` - 평가 조회
- `GET /api/evaluations/needs-revision` - 수정 필요 목록

## MCP 도구

MCP 서버는 다음 도구들을 제공합니다:

| 도구 | 설명 |
|------|------|
| `get_project_context` | 프로젝트 전체 컨텍스트 |
| `get_character_context` | 캐릭터 정보 |
| `get_world_rules` | 세계관 규칙 |
| `get_scene_history` | 이전 장면 요약 |
| `validate_scene` | 설정 충돌 검증 |
| `evaluate_scene` | 장면 평가 |
| `generate_with_context` | 컨텍스트 포함 생성 |

## 데이터 모델

### Scene (장면) - 핵심 모델

```python
{
    "scene_id": "S01E03_SC02",
    "emotion_curve": ["tension", "climax", "resolution"],
    "conflict_type": "relationship",
    "dialog_density": "high",
    "characters": [1, 2],
    "content": "...",
    "ai_generated": true,
    "human_edited": true,
    "evaluation": {
        "creativity_score": 0.72,
        "cliche_detected": true
    }
}
```

## Git 워크플로우

```
브랜치 전략:
- main          : 최종 승인된 대본
- draft/ai_v1   : AI 초안
- draft/edited  : 작가 수정본
- review/       : 검토 중

커밋 메시지:
- feat(scene): 장면 생성
- ai(scene): AI 생성 장면
- fix(scene): 장면 수정
```

## 라이선스

MIT License

## 기여

이슈와 PR을 환영합니다!
