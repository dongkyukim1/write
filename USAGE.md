# 사용법 가이드

이 문서는 글쓰기 작가를 위한 AI LLM 워크스페이스를 사용하는 방법을 단계별로 안내합니다.

## 📋 목차

1. [초기 설정](#초기-설정)
2. [기본 사용법](#기본-사용법)
3. [템플릿 사용하기](#템플릿-사용하기)
4. [프롬프트 사용하기](#프롬프트-사용하기)
5. [AI 모델과 함께 사용하기](#ai-모델과-함께-사용하기)
6. [고급 사용법](#고급-사용법)

---

## 초기 설정

### 1. 환경 변수 설정 (선택사항)

AI 모델을 사용하려면 API 키가 필요합니다.

```bash
# config 폴더로 이동
cd config

# .env.example을 .env로 복사
copy .env.example .env

# .env 파일을 열어서 API 키 입력
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here
```

### 2. Python 패키지 설치 (선택사항)

유틸리티 함수를 사용하려면:

```bash
pip install python-dotenv
# 또는
pip install -r requirements.txt  # requirements.txt가 있다면
```

---

## 기본 사용법

### 템플릿으로 대본 작성하기

1. **템플릿 파일 열기**
   ```
   templates/talk_show/maebul_show_template.md
   ```

2. **새 파일로 복사**
   ```bash
   copy templates\talk_show\maebul_show_template.md my_episode.md
   ```

3. **각 섹션 채우기**
   - 에피소드 기본 정보 입력
   - 오프닝 멘트 작성
   - 뉴스 요약 섹션 작성
   - 본격 토크 섹션 작성
   - 체크리스트 확인

4. **완성**

### 프롬프트로 소설/캐릭터 생성하기

1. **프롬프트 파일 확인**
   ```
   prompts/story/novel_generator.md
   prompts/character/character_generator.md
   ```

2. **변수 값 준비**
   - genre: "SF", "로맨스" 등
   - length: "단편", "중편", "장편"
   - style: "모던", "클래식" 등

3. **AI 모델에 입력** (다음 섹션 참고)

---

## 템플릿 사용하기

### 매불쇼 대본 템플릿

**위치:** `templates/talk_show/maebul_show_template.md`

**사용 절차:**

1. 템플릿 파일을 새 이름으로 복사
2. 에피소드 정보 입력
3. 각 섹션을 순서대로 채우기:
   - 오프닝 (2분)
   - 뉴스 요약 (6분)
   - 본격 토크 (17분)
   - 하이라이트 (5분)
   - 마무리 (2분)
4. 체크리스트 확인
5. 러닝타임 체크

**팁:**
- 티키타카 포인트를 미리 기획하세요
- 웃음 포인트는 최소 5개 이상 배치
- 가볍게 시작하되 핵심은 정확히

### 소설 템플릿

**위치:** `templates/novel/` (추가 예정)

**사용법:**
1. 템플릿 선택
2. 구조에 맞춰 작성
3. 각 장/섹션 완성

---

## 프롬프트 사용하기

### Python으로 프롬프트 로드하기

```python
from utils import load_prompt_template

# 프롬프트 로드 및 변수 치환
prompt = load_prompt_template(
    "story/novel_generator.md",
    genre="SF",
    length="단편",
    style="모던",
    topic="시간여행"
)

print(prompt)
```

### 변수 확인하기

```python
from utils import extract_variables, validate_template

# 템플릿에서 필요한 변수 추출
template_path = "story/novel_generator.md"
variables = extract_variables(template_path)
print(f"필요한 변수: {variables}")

# 변수 검증
is_valid, missing = validate_template(
    template_path,
    genre="SF",
    length="단편"
)
if not is_valid:
    print(f"누락된 변수: {missing}")
```

---

## AI 모델과 함께 사용하기

### 기본 사용법

```python
import os
from dotenv import load_dotenv
from models import get_provider, get_model_config, get_api_key

# 환경 변수 로드
load_dotenv("config/.env")

# 설정 로드
config = get_model_config("openai", "creative")
api_key = get_api_key("openai")

# 프로바이더 생성
provider = get_provider("openai", api_key, config)

# 프롬프트 준비
from utils import load_prompt_template
prompt = load_prompt_template(
    "story/novel_generator.md",
    genre="SF",
    length="단편",
    style="모던",
    topic="시간여행"
)

# 텍스트 생성
result = provider.generate(prompt)
print(result)
```

### 스트리밍으로 생성하기

```python
# 스트리밍 방식 (실시간으로 결과 확인)
for chunk in provider.generate_stream(prompt):
    print(chunk, end="", flush=True)
```

### 모델 설정 커스터마이징

```python
# 직접 설정 지정
result = provider.generate(
    prompt,
    temperature=0.9,  # 창의성 높임
    max_tokens=3000    # 더 긴 텍스트 생성
)
```

---

## 고급 사용법

### 대본 포맷팅

```python
from utils import format_talk_show_script, calculate_running_time

# 원본 대본
script = """
최욱: 안녕하세요
정영진: 네 안녕하세요
"""

# 포맷팅
formatted = format_talk_show_script(script, ["최욱", "정영진"])
print(formatted)

# 러닝타임 계산
time = calculate_running_time(script)
print(f"예상 러닝타임: {time:.1f}분")
```

### 진행자별 멘트 추출

```python
from utils import extract_speaker_lines

# 특정 진행자의 멘트만 추출
최욱_멘트 = extract_speaker_lines(script, "최욱")
for 멘트 in 최욱_멘트:
    print(멘트)
```

### 배치 처리

여러 프롬프트를 한 번에 처리:

```python
topics = ["시간여행", "첫사랑", "복수"]

for topic in topics:
    prompt = load_prompt_template(
        "story/novel_generator.md",
        genre="SF",
        length="단편",
        style="모던",
        topic=topic
    )
    result = provider.generate(prompt)
    # 결과 저장
    with open(f"output_{topic}.md", "w", encoding="utf-8") as f:
        f.write(result)
```

---

## 워크플로우 예시

### 방송작가 워크플로우

1. **이슈 선정** → 이번 주 주요 뉴스 정리
2. **템플릿 사용** → `maebul_show_template.md` 복사
3. **대본 작성** → 각 섹션 채우기
4. **AI 보조** → 필요시 AI로 아이디어 생성
5. **검토** → 체크리스트 확인, 러닝타임 체크
6. **완성** → 최종 대본 완성

### 소설가 워크플로우

1. **아이디어** → 주제/장르 선정
2. **캐릭터 생성** → `character_generator.md` 사용
3. **플롯 구성** → `three_act_structure.md` 사용
4. **소설 작성** → `novel_generator.md` 사용
5. **수정/보완** → 반복 개선

---

## 문제 해결

### API 키 오류
- `.env` 파일에 올바른 키가 있는지 확인
- 환경 변수가 제대로 로드되는지 확인

### 프롬프트 변수 오류
- `validate_template()` 함수로 변수 확인
- 필요한 변수가 모두 제공되었는지 확인

### 모델 응답 품질
- `temperature` 값 조정 (낮추면 일관성, 높이면 창의성)
- 프롬프트를 더 구체적으로 작성
- 예시를 프롬프트에 포함

---

## 추가 리소스

- [프롬프트 작성 가이드](docs/prompt_guide.md)
- [템플릿 사용법](docs/template_usage.md)
- [모델 설정 가이드](docs/model_config.md)
- [예제 모음](examples/README.md)

---

## 도움이 필요하신가요?

이슈를 등록하거나 개선 사항을 제안해주세요!

