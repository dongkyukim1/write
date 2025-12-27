# Notion 통합 가이드

생성된 대본/소설을 Notion 페이지로 자동 생성하는 방법을 안내합니다.

## 준비하기

### 1. Notion Integration 생성

1. https://www.notion.so/my-integrations 접속
2. "New integration" 클릭
3. 이름 입력 (예: "Write AI Tool")
4. 워크스페이스 선택
5. "Submit" 클릭
6. **Internal Integration Token 복사** (다시 볼 수 없음!)

### 2. 페이지에 Integration 연결

1. Notion 페이지 열기
2. 우측 상단 "..." 메뉴 클릭
3. "Connections" → "Add connections" 클릭
4. 만든 Integration 선택
5. 연결 완료!

### 3. API 키 설정

`.env` 파일에 추가:
```
NOTION_API_KEY=secret_abc123...
```

## 사용 방법

### 방송 대본을 Notion에 생성

```bash
python scripts/notion_auto_create.py \
  "https://www.notion.so/your-page-id" \
  --type script \
  --script-file templates/talk_show/ep1.md \
  --title "이번 주 매불쇼 대본"
```

### 소설 챕터를 Notion에 생성

```bash
python scripts/notion_auto_create.py \
  "https://www.notion.so/your-page-id" \
  --type chapter \
  --novel-id my_novel \
  --chapter 1
```

### 소설 요약 페이지 생성

```bash
python scripts/notion_auto_create.py \
  "https://www.notion.so/your-page-id" \
  --type summary \
  --novel-id my_novel
```

## Python 코드로 사용

```python
from utils.notion import NotionClient

# 클라이언트 초기화
client = NotionClient()

# 페이지 ID 추출 (URL에서)
parent_id = client.get_page_id_from_url(
    "https://www.notion.so/2d2e7fbfc5a78081840fdc817d264771"
)

# 하위 페이지 생성
page = client.create_page(
    parent_page_id=parent_id,
    title="새 페이지",
    content="""
# 제목

내용입니다.

## 섹션

- 리스트 항목 1
- 리스트 항목 2
"""
)

print(f"생성된 페이지: {page['url']}")
```

## 자동화 예시

### 대본 생성 후 자동으로 Notion에 업로드

```python
from scripts.generate_script import generate_opening
from utils.notion import NotionClient

# 대본 생성
opening = generate_opening("이번 주 이슈", "openai")

# Notion에 업로드
client = NotionClient()
parent_id = client.get_page_id_from_url("YOUR_NOTION_URL")

page = client.create_page(
    parent_page_id=parent_id,
    title="이번 주 대본",
    content=opening["result"]
)
```

### 소설 챕터 생성 후 자동 업로드

`scripts/long_form_novel_generator.py`를 수정하여 챕터 생성 후 자동으로 Notion에 업로드하도록 할 수 있습니다.

## 주의사항

⚠️ **API 키 보안**
- `.env` 파일에만 저장
- Git에 커밋하지 마세요
- 다른 사람과 공유하지 마세요

⚠️ **페이지 권한**
- Integration을 페이지에 연결해야 합니다
- 부모 페이지에 대한 접근 권한이 필요합니다

⚠️ **속도 제한**
- Notion API는 속도 제한이 있습니다
- 너무 많은 요청을 한 번에 보내지 마세요

## 문제 해결

### "Unauthorized" 오류
- API 키가 올바른지 확인
- Integration이 페이지에 연결되어 있는지 확인

### "Parent page not found" 오류
- 페이지 ID가 올바른지 확인
- Integration이 해당 페이지에 접근 권한이 있는지 확인

### 마크다운이 제대로 변환되지 않음
- Notion은 모든 마크다운을 지원하지 않습니다
- 복잡한 형식은 수동으로 수정 필요

## 참고 자료

- [Notion API 문서](https://developers.notion.com/)
- [notion-client Python 라이브러리](https://github.com/ramnes/notion-sdk-py)

