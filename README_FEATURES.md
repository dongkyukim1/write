# 추가 기능 가이드

프로젝트에 추가된 고급 기능들을 소개합니다.

## 🆕 새로 추가된 기능

### 1. MCP 서버
**위치**: `mcp_server/mcp_server.py`

로컬에서 AI 모델과 통신하기 위한 HTTP 서버입니다.

**사용법**:
```bash
# 서버 실행
python mcp_server/mcp_server.py --port 8001

# 다른 터미널에서 테스트
curl http://localhost:8001/providers
```

**기능**:
- 텍스트 생성 API
- 프로바이더 목록 조회
- 헬스 체크

**자세한 내용**: [mcp_server/README.md](mcp_server/README.md)

---

### 2. RAG 시스템 (벡터 DB)
**위치**: `utils/rag/vector_db.py`

장편 소설 작성 시 컨텍스트를 효과적으로 관리하는 벡터 검색 시스템입니다.

**설치**:
```bash
pip install chromadb
```

**사용법**:
```python
from utils.rag import NovelRAG

rag = NovelRAG("my_novel")
rag.add_world_setting("세계관 설정...")
rag.add_character("주인공", "캐릭터 설명...")

# 관련 컨텍스트 검색
context = rag.get_relevant_context("주인공이 마법을 사용")
```

**자세한 내용**: [docs/rag_guide.md](docs/rag_guide.md)

---

### 3. 백업/복원 시스템
**위치**: `scripts/backup_restore.py`

소설 데이터와 체크포인트를 백업하고 복원합니다.

**사용법**:
```bash
# 백업
python scripts/backup_restore.py backup --novel-id my_novel

# 백업 목록 조회
python scripts/backup_restore.py list

# 복원
python scripts/backup_restore.py restore --backup-file backups/my_novel_20241223.zip
```

**기능**:
- ZIP 파일로 압축 백업
- 메타데이터 저장
- 선택적 복원

---

### 4. 소설 분석 도구
**위치**: `scripts/analyze_novel.py`

소설의 통계, 일관성, 문체를 분석합니다.

**사용법**:
```bash
# 분석 실행
python scripts/analyze_novel.py my_novel

# 리포트 파일로 저장
python scripts/analyze_novel.py my_novel --output report.md
```

**분석 항목**:
- 통계: 총 분량, 챕터 수, 평균 길이 등
- 일관성: 캐릭터 사용, 복선 회수, 챕터 길이 등
- 문체: 문장 길이, 대화 비율, 일관성 등

---

### 5. 배치 생성 스크립트
**위치**: `scripts/batch_generate.py`

여러 챕터를 한 번에 생성합니다.

**사용법**:
```bash
# JSON 파일 사용
python scripts/batch_generate.py my_novel --goals-file examples/chapter_goals.json

# 대화형 입력
python scripts/batch_generate.py my_novel
```

**JSON 형식**:
```json
[
  {
    "chapter": 1,
    "goal": "주인공이 모험을 시작한다"
  },
  {
    "chapter": 2,
    "goal": "첫 번째 시련에 직면한다"
  }
]
```

---

## 📊 기능 비교표

| 기능 | 웹 모델만 | + 체크포인트 | + RAG | + 분석 |
|------|----------|------------|-------|--------|
| 3만자 벽 | ❌ | ✅ | ✅✅ | ✅✅ |
| 20화 벽 | ❌ | ✅ | ✅✅ | ✅✅ |
| 맥락 유지 | ❌ | ⚠️ | ✅ | ✅ |
| 일관성 검증 | ❌ | ⚠️ | ✅ | ✅✅ |
| 편집 비용 | 높음 | 중간 | 낮음 | 낮음 |

---

## 🔧 통합 사용 예시

### 완전한 워크플로우

```bash
# 1. 소설 초기화
python scripts/long_form_novel_generator.py

# 2. 배치로 챕터 생성
python scripts/batch_generate.py my_novel --goals-file goals.json

# 3. 분석 및 리포트 생성
python scripts/analyze_novel.py my_novel --output report.md

# 4. 백업
python scripts/backup_restore.py backup --novel-id my_novel
```

### RAG 통합 워크플로우

```python
from scripts.long_form_novel_generator import LongFormNovelGenerator
from utils.rag import NovelRAG

# 소설 생성기 초기화
generator = LongFormNovelGenerator("my_novel")

# RAG 시스템 초기화
rag = NovelRAG("my_novel")

# 초기 정보를 RAG에 추가
rag.add_world_setting("세계관 설정...")
rag.add_character("주인공", "설명...")

# 챕터 생성 시 RAG 활용
context = rag.get_relevant_context("주인공의 모험")
# ... 프롬프트에 컨텍스트 포함하여 생성 ...
```

---

## 🚀 다음 단계

1. **로컬 모델 연동**: MCP 서버에 로컬 모델 추가
2. **웹 UI**: 브라우저에서 사용할 수 있는 인터페이스
3. **자동 편집**: 생성된 텍스트의 오류 자동 수정
4. **협업 기능**: 여러 작가가 함께 작업할 수 있는 기능

---

## 📚 관련 문서

- [MCP 서버 가이드](mcp_server/README.md)
- [RAG 시스템 가이드](docs/rag_guide.md)
- [장편 소설 가이드](README_LONG_FORM.md)
- [전체 사용법](USAGE.md)

