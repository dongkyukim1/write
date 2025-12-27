# 글쓰기 작가를 위한 AI LLM 워크스페이스

방송작가, 소설가, 시나리오 작가를 위한 AI LLM 프롬프트 및 템플릿 관리 시스템입니다.

## 📁 폴더 구조

```
write/
├── prompts/              # 프롬프트 템플릿
│   ├── story/           # 스토리 생성 프롬프트
│   ├── character/       # 캐릭터 생성 프롬프트
│   ├── plot/            # 플롯 구조 프롬프트
│   └── style/           # 글쓰기 스타일 프롬프트
├── models/              # LLM 모델 설정 및 관리
│   ├── config/          # 모델별 설정 파일
│   └── providers/       # OpenAI, Claude 등 프로바이더 설정
├── templates/           # 글쓰기 템플릿
│   ├── novel/          # 소설 템플릿
│   ├── short_story/    # 단편 템플릿
│   ├── script/         # 시나리오 템플릿
│   └── talk_show/      # 방송 대본 템플릿
├── utils/               # 유틸리티 함수
│   ├── text_processing/ # 텍스트 처리
│   └── formatting/      # 포맷팅 도구
├── examples/            # 예제 및 샘플
├── config/              # 전역 설정
└── docs/                # 문서
```

## 🚀 빠른 시작

### 0. 실행 방법

**가장 쉬운 방법 (루트에서 실행):**
```bash
# 방송 대본 생성
python create_script.py

# 장편 소설 생성
python create_novel.py
```

**또는 scripts 폴더에서:**
```bash
python scripts/generate_script.py
python scripts/long_form_novel_generator.py
```

자세한 실행 방법: [HOW_TO_RUN.md](HOW_TO_RUN.md)

### 1. 설정 파일 준비

```bash
# 환경 변수 설정 (선택사항)
cp config/.env.example config/.env
# .env 파일에 API 키 등 입력
```

### 2. 템플릿 사용하기

#### 방송 대본 작성 (매불쇼 스타일)
```bash
# 템플릿 파일 열기
templates/talk_show/maebul_show_template.md

# 각 섹션을 채워서 대본 완성
```

#### 소설/단편 작성
```bash
# 프롬프트 사용
prompts/story/novel_generator.md

# 템플릿 사용
templates/novel/basic_structure.md
```

### 3. AI 모델과 함께 사용하기

```python
# Python 예시 (utils 사용)
from utils.text_processing import load_prompt_template
from models.providers import get_llm_client

# 프롬프트 로드
prompt = load_prompt_template("story/novel_generator.md", 
                               topic="SF 소설", 
                               length="중편")

# AI 모델 호출
client = get_llm_client("openai")
response = client.generate(prompt)
```

## 📖 주요 기능

### 1. 프롬프트 관리
- 재사용 가능한 프롬프트 템플릿
- 변수 치환 지원
- 스타일별 프롬프트 분류

### 2. 템플릿 시스템
- 방송 대본 템플릿 (토크쇼, 예능 등)
- 소설/단편 템플릿
- 시나리오 템플릿

### 3. 모델 관리
- 여러 LLM 프로바이더 지원
- 모델별 설정 관리
- API 키 관리

### 4. 유틸리티
- 텍스트 처리 함수
- 포맷팅 도구
- 대본 검증 도구

## 🎯 사용 예시

### 방송작가: 매불쇼 대본 작성
1. `templates/talk_show/maebul_show_template.md` 열기
2. 이번 주 이슈 선정
3. 각 섹션 채우기
4. 티키타카 포인트 기획
5. 러닝타임 체크

### 소설가: 캐릭터 생성
1. `prompts/character/character_generator.md` 사용
2. 캐릭터 속성 입력
3. AI로 캐릭터 프로필 생성
4. `examples/character/` 참고

### 시나리오 작가: 플롯 구조
1. `prompts/plot/three_act_structure.md` 사용
2. 장르, 주제 입력
3. 3막 구조 플롯 생성
4. `templates/script/` 템플릿으로 대본화

## 📝 파일 형식

- **프롬프트**: `.md` 파일, 변수는 `{{변수명}}` 형식
- **템플릿**: `.md` 파일, 체크리스트 포함
- **설정**: `.json` 또는 `.yaml` 파일
- **유틸리티**: `.py` 파일 (Python)

## 🔧 커스터마이징

### 새로운 프롬프트 추가
```bash
# prompts/story/ 폴더에 새 파일 생성
prompts/story/my_custom_prompt.md
```

### 새로운 템플릿 추가
```bash
# templates/ 폴더에 새 템플릿 생성
templates/my_template.md
```

### 모델 설정 변경
```bash
# models/config/ 폴더에서 설정 파일 수정
models/config/openai_config.json
```

## 📚 더 알아보기

- [프롬프트 작성 가이드](docs/prompt_guide.md)
- [템플릿 사용법](docs/template_usage.md)
- [모델 설정 가이드](docs/model_config.md)
- [예제 모음](examples/README.md)

## 💡 팁

1. **프롬프트는 구체적으로**: 모호한 지시보다는 명확한 예시 제공
2. **템플릿은 유연하게**: 고정된 구조보다는 가이드라인으로 활용
3. **예제를 참고하세요**: `examples/` 폴더의 샘플 활용
4. **반복 작업은 자동화**: `utils/` 폴더의 함수 활용

## 📚 문서 가이드

### 초보자용
- **[초보자를 위한 완전 가이드](GUIDE_FOR_BEGINNERS.md)** ⭐ 추천
  - 설치부터 사용까지 모든 과정을 쉽게 설명
  - 프로그래밍 지식 없어도 따라할 수 있음
  - FAQ 포함

- **[단계별 상세 가이드](GUIDE_STEP_BY_STEP.md)**
  - 각 기능을 더 자세히 설명
  - 스크린샷 대신 텍스트로 설명
  - 예시 많이 포함

- **[문제 해결 가이드](TROUBLESHOOTING.md)**
  - 자주 발생하는 오류와 해결 방법
  - 단계별 해결 가이드
  - 체크리스트 제공

### 일반 사용자용
- **[빠른 시작 가이드](QUICKSTART.md)** - 5분 안에 시작하기
- **[전체 사용법](USAGE.md)** - 모든 기능 상세 설명
- **[기능 가이드](README_FEATURES.md)** - 추가 기능 설명

### 고급 사용자용
- **[장편 소설 가이드](README_LONG_FORM.md)** - 장편 소설 작성 시스템
- **[RAG 시스템 가이드](docs/rag_guide.md)** - 벡터 DB 활용
- **[MCP 서버 가이드](mcp_server/README.md)** - 로컬 모델 연동

## 📞 문의

이슈나 개선 사항이 있으면 이슈를 등록해주세요.

**도움이 필요하신가요?**
1. [초보자 가이드](GUIDE_FOR_BEGINNERS.md) 먼저 확인
2. [문제 해결 가이드](TROUBLESHOOTING.md)에서 오류 찾기
3. [전체 사용법](USAGE.md) 참고

