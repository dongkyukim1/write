# Notion 자동 업로드 가이드

생성된 대본/소설이 자동으로 Notion 페이지 하위 페이지로 생성됩니다.

## 설정 완료

✅ **부모 페이지 URL**: https://www.notion.so/2d2e7fbfc5a78081840fdc817d264771  
✅ **자동 업로드**: 활성화됨

## 작동 방식

### 방송 대본 생성 시
```bash
python scripts/generate_script.py
```

대본 생성 후 자동으로:
- 부모 페이지 하위에 새 페이지 생성
- 제목: "{에피소드 제목} - {방송일}"
- 내용: 생성된 대본 전체

### 소설 챕터 생성 시
```bash
python scripts/long_form_novel_generator.py
```

챕터 생성 후 자동으로:
- 부모 페이지 하위에 새 페이지 생성
- 제목: "{소설 제목} - 챕터 {번호}"
- 내용: 생성된 챕터 전체

## 설정 변경

### 자동 업로드 끄기
`config/settings.json` 파일에서:
```json
{
  "notion": {
    "auto_upload": false
  }
}
```

### 부모 페이지 URL 변경
`config/settings.json` 파일에서:
```json
{
  "notion": {
    "default_parent_url": "새로운_URL"
  }
}
```

## 확인 방법

설정 확인:
```bash
python scripts/check_notion_config.py
```

## 주의사항

⚠️ **Integration 연결 필수**
- Notion 페이지에 Integration이 연결되어 있어야 합니다
- 연결 방법: 페이지 → "..." → "Connections" → Integration 선택

⚠️ **API 키 필요**
- `.env` 파일에 `NOTION_API_KEY`가 설정되어 있어야 합니다

⚠️ **업로드 실패 시**
- 대본/소설은 정상적으로 생성됩니다
- Notion 업로드만 실패한 경우 경고 메시지가 표시됩니다
- 오류 메시지를 확인하여 문제를 해결하세요

## 문제 해결

### "Could not find page" 오류
→ 페이지에 Integration이 연결되지 않았습니다. 연결하세요.

### "Unauthorized" 오류
→ API 키가 잘못되었거나 만료되었습니다. 확인하세요.

### 업로드가 안 됨
→ `config/settings.json`에서 `auto_upload`가 `true`인지 확인하세요.


