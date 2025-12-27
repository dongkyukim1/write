"""
간단한 대본 생성 스크립트
명령줄 인자로 간단하게 대본 생성
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models import get_provider, get_model_config, get_api_key

# 환경 변수 로드
load_dotenv(project_root / ".env")


def generate_script_section(section_type: str, topic: str, additional_info: str = "") -> str:
    """
    대본 섹션 생성
    
    Args:
        section_type: 'opening', 'news', 'talk', 'highlight'
        topic: 주제/이슈
        additional_info: 추가 정보
    
    Returns:
        생성된 대본
    """
    # API 키 확인
    api_key = get_api_key("openai") or get_api_key("claude")
    if not api_key:
        return "❌ 오류: API 키가 설정되지 않았습니다. .env 파일을 확인하세요."
    
    provider_name = "openai" if get_api_key("openai") else "claude"
    config = get_model_config(provider_name, "creative")
    provider = get_provider(provider_name, api_key, config)
    
    prompts = {
        "opening": f"""매불쇼 방송작가처럼 오프닝 멘트를 작성해주세요.

이슈: {topic}
{additional_info}

**최욱 오프닝 멘트:**
- 이번 주 핵심 뉴스/이슈를 한 문장으로
- "이번 주 [핵심 키워드] 때문에 정말 시끄러웠죠?" 형식

**정영진 첫 반응:**
- 반응형 멘트 (웃음, 놀람, 공감)
- "아 진짜 [감탄사]... 이거 어떻게 된 거예요?" 형식

**티키타카 전환:**
- 자연스럽게 본론으로 연결

매불쇼 스타일: 가볍게 시작하되 핵심은 정확히.""",
        
        "news": f"""매불쇼 방송작가처럼 뉴스 요약 섹션을 작성해주세요.

이슈: {topic}
{additional_info}

**최욱:**
"일단 이게 뭔 일이냐면..."
- 핵심 사실들을 쉽고 명확하게 설명

**정영진 반응:**
- 놀람/비꼬기/풍자
- 개인적 경험이나 비유로 연결

매불쇼 스타일: 딱딱하지 않게, 하지만 핵심은 정확히.""",
        
        "talk": f"""매불쇼 방송작가처럼 본격 토크 섹션을 작성해주세요.

토픽: {topic}
{additional_info}

**최욱 입장:**
- 입장 정리, 근거/사례

**정영진 반박/보완:**
- 다른 각도에서 접근
- 풍자/개그 요소

**티키타카 포인트:**
- 웃음 포인트 2-3개
- 진지한 포인트 1개

매불쇼 스타일: 가볍게 시작 → 점점 깊이 들어가기.""",
        
        "highlight": f"""매불쇼 방송작가처럼 하이라이트 구간을 작성해주세요.

이슈: {topic}
{additional_info}

**최욱:**
- 핵심 정리
- 직설적 의견

**정영진:**
- 풍자/비꼬기
- 마무리 멘트

매불쇼 스타일: 가장 강렬한 메시지 전달 구간. 독설과 풍자가 적절히 섞인 톤."""
    }
    
    prompt = prompts.get(section_type, f"매불쇼 스타일로 {topic}에 대한 대본을 작성해주세요.")
    
    try:
        result = provider.generate(prompt, temperature=0.8, max_tokens=1000)
        return result
    except Exception as e:
        return f"❌ 오류 발생: {e}"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python scripts/simple_generate.py <섹션타입> <주제> [추가정보]")
        print()
        print("섹션 타입:")
        print("  opening  - 오프닝 생성")
        print("  news     - 뉴스 요약 생성")
        print("  talk     - 토크 섹션 생성")
        print("  highlight - 하이라이트 생성")
        print()
        print("예시:")
        print('  python scripts/simple_generate.py opening "이번 주 국회 이슈"')
        print('  python scripts/simple_generate.py news "국회 관련 뉴스" "핵심 사실 1, 사실 2"')
        sys.exit(1)
    
    section_type = sys.argv[1]
    topic = sys.argv[2]
    additional_info = sys.argv[3] if len(sys.argv) > 3 else ""
    
    print(f"생성 중... ({section_type})")
    print("-" * 50)
    result = generate_script_section(section_type, topic, additional_info)
    print(result)
    print("-" * 50)

