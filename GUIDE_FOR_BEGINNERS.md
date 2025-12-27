# 초보자를 위한 완전 가이드

**프로그래밍을 모르셔도 괜찮습니다!** 이 가이드를 따라하시면 누구나 사용할 수 있습니다.

## 📋 목차

1. [이 프로그램이 뭔가요?](#이-프로그램이-뭔가요)
2. [준비하기](#준비하기)
3. [첫 번째 사용하기](#첫-번째-사용하기)
4. [주요 기능 사용법](#주요-기능-사용법)
5. [문제 해결](#문제-해결)

---

## 이 프로그램이 뭔가요?

이 프로그램은 **글쓰기를 도와주는 AI 도구**입니다.

### 할 수 있는 일

✅ **방송 대본 작성** - 매불쇼 같은 토크쇼 대본 만들기  
✅ **소설 쓰기** - 단편부터 장편까지 소설 작성  
✅ **캐릭터 만들기** - 소설에 등장할 인물 만들기  
✅ **플롯 구성** - 이야기 구조 짜기  

### 필요한 것

- 컴퓨터 (Windows, Mac, Linux 모두 가능)
- 인터넷 연결
- AI 모델 API 키 (OpenAI 또는 Claude) - 나중에 설명합니다

---

## 준비하기

### 1단계: Python 설치 확인

**Python이 뭔가요?**  
→ 이 프로그램이 작동하는 데 필요한 기본 프로그램입니다.

**설치되어 있는지 확인하기:**

1. 키보드에서 `Windows 키 + R` 누르기
2. `cmd` 입력하고 Enter
3. 검은 창이 뜨면 다음 입력:
   ```
   python --version
   ```
4. 버전 번호가 나오면 → ✅ 설치됨!
5. "python은 내부 또는 외부 명령..." 나오면 → ❌ 설치 필요

**Python 설치하기 (설치 안 되어 있다면):**

1. 인터넷 브라우저 열기
2. https://www.python.org/downloads/ 접속
3. "Download Python" 큰 버튼 클릭
4. 다운로드된 파일 실행
5. **중요**: "Add Python to PATH" 체크박스에 체크!
6. "Install Now" 클릭
7. 설치 완료 후 컴퓨터 재시작

### 2단계: 프로그램 파일 다운로드

이 폴더(`c:\write\`)가 이미 있다면 다음 단계로 넘어가세요.

### 3단계: 필요한 도구 설치

1. 검은 창(cmd) 열기 (위에서 설명한 방법)
2. 다음 명령어 입력 (한 줄씩):
   ```
   cd c:\write
   pip install -r requirements.txt
   ```

**설명:**
- `cd c:\write` → 프로그램 폴더로 이동
- `pip install...` → 필요한 도구들 설치

**시간:** 5-10분 정도 걸릴 수 있습니다.

### 4단계: API 키 준비

**API 키가 뭔가요?**  
→ AI를 사용하기 위한 열쇠 같은 것입니다. 유료 서비스입니다.

**OpenAI API 키 받기 (추천):**

1. https://platform.openai.com 접속
2. 회원가입 또는 로그인
3. 왼쪽 메뉴에서 "API keys" 클릭
4. "Create new secret key" 클릭
5. 키 복사 (다시 볼 수 없으니 잘 보관!)

**Claude API 키 받기 (선택사항):**

1. https://console.anthropic.com 접속
2. 회원가입 또는 로그인
3. "API Keys" 메뉴에서 키 생성
4. 키 복사

**⚠️ 중요:**
- API 키는 돈이 듭니다 (사용량에 따라)
- 키를 다른 사람에게 알려주지 마세요
- 키를 잃어버리면 다시 만들어야 합니다

### 5단계: API 키 설정

1. `c:\write\` 폴더 열기
2. 새 텍스트 파일 만들기
3. 파일 이름을 정확히 `.env`로 변경 (확장자 없음!)
   - Windows 탐색기에서 파일 확장자 보이게 설정 필요
   - 파일 이름: `.env` (앞에 점 포함)
4. 파일 열어서 다음 내용 입력:
   ```
   OPENAI_API_KEY=여기에_복사한_키_붙여넣기
   ```
   예시:
   ```
   OPENAI_API_KEY=sk-proj-abc123def456...
   ```
5. 저장하고 닫기

**파일 이름이 안 바뀌나요?**
- Windows 탐색기에서 "보기" → "파일 확장자" 체크
- 또는 메모장에서 "다른 이름으로 저장" → 파일 이름: `.env` → 파일 형식: "모든 파일"

---

## 첫 번째 사용하기

### 테스트: API가 작동하는지 확인

1. 검은 창(cmd) 열기
2. 다음 입력:
   ```
   cd c:\write
   python scripts/test_api.py
   ```
3. "성공!" 메시지가 나오면 → ✅ 준비 완료!
4. 오류가 나오면 → [문제 해결](#문제-해결) 참고

### 첫 번째 대본 작성하기

**간단한 방법 (템플릿 사용):**

1. `c:\write\templates\talk_show\` 폴더 열기
2. `maebul_show_template.md` 파일 복사
3. 새 이름으로 저장 (예: `my_first_script.md`)
4. 파일 열어서 각 섹션 채우기
5. 완성!

**AI 도움 받기:**

1. 검은 창(cmd) 열기
2. 다음 입력:
   ```
   cd c:\write
   python scripts/generate_script.py
   ```
3. 질문에 답하기:
   - 에피소드 제목: "이번 주 날씨 이야기"
   - 방송일: 2024-12-23
   - 메인 토픽: "겨울 날씨"
4. AI가 대본 생성해줌!

---

## 주요 기능 사용법

### 기능 1: 방송 대본 작성

**언제 사용하나요?**
- 토크쇼, 예능 프로그램 대본이 필요할 때
- 매불쇼 같은 시사 토크 프로그램 대본

**사용 방법:**

#### 방법 A: 템플릿 사용 (가장 쉬움)

1. `templates\talk_show\maebul_show_template.md` 파일 열기
2. 각 섹션에 내용 입력:
   - 에피소드 제목
   - 오프닝 멘트
   - 뉴스 요약
   - 본격 토크
3. 저장

#### 방법 B: AI 생성 (빠름)

```bash
python scripts/generate_script.py
```

질문에 답하면 AI가 대본을 만들어줍니다.

**예시:**
```
에피소드 제목: 이번 주 국회 이슈
방송일: 2024-12-23
메인 토픽: 국회 관련 주요 뉴스
```

---

### 기능 2: 소설 쓰기

**언제 사용하나요?**
- 소설, 웹소설을 쓰고 싶을 때
- 단편부터 장편까지

**사용 방법:**

#### 단편 소설 (짧은 이야기)

1. 검은 창 열기
2. Python 코드 실행:
   ```python
   python
   ```
3. 다음 코드 입력 (한 줄씩):
   ```python
   from utils import load_prompt_template
   from models import get_provider, get_api_key, get_model_config
   
   # 프롬프트 준비
   prompt = load_prompt_template(
       "story/novel_generator.md",
       genre="로맨스",
       length="단편",
       style="모던",
       topic="첫사랑"
   )
   
   # AI 호출
   api_key = get_api_key("openai")
   config = get_model_config("openai", "creative")
   provider = get_provider("openai", api_key, config)
   result = provider.generate(prompt)
   
   print(result)
   ```

**⚠️ 복잡하신가요?**  
→ 아래 "장편 소설" 방법이 더 쉽습니다!

#### 장편 소설 (긴 이야기)

**1단계: 소설 초기화**

```bash
python scripts/long_form_novel_generator.py
```

질문에 답하기:
- 소설 ID: `my_first_novel` (영문/숫자만)
- 제목: "마법사의 모험"
- 장르: "판타지"
- 세계관 설정: 여러 줄 입력 (빈 줄로 종료)
- 등장인물: "주인공: 용감한 마법사" 형식으로 입력
- 플롯 구조: 전체 이야기 흐름 입력

**2단계: 챕터 생성**

같은 프로그램에서:
- 챕터 번호: `1`
- 챕터 목표: "주인공이 모험을 시작한다"
- 목표 분량: `5000` (기본값)

**3단계: 계속 챕터 추가**

챕터 2, 3, 4... 계속 생성

**4단계: 결과 확인**

- `novels\my_first_novel\chapters\` 폴더에 챕터 파일 저장됨
- 각 챕터는 `chapter_001.md`, `chapter_002.md` 형식

---

### 기능 3: 캐릭터 만들기

**언제 사용하나요?**
- 소설에 등장할 인물을 만들고 싶을 때

**사용 방법:**

1. `prompts\character\character_generator.md` 파일 참고
2. 또는 Python으로:
   ```python
   from utils import load_prompt_template
   
   prompt = load_prompt_template(
       "character/character_generator.md",
       name="김철수",
       age="25",
       gender="남성",
       role="주인공"
   )
   ```

---

### 기능 4: 소설 분석하기

**언제 사용하나요?**
- 소설이 잘 쓰였는지 확인하고 싶을 때
- 통계를 보고 싶을 때

**사용 방법:**

```bash
python scripts/analyze_novel.py my_first_novel
```

**결과:**
- 총 분량
- 챕터 수
- 일관성 검사 결과
- 문체 분석

**리포트 파일로 저장:**

```bash
python scripts/analyze_novel.py my_first_novel --output report.md
```

---

### 기능 5: 백업하기

**언제 사용하나요?**
- 소설 데이터를 안전하게 보관하고 싶을 때
- 실수로 삭제했을 때 복구하고 싶을 때

**백업하기:**

```bash
python scripts/backup_restore.py backup --novel-id my_first_novel
```

**백업 목록 보기:**

```bash
python scripts/backup_restore.py list
```

**복원하기:**

```bash
python scripts/backup_restore.py restore --backup-file backups\my_first_novel_20241223_120000.zip
```

---

## 문제 해결

### 문제 1: "python은 내부 또는 외부 명령..."

**원인:** Python이 설치되지 않았거나 경로 설정이 안 됨

**해결:**
1. Python 재설치 (위 "준비하기" 참고)
2. 설치 시 "Add Python to PATH" 반드시 체크
3. 컴퓨터 재시작

---

### 문제 2: "모듈을 찾을 수 없습니다"

**원인:** 필요한 도구가 설치 안 됨

**해결:**
```bash
cd c:\write
pip install -r requirements.txt
```

---

### 문제 3: "API 키가 설정되지 않았습니다"

**원인:** `.env` 파일이 없거나 잘못됨

**해결:**
1. `c:\write\.env` 파일 확인
2. 파일 내용 확인:
   ```
   OPENAI_API_KEY=sk-...
   ```
3. 키 앞뒤 공백 없어야 함
4. `=` 기호 양쪽에 공백 없어야 함

---

### 문제 4: "API 호출 실패"

**원인:**
- API 키가 잘못됨
- 인터넷 연결 문제
- API 사용량 초과

**해결:**
1. API 키 다시 확인
2. 인터넷 연결 확인
3. OpenAI/Claude 웹사이트에서 사용량 확인
4. 카드 결제 확인 (첫 사용 시 필요)

---

### 문제 5: 한글이 깨져요

**원인:** 인코딩 문제

**해결:**
1. 파일을 UTF-8로 저장
2. 메모장에서 "다른 이름으로 저장" → 인코딩: UTF-8 선택

---

### 문제 6: 파일을 찾을 수 없어요

**원인:** 경로가 잘못됨

**해결:**
1. 파일 탐색기에서 정확한 경로 확인
2. 검은 창에서 `cd c:\write` 입력하여 이동
3. `dir` 입력하여 파일 목록 확인

---

## 자주 묻는 질문 (FAQ)

### Q1: 무료로 사용할 수 있나요?

**A:** 프로그램 자체는 무료지만, AI 모델 사용은 유료입니다.
- OpenAI: 사용량에 따라 과금 (약 $0.01-0.03 per 1000자)
- Claude: 사용량에 따라 과금

**절약 팁:**
- 짧은 텍스트만 생성
- 결과를 수정해서 재사용
- 로컬 모델 사용 (추후 설명)

---

### Q2: 인터넷 없이 사용할 수 있나요?

**A:** 현재는 인터넷이 필요합니다 (API 호출).  
로컬 모델을 사용하면 인터넷 없이도 가능하지만, 고사양 컴퓨터가 필요합니다.

---

### Q3: 만든 소설은 어디에 저장되나요?

**A:** `c:\write\novels\소설ID\` 폴더에 저장됩니다.

---

### Q4: 다른 사람과 공유할 수 있나요?

**A:** 네! `novels` 폴더를 복사해서 공유하면 됩니다.  
단, `.env` 파일(API 키)은 공유하지 마세요!

---

### Q5: 실수로 삭제했어요

**A:** 백업이 있다면 복원하세요:
```bash
python scripts/backup_restore.py restore --backup-file 백업파일경로
```

---

### Q6: 더 많은 기능을 알고 싶어요

**A:** 다음 문서들을 참고하세요:
- `USAGE.md` - 상세 사용법
- `README_FEATURES.md` - 모든 기능 설명
- `README_LONG_FORM.md` - 장편 소설 가이드

---

## 다음 단계

### 초보자 추천 순서

1. ✅ **방송 대본 작성** - 가장 쉬움
2. ✅ **단편 소설** - 중간 난이도
3. ✅ **장편 소설** - 조금 어려움
4. ✅ **분석 도구** - 통계 보기

### 고급 기능 (나중에)

- RAG 시스템 (벡터 DB)
- MCP 서버
- 배치 생성
- 로컬 모델 연동

---

## 도움이 필요하신가요?

1. 이 가이드 다시 읽어보기
2. `USAGE.md` 파일 참고
3. 오류 메시지를 그대로 검색해보기
4. 문제 해결 섹션 확인

---

**마지막 팁:**

- 처음엔 작은 것부터 시작하세요
- 실수해도 괜찮습니다 (백업 있으니까!)
- AI가 만든 결과는 참고용입니다 - 수정하고 다듬으세요
- 즐겁게 사용하세요! 🎉

