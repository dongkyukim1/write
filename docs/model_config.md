# 모델 설정 가이드

LLM 모델 설정 및 사용 방법을 안내합니다.

## 설정 파일 구조

`config/settings.json` 파일에서 모델 설정을 관리합니다.

```json
{
  "default_model": {
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

## 주요 설정 항목

### temperature (0.0 ~ 2.0)
- **낮은 값 (0.0 ~ 0.5)**: 일관되고 예측 가능한 출력
  - 구조화된 내용, 사실 기반 작성에 적합
- **중간 값 (0.6 ~ 0.8)**: 균형잡힌 창의성
  - 일반적인 창작 작업에 적합
- **높은 값 (0.9 ~ 2.0)**: 매우 창의적이고 다양함
  - 실험적 작품, 다양한 아이디어 생성에 적합

### max_tokens
- 생성할 최대 토큰 수
- 토큰 ≈ 단어 수의 0.75배 (한글 기준)
- 예: 2000 tokens ≈ 1500 단어

## 모델 타입별 추천 설정

### 창의적 작업 (Creative)
```json
{
  "temperature": 0.9,
  "max_tokens": 3000
}
```
- 소설, 시, 창의적 대본 작성

### 구조화된 작업 (Structured)
```json
{
  "temperature": 0.5,
  "max_tokens": 2000
}
```
- 대본 구조, 플롯 구성, 체크리스트 작성

### 빠른 작업 (Fast)
```json
{
  "temperature": 0.7,
  "max_tokens": 1500
}
```
- 아이디어 생성, 요약, 간단한 작성

## API 키 설정

1. `.env.example` 파일을 `.env`로 복사
2. API 키 입력:
```bash
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=your-key-here
```

3. 환경 변수로 로드:
```python
from dotenv import load_dotenv
load_dotenv("config/.env")
```

## 모델 선택 가이드

### OpenAI GPT-4
- **장점**: 강력한 창의성, 긴 컨텍스트
- **단점**: 비용이 높음
- **적합한 작업**: 장편 소설, 복잡한 플롯

### OpenAI GPT-3.5-turbo
- **장점**: 빠르고 저렴
- **단점**: 창의성 제한적
- **적합한 작업**: 간단한 대본, 요약

### Claude (Anthropic)
- **장점**: 긴 컨텍스트, 안전한 출력
- **단점**: 창의성 제한적일 수 있음
- **적합한 작업**: 논리적 구조, 사실 기반

## 사용 예시

```python
from models.config.model_config import get_model_config, get_api_key
from models.providers import get_provider

# 설정 로드
config = get_model_config("openai", "creative")
api_key = get_api_key("openai")

# 프로바이더 생성
provider = get_provider("openai", api_key, config)

# 텍스트 생성
result = provider.generate(
    prompt="소설의 첫 문장을 써주세요",
    temperature=config["temperature"],
    max_tokens=config["max_tokens"]
)
```

## 비용 최적화

1. **짧은 작업**: GPT-3.5-turbo 사용
2. **긴 작업**: 필요한 부분만 GPT-4 사용
3. **반복 작업**: 결과를 캐시하여 재사용
4. **토큰 관리**: max_tokens를 적절히 설정

