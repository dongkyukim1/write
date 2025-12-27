# 설정 파일 가이드

## 환경 변수 설정

AI 모델을 사용하려면 API 키가 필요합니다. `.env` 파일을 생성하여 설정하세요.

### .env 파일 생성

프로젝트 루트에 `.env` 파일을 만들고 다음 내용을 입력하세요:

```bash
# OpenAI API 키
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Claude API 키
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# 기본 설정
DEFAULT_MODEL_PROVIDER=openai
DEFAULT_MODEL_NAME=gpt-4
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=2000
```

### 주의사항

- `.env` 파일은 Git에 커밋하지 마세요 (민감 정보 포함)
- 실제 API 키를 입력하세요
- 파일명은 정확히 `.env`여야 합니다

## settings.json

모델별 상세 설정은 `settings.json` 파일에서 관리합니다.

### 설정 항목 설명

- **temperature**: 창의성 수준 (0.0 ~ 2.0)
- **max_tokens**: 최대 생성 토큰 수
- **model**: 사용할 모델 이름

### 모델 타입

- **creative**: 창의적 작업용 (temperature: 0.9)
- **structured**: 구조화된 작업용 (temperature: 0.5)
- **fast**: 빠른 작업용 (temperature: 0.7)

