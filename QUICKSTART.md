# 빠른 시작 가이드

5분 안에 시작하는 방법을 안내합니다.

## 🚀 1단계: 템플릿으로 대본 작성하기 (가장 간단!)

### 매불쇼 대본 작성

1. **템플릿 파일 열기**
   ```
   templates/talk_show/maebul_show_template.md
   ```

2. **새 파일로 복사**
   - 파일 탐색기에서 복사하거나
   - 에디터에서 "다른 이름으로 저장"

3. **각 섹션 채우기**
   - 에피소드 제목, 날짜 입력
   - 오프닝 멘트 작성
   - 뉴스 요약 작성
   - 본격 토크 작성
   - 체크리스트 확인

**끝!** 이제 대본이 완성되었습니다.

---

## 🤖 2단계: AI와 함께 사용하기 (선택사항)

### Python 설치 확인

```bash
python --version
```

### 패키지 설치

```bash
pip install python-dotenv openai
```

### 환경 변수 설정

1. 프로젝트 루트에 `.env` 파일 생성
2. 다음 내용 입력:
   ```
   OPENAI_API_KEY=your_key_here
   ```

### 간단한 사용 예시

```python
# test.py 파일 생성
from utils import load_prompt_template

# 프롬프트 로드
prompt = load_prompt_template(
    "story/novel_generator.md",
    genre="SF",
    length="단편",
    style="모던",
    topic="시간여행"
)

print(prompt)
```

```bash
python test.py
```

---

## 📚 다음 단계

- **템플릿 사용법**: [USAGE.md](USAGE.md) 참고
- **프롬프트 작성**: [docs/prompt_guide.md](docs/prompt_guide.md) 참고
- **모델 설정**: [docs/model_config.md](docs/model_config.md) 참고
- **예제 보기**: [examples/](examples/) 폴더 참고

---

## 💡 추천 워크플로우

### 방송작가
1. 매주 월요일: 이번 주 이슈 선정
2. 템플릿 복사하여 대본 작성 시작
3. 각 섹션 채우기
4. 체크리스트 확인
5. 완성!

### 소설가
1. 아이디어 정리
2. 캐릭터 생성 (`prompts/character/`)
3. 플롯 구성 (`prompts/plot/`)
4. 소설 작성 (`prompts/story/`)

---

## ❓ 문제가 있나요?

- [USAGE.md](USAGE.md)의 "문제 해결" 섹션 참고
- [README.md](README.md)의 전체 문서 확인

