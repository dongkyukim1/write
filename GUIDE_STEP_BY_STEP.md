# 단계별 상세 가이드

**비전공자도 따라할 수 있는** 단계별 설명서입니다.

## 📚 목차

1. [설치부터 시작까지 (완전 초보용)](#1-설치부터-시작까지)
2. [방송 대본 작성하기](#2-방송-대본-작성하기)
3. [소설 쓰기](#3-소설-쓰기)
4. [고급 기능 사용하기](#4-고급-기능-사용하기)

---

## 1. 설치부터 시작까지

### 1-1. Python 설치 확인 및 설치

#### Windows에서 확인하기

**방법 1: 명령 프롬프트 사용**

1. 키보드에서 `Windows 키` 누르기
2. `cmd` 입력
3. Enter 키 누르기
4. 검은 창이 뜹니다
5. 다음 입력:
   ```
   python --version
   ```
6. 결과 확인:
   - `Python 3.x.x` 나오면 → ✅ 설치됨!
   - `'python'은(는) 내부 또는 외부 명령...` 나오면 → ❌ 설치 필요

**방법 2: 시작 메뉴에서 확인**

1. 시작 메뉴 열기
2. "Python" 검색
3. "Python 3.x" 나오면 설치됨

#### Python 설치하기 (설치 안 되어 있다면)

**단계별 설치:**

1. **다운로드**
   - 브라우저 열기
   - https://www.python.org/downloads/ 접속
   - 노란색 "Download Python 3.x.x" 버튼 클릭
   - 다운로드 폴더에 파일 저장됨

2. **설치**
   - 다운로드한 파일 더블클릭
   - **중요**: "Add Python to PATH" 체크박스에 체크! ✅
   - "Install Now" 클릭
   - 설치 완료까지 대기 (5-10분)

3. **확인**
   - 컴퓨터 재시작 (권장)
   - 명령 프롬프트 열기
   - `python --version` 입력
   - 버전 번호 나오면 성공!

**⚠️ 주의사항:**
- "Add Python to PATH"를 반드시 체크해야 합니다!
- 체크 안 하면 나중에 문제 생깁니다

---

### 1-2. 프로그램 파일 확인

**현재 위치 확인:**

1. 파일 탐색기 열기
2. 주소창에 `c:\write` 입력
3. Enter
4. 다음 파일들이 보여야 합니다:
   - `README.md`
   - `requirements.txt`
   - `scripts` 폴더
   - `templates` 폴더

**없다면:**
- 이 폴더를 다운로드하거나
- 올바른 위치로 이동

---

### 1-3. 필요한 도구 설치

**pip가 뭔가요?**
→ Python 패키지(도구)를 설치하는 프로그램입니다.

**설치하기:**

1. 명령 프롬프트 열기 (cmd)
2. 다음 명령어 입력 (한 줄씩):
   ```
   cd c:\write
   ```
   Enter
   ```
   pip install -r requirements.txt
   ```
   Enter

**설명:**
- `cd c:\write` → 프로그램 폴더로 이동
- `pip install...` → 필요한 도구들 설치

**시간:** 5-15분 걸릴 수 있습니다.

**성공 확인:**
- 마지막에 "Successfully installed..." 메시지 나오면 성공!

**오류 발생 시:**
- 인터넷 연결 확인
- `pip install --upgrade pip` 실행 후 다시 시도

---

### 1-4. API 키 받기

**API 키란?**
→ AI를 사용하기 위한 열쇠입니다. 유료 서비스입니다.

#### OpenAI API 키 받기 (추천)

**단계별:**

1. **회원가입/로그인**
   - 브라우저에서 https://platform.openai.com 접속
   - "Sign up" 또는 "Log in" 클릭
   - 이메일로 가입 (또는 Google 계정 사용)

2. **결제 정보 등록**
   - 왼쪽 메뉴에서 "Billing" 클릭
   - "Add payment method" 클릭
   - 카드 정보 입력
   - ⚠️ 최소 $5 충전 필요할 수 있음

3. **API 키 생성**
   - 왼쪽 메뉴에서 "API keys" 클릭
   - "Create new secret key" 클릭
   - 키 이름 입력 (예: "my-write-tool")
   - "Create secret key" 클릭
   - **키 복사!** (다시 볼 수 없음)
   - 안전한 곳에 저장 (메모장 등)

**키 형식:**
```
sk-proj-abc123def456ghi789...
```

#### Claude API 키 받기 (선택사항)

1. https://console.anthropic.com 접속
2. 회원가입/로그인
3. "API Keys" 메뉴
4. "Create Key" 클릭
5. 키 복사

---

### 1-5. API 키 설정

**`.env` 파일 만들기:**

**방법 1: 메모장 사용 (쉬움)**

1. 메모장 열기
2. 다음 내용 입력:
   ```
   OPENAI_API_KEY=여기에_복사한_키_붙여넣기
   ```
   예시:
   ```
   OPENAI_API_KEY=sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
   ```
3. "파일" → "다른 이름으로 저장"
4. 파일 이름: `.env` (정확히!)
5. 파일 형식: "모든 파일 (*.*)" 선택
6. 저장 위치: `c:\write\` 폴더
7. 저장

**방법 2: 파일 탐색기 사용**

1. `c:\write\` 폴더 열기
2. 빈 공간에서 우클릭
3. "새로 만들기" → "텍스트 문서"
4. 파일 이름을 `.env`로 변경
   - 파일 확장자 보이게 설정 필요
   - "보기" → "파일 확장자" 체크
5. 파일 열기
6. 내용 입력 (위와 동일)
7. 저장

**확인하기:**

1. `c:\write\.env` 파일이 있는지 확인
2. 파일 열어서 내용 확인:
   ```
   OPENAI_API_KEY=sk-...
   ```
3. 키 앞뒤 공백 없어야 함
4. `=` 기호 양쪽 공백 없어야 함

---

### 1-6. 테스트: 작동하는지 확인

**테스트 실행:**

1. 명령 프롬프트 열기
2. 다음 입력:
   ```
   cd c:\write
   python scripts/test_api.py
   ```
3. 결과 확인:
   - "성공!" 또는 "API 연동이 정상적으로 작동합니다!" → ✅ 성공!
   - 오류 메시지 → [문제 해결](#문제-해결) 참고

**성공했다면:** 다음 단계로!

**실패했다면:**
- API 키 확인
- `.env` 파일 위치 확인
- 인터넷 연결 확인

---

## 2. 방송 대본 작성하기

### 2-1. 템플릿 사용하기 (가장 쉬움)

**단계별:**

1. **템플릿 파일 열기**
   - 파일 탐색기에서 `c:\write\templates\talk_show\` 폴더 열기
   - `maebul_show_template.md` 파일 더블클릭
   - 메모장이나 마크다운 에디터로 열림

2. **템플릿 복사**
   - 전체 선택 (Ctrl+A)
   - 복사 (Ctrl+C)
   - 새 파일 만들기
   - 붙여넣기 (Ctrl+V)
   - 다른 이름으로 저장: `my_script.md`

3. **각 섹션 채우기**
   - `[이번 주 핵심 이슈 한 줄]` → 실제 이슈로 변경
   - `[YYYY-MM-DD]` → 실제 날짜로 변경
   - 각 멘트 부분에 실제 대사 입력

4. **완성!**
   - 저장
   - 사용

**예시:**

원래:
```
**에피소드 제목:** [이번 주 핵심 이슈 한 줄]
**방송일:** [YYYY-MM-DD]
```

변경 후:
```
**에피소드 제목:** 이번 주 날씨가 정말 춥네요
**방송일:** 2024-12-23
```

---

### 2-2. AI로 생성하기 (빠름)

**단계별:**

1. **명령 프롬프트 열기**
   ```
   cd c:\write
   python scripts/generate_script.py
   ```

2. **질문에 답하기**
   ```
   사용할 프로바이더를 선택하세요 (1: OpenAI, 2: Claude) [1]: 
   ```
   → `1` 입력하고 Enter

   ```
   대본 정보를 입력해주세요:
   에피소드 제목: 
   ```
   → `이번 주 날씨 이야기` 입력하고 Enter

   ```
   방송일 (YYYY-MM-DD): 
   ```
   → `2024-12-23` 입력하고 Enter

   ```
   메인 토픽: 
   ```
   → `겨울 날씨가 추운 이유` 입력하고 Enter

3. **결과 확인**
   - AI가 오프닝 멘트 생성
   - 화면에 출력됨
   - 복사해서 사용

4. **뉴스 요약 생성 (선택)**
   ```
   뉴스 요약 섹션을 생성하시겠습니까? (y/n) [y]: 
   ```
   → `y` 입력하고 Enter

   ```
   핵심 사실을 입력하세요 (한 줄씩, 빈 줄로 종료):
     사실: 
   ```
   → 사실 입력 (예: `전국적으로 영하 10도 이하`)
   → Enter
   → 또 다른 사실 입력
   → 빈 줄 입력하면 종료

5. **완성!**
   - 생성된 내용 복사
   - 템플릿에 붙여넣기
   - 수정 및 보완

---

### 2-3. 간단한 명령줄 사용

**한 번에 생성:**

```bash
python scripts/simple_generate.py opening "이번 주 날씨 이야기"
```

**결과:**
- 오프닝 멘트가 바로 생성됨
- 화면에 출력

**다른 섹션 생성:**

```bash
# 뉴스 요약
python scripts/simple_generate.py news "날씨 뉴스" "전국 영하 10도, 눈 내림"

# 토크 섹션
python scripts/simple_generate.py talk "겨울 날씨"

# 하이라이트
python scripts/simple_generate.py highlight "추위의 원인"
```

---

## 3. 소설 쓰기

### 3-1. 단편 소설 (짧은 이야기)

**방법 1: 간단한 방법**

1. 명령 프롬프트 열기
2. Python 실행:
   ```
   python
   ```
3. 다음 코드 입력 (한 줄씩):
   ```python
   from utils import load_prompt_template
   from models import get_provider, get_api_key, get_model_config
   
   prompt = load_prompt_template(
       "story/novel_generator.md",
       genre="로맨스",
       length="단편",
       style="모던",
       topic="첫사랑"
   )
   
   api_key = get_api_key("openai")
   config = get_model_config("openai", "creative")
   provider = get_provider("openai", api_key, config)
   result = provider.generate(prompt)
   
   print(result)
   ```

4. 결과 확인
5. 복사해서 파일로 저장

**방법 2: 스크립트 만들기 (더 쉬움)**

1. 메모장 열기
2. 다음 내용 입력:
   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent))
   
   from utils import load_prompt_template
   from models import get_provider, get_api_key, get_model_config
   
   prompt = load_prompt_template(
       "story/novel_generator.md",
       genre="로맨스",
       length="단편",
       style="모던",
       topic="첫사랑"
   )
   
   api_key = get_api_key("openai")
   config = get_model_config("openai", "creative")
   provider = get_provider("openai", api_key, config)
   result = provider.generate(prompt)
   
   print(result)
   ```
3. `generate_novel.py`로 저장 (`c:\write\` 폴더에)
4. 명령 프롬프트에서:
   ```
   python generate_novel.py
   ```

---

### 3-2. 장편 소설 (긴 이야기)

**1단계: 소설 초기화**

```bash
python scripts/long_form_novel_generator.py
```

**질문에 답하기:**

```
소설 ID (영문/숫자만): 
```
→ `my_novel` 입력

```
새 소설을 초기화합니다.
제목: 
```
→ `마법사의 모험` 입력

```
장르: 
```
→ `판타지` 입력

```
세계관 설정을 입력하세요 (여러 줄, 빈 줄로 종료):
```
→ 여러 줄 입력:
```
이 세계는 마법과 기술이 공존하는 판타지 세계입니다.
마법사들은 기술을 경멸하고, 기술자들은 마법을 두려워합니다.
주인공은 두 가지를 모두 사용할 수 있는 희귀한 재능을 가졌습니다.
```
→ 빈 줄 입력하면 종료

```
등장인물 정보를 입력하세요 (이름:설명 형식, 빈 줄로 종료):
인물: 
```
→ `주인공: 용감하고 정의로운 25세 마법사` 입력
→ Enter
→ `동료: 냉정하지만 충성스러운 전사` 입력
→ Enter
→ 빈 줄 입력하면 종료

```
플롯 구조를 입력하세요 (여러 줄, 빈 줄로 종료):
```
→ 전체 이야기 흐름 입력:
```
1막: 주인공이 평범한 일상을 살다가 모험을 시작한다
2막: 여러 시련을 겪으며 성장한다
3막: 최종 보스와 대결하여 승리한다
```
→ 빈 줄 입력하면 종료

**2단계: 챕터 생성**

```
챕터 생성을 시작합니다.

생성할 챕터 번호 (종료: q): 
```
→ `1` 입력

```
이 챕터의 목표/주요 사건: 
```
→ `주인공이 평범한 일상을 살고 있다가 이상한 편지를 받는다` 입력

```
목표 분량 (기본 5000자): 
```
→ `5000` 입력 (또는 Enter로 기본값 사용)

**결과:**
- 챕터 생성 중...
- 완료 메시지
- `novels\my_novel\chapters\chapter_001.md` 파일 생성됨

**3단계: 계속 챕터 추가**

같은 프로그램에서 계속:
```
생성할 챕터 번호 (종료: q): 
```
→ `2` 입력
→ 목표 입력
→ 반복...

**4단계: 결과 확인**

- `c:\write\novels\my_novel\chapters\` 폴더 열기
- `chapter_001.md`, `chapter_002.md` 등 확인
- 파일 열어서 내용 확인

---

### 3-3. 배치로 여러 챕터 생성

**JSON 파일 준비:**

1. 메모장 열기
2. 다음 내용 입력:
   ```json
   [
     {
       "chapter": 1,
       "goal": "주인공이 모험을 시작한다"
     },
     {
       "chapter": 2,
       "goal": "첫 번째 시련에 직면한다"
     },
     {
       "chapter": 3,
       "goal": "동료를 만난다"
     }
   ]
   ```
3. `chapter_goals.json`으로 저장 (`c:\write\` 폴더에)

**배치 생성 실행:**

```bash
python scripts/batch_generate.py my_novel --goals-file chapter_goals.json
```

**결과:**
- 챕터 1, 2, 3이 자동으로 생성됨
- 각 챕터 사이에 1초 대기 (API 비용 고려)

---

### 3-4. 소설 분석하기

**분석 실행:**

```bash
python scripts/analyze_novel.py my_novel
```

**결과 예시:**
```
# 소설 분석 리포트: 마법사의 모험

## 기본 정보
- 총 챕터: 5개
- 총 분량: 25,000자
- 평균 챕터 길이: 5,000자

## 일관성 검사
- 발견된 이슈: 2개
  - 낮음: 2개
```

**리포트 파일로 저장:**

```bash
python scripts/analyze_novel.py my_novel --output report.md
```

- `report.md` 파일 생성됨
- 파일 열어서 확인

---

### 3-5. 백업하기

**백업:**

```bash
python scripts/backup_restore.py backup --novel-id my_novel
```

**결과:**
- `backups\my_novel_20241223_120000.zip` 파일 생성됨
- 메타데이터도 함께 저장

**백업 목록:**

```bash
python scripts/backup_restore.py list
```

**복원:**

```bash
python scripts/backup_restore.py restore --backup-file backups\my_novel_20241223_120000.zip
```

---

## 4. 고급 기능 사용하기

### 4-1. RAG 시스템 (벡터 DB)

**설치:**

```bash
pip install chromadb
```

**사용:**

```python
from utils.rag import NovelRAG

# RAG 시스템 초기화
rag = NovelRAG("my_novel")

# 세계관 추가
rag.add_world_setting("마법과 기술이 공존하는 세계")

# 캐릭터 추가
rag.add_character("주인공", "용감한 마법사")

# 관련 정보 검색
context = rag.get_relevant_context("주인공이 마법을 사용")
```

**자세한 내용:** `docs/rag_guide.md` 참고

---

### 4-2. MCP 서버

**실행:**

```bash
python mcp_server/mcp_server.py
```

**사용:**

다른 터미널에서:
```bash
curl http://localhost:8001/providers
```

**자세한 내용:** `mcp_server/README.md` 참고

---

## 문제 해결

### 자주 발생하는 오류

**1. "python은 내부 또는 외부 명령..."**
- Python 재설치
- PATH 설정 확인

**2. "모듈을 찾을 수 없습니다"**
```bash
pip install -r requirements.txt
```

**3. "API 키가 설정되지 않았습니다"**
- `.env` 파일 확인
- 키 형식 확인

**4. "API 호출 실패"**
- 인터넷 연결 확인
- API 키 확인
- 사용량 확인

---

## 다음 단계

1. ✅ 기본 기능 익히기
2. ✅ 템플릿 활용하기
3. ✅ AI 생성 활용하기
4. ✅ 고급 기능 탐색하기

**추천 학습 순서:**
1. 방송 대본 작성 (가장 쉬움)
2. 단편 소설
3. 장편 소설
4. 분석 도구
5. 고급 기능

---

**도움이 필요하신가요?**

- `GUIDE_FOR_BEGINNERS.md` - 더 자세한 초보자 가이드
- `USAGE.md` - 전체 사용법
- `README_FEATURES.md` - 모든 기능 설명

