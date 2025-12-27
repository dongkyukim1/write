# 스크립트 정리 가이드

## 주요 스크립트 (유지)

### 대본/소설 생성
- `generate_script.py` - 방송 대본 생성
- `long_form_novel_generator.py` - 장편 소설 생성
- `simple_generate.py` - 간단한 명령줄 생성
- `batch_generate.py` - 배치 챕터 생성

### 관리 도구
- `backup_restore.py` - 백업/복원
- `analyze_novel.py` - 소설 분석
- `notion_auto_create.py` - Notion 페이지 생성
- `setup_notion_auto.py` - Notion 자동 업로드 설정

### 테스트 (필요시 사용)
- `test_api.py` - API 연결 테스트
- `test_mcp.py` - MCP 서버 테스트
- `test_notion_access.py` - Notion 접근 테스트
- `check_notion_config.py` - Notion 설정 확인

## 삭제된 파일

다음 파일들은 정리되었습니다:
- `test_notion_create.py` - 중복
- `test_notion.py` - 중복
- `test_auto_upload.py` - 중복
- `quick_test_script.py` - 임시 테스트용
- `show_notion_page_id.py` - 디버깅용
- `notion_setup_guide.py` - 중복

## 캐시 파일

`__pycache__` 폴더는 자동으로 생성되므로 삭제해도 됩니다.
`.gitignore`에 포함되어 있어 Git에 커밋되지 않습니다.


