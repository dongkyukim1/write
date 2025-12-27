# MCP 서버 사용 가이드

MCP (Model Context Protocol) 서버를 통해 로컬에서 AI 모델과 통신할 수 있습니다.

## 설치

```bash
# 필요한 패키지가 이미 설치되어 있어야 합니다
pip install -r requirements.txt
```

## 실행

```bash
# 기본 포트 (8001)로 실행
python mcp_server/mcp_server.py

# 커스텀 포트로 실행
python mcp_server/mcp_server.py --port 8080
```

## API 사용법

### 1. 텍스트 생성 (POST)

```bash
curl -X POST http://localhost:8001 \
  -H "Content-Type: application/json" \
  -d '{
    "action": "generate",
    "prompt": "매불쇼 스타일로 짧은 멘트를 작성해주세요",
    "provider": "openai",
    "temperature": 0.8,
    "max_tokens": 500
  }'
```

### 2. 프로바이더 목록 조회 (GET)

```bash
curl http://localhost:8001/providers
```

### 3. 헬스 체크 (GET)

```bash
curl http://localhost:8001/health
```

## Python 클라이언트 예시

```python
import requests

# 텍스트 생성
response = requests.post(
    "http://localhost:8001",
    json={
        "action": "generate",
        "prompt": "소설의 첫 문장을 써주세요",
        "provider": "openai",
        "temperature": 0.8,
        "max_tokens": 500
    }
)

result = response.json()
print(result["text"])
```

## 로컬 모델 연동

로컬 모델(Ollama, LM Studio 등)과 연동하려면:

1. 로컬 모델이 HTTP API를 제공하는지 확인
2. `models/providers/base.py`에 로컬 프로바이더 추가
3. MCP 서버에 등록

## 보안 주의사항

- 기본적으로 localhost에서만 접근 가능
- 프로덕션 환경에서는 인증 추가 필요
- API 키는 환경 변수로 관리

