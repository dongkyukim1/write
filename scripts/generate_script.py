"""
매불쇼 대본 생성 도우미 스크립트
AI를 활용하여 대본의 각 섹션을 채워줍니다.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils import load_prompt_template
from models import get_provider, get_model_config, get_api_key
from models.config.model_config import load_config

# 환경 변수 로드
load_dotenv(project_root / ".env")

# Notion 자동 업로드 (선택사항)
try:
    from utils.notion.notion_client import NotionClient
    NOTION_AVAILABLE = True
except ImportError:
    NOTION_AVAILABLE = False


def generate_opening(issue: str, provider_name: str = "openai") -> dict:
    """
    오프닝 멘트 생성
    
    Args:
        issue: 이번 주 핵심 이슈
        provider_name: 사용할 프로바이더 ('openai' 또는 'claude')
    
    Returns:
        최욱과 정영진의 오프닝 멘트 딕셔너리
    """
    prompt = f"""당신은 매불쇼 방송작가입니다. 
이번 주 핵심 이슈: {issue}

다음 형식으로 오프닝 멘트를 작성해주세요:

**최욱 오프닝 멘트:**
- 이번 주 핵심 뉴스/이슈를 한 문장으로 시작
- "이번 주 [핵심 키워드] 때문에 정말 시끄러웠죠?" 형식
- 가볍고 자연스럽게

**정영진 첫 반응:**
- 반응형 멘트 (웃음, 놀람, 공감 등)
- "아 진짜 [감탄사/반응]... 이거 어떻게 된 거예요?" 형식
- 자연스러운 반응

**티키타카 전환:**
- 최욱: 가볍게 시작하는 멘트
- 정영진: 받아치는 멘트
- 자연스럽게 본론으로 연결되는 흐름

매불쇼 스타일: 가볍게 시작하되 핵심은 정확히, 풍자와 유머가 적절히 섞인 톤으로 작성해주세요.
"""
    
    config = get_model_config(provider_name, "creative")
    api_key = get_api_key(provider_name)
    
    if not api_key:
        raise ValueError(f"{provider_name} API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
    
    provider = get_provider(provider_name, api_key, config)
    result = provider.generate(prompt, temperature=0.8, max_tokens=500)
    
    return {"result": result, "issue": issue}


def generate_news_summary(issue: str, facts: list, provider_name: str = "openai") -> str:
    """
    뉴스 요약 섹션 생성
    
    Args:
        issue: 이슈 제목
        facts: 핵심 사실 리스트
        provider_name: 사용할 프로바이더
    
    Returns:
        뉴스 요약 대본
    """
    facts_text = "\n".join([f"- {fact}" for fact in facts])
    
    prompt = f"""당신은 매불쇼 방송작가입니다.

이슈: {issue}

핵심 사실:
{facts_text}

다음 형식으로 뉴스 요약 섹션을 작성해주세요:

**최욱:**
"일단 이게 뭔 일이냐면..."
- 핵심 사실들을 쉽고 명확하게 설명
- 시청자가 모를 수 있으니 배경 설명 포함

**정영진 반응:**
- 놀람/비꼬기/풍자
- 개인적 경험이나 비유로 연결
- 자연스러운 반응

매불쇼 스타일: 딱딱하지 않게, 하지만 핵심은 정확히 전달하는 톤으로 작성해주세요.
"""
    
    config = get_model_config(provider_name, "structured")
    api_key = get_api_key(provider_name)
    provider = get_provider(provider_name, api_key, config)
    result = provider.generate(prompt, temperature=0.7, max_tokens=800)
    
    return result


def generate_talk_section(topic: str, provider_name: str = "openai") -> str:
    """
    본격 토크 섹션 생성
    
    Args:
        topic: 토픽 제목
        provider_name: 사용할 프로바이더
    
    Returns:
        토크 섹션 대본
    """
    prompt = f"""당신은 매불쇼 방송작가입니다.

토픽: {topic}

다음 형식으로 본격 토크 섹션을 작성해주세요:

**최욱 입장:**
- 입장 정리
- 근거/사례 제시

**정영진 반박/보완:**
- 다른 각도에서 접근
- 풍자/개그 요소 포함

**티키타카 포인트:**
- 웃음 포인트 2-3개
- 진지한 포인트 1개

매불쇼 스타일: 가볍게 시작 → 점점 깊이 들어가기. 웃음과 진지함이 적절히 섞인 대화 형식으로 작성해주세요.
"""
    
    config = get_model_config(provider_name, "creative")
    api_key = get_api_key(provider_name)
    provider = get_provider(provider_name, api_key, config)
    result = provider.generate(prompt, temperature=0.8, max_tokens=1000)
    
    return result


def generate_highlight(issue: str, main_points: list, provider_name: str = "openai") -> str:
    """
    하이라이트 구간 생성
    
    Args:
        issue: 이슈 제목
        main_points: 핵심 포인트 리스트
        provider_name: 사용할 프로바이더
    
    Returns:
        하이라이트 구간 대본
    """
    points_text = "\n".join([f"- {point}" for point in main_points])
    
    prompt = f"""당신은 매불쇼 방송작가입니다.

이슈: {issue}

핵심 포인트:
{points_text}

다음 형식으로 하이라이트 구간을 작성해주세요:

**최욱:**
- 핵심 정리
- 직설적 의견

**정영진:**
- 풍자/비꼬기
- 마무리 멘트

매불쇼 스타일: 가장 강렬한 메시지 전달 구간. 독설과 풍자가 적절히 섞인, 날카롭지만 재미있는 톤으로 작성해주세요.
"""
    
    config = get_model_config(provider_name, "creative")
    api_key = get_api_key(provider_name)
    provider = get_provider(provider_name, api_key, config)
    result = provider.generate(prompt, temperature=0.9, max_tokens=600)
    
    return result


def main():
    """대화형 대본 생성 도우미"""
    print("=" * 50)
    print("매불쇼 대본 생성 도우미")
    print("=" * 50)
    print()
    
    # API 키 확인
    openai_key = get_api_key("openai")
    claude_key = get_api_key("claude")
    
    if not openai_key and not claude_key:
        print("❌ 오류: API 키가 설정되지 않았습니다.")
        print("   .env 파일에 OPENAI_API_KEY 또는 ANTHROPIC_API_KEY를 설정하세요.")
        return
    
    # 프로바이더 선택
    if openai_key and claude_key:
        provider_choice = input("사용할 프로바이더를 선택하세요 (1: OpenAI, 2: Claude) [1]: ").strip() or "1"
        provider_name = "claude" if provider_choice == "2" else "openai"
    elif openai_key:
        provider_name = "openai"
        print("✅ OpenAI 사용")
    else:
        provider_name = "claude"
        print("✅ Claude 사용")
    
    print()
    print("대본 정보를 입력해주세요:")
    print("-" * 50)
    
    # 기본 정보 입력
    episode_title = input("에피소드 제목: ").strip()
    broadcast_date = input("방송일 (YYYY-MM-DD): ").strip()
    main_topic = input("메인 토픽: ").strip()
    
    print()
    print("오프닝 생성 중...")
    opening = generate_opening(main_topic, provider_name)
    print("✅ 오프닝 생성 완료")
    print()
    
    # 뉴스 요약
    print("뉴스 요약 섹션을 생성하시겠습니까? (y/n) [y]: ", end="")
    if input().strip().lower() != "n":
        print("핵심 사실을 입력하세요 (한 줄씩, 빈 줄로 종료):")
        facts = []
        while True:
            fact = input("  사실: ").strip()
            if not fact:
                break
            facts.append(fact)
        
        if facts:
            print("뉴스 요약 생성 중...")
            news_summary = generate_news_summary(main_topic, facts, provider_name)
            print("✅ 뉴스 요약 생성 완료")
            print()
    
    # 결과 출력
    print()
    print("=" * 50)
    print("생성된 대본")
    print("=" * 50)
    print()
    print(f"**에피소드 제목:** {episode_title}")
    print(f"**방송일:** {broadcast_date}")
    print(f"**주제:** {main_topic}")
    print()
    print("## 오프닝")
    print(opening["result"])
    print()
    
    if 'news_summary' in locals():
        print("## 뉴스 요약 섹션")
        print(news_summary)
        print()
    
    # Notion 자동 업로드 (설정되어 있으면)
    if NOTION_AVAILABLE:
        try:
            config = load_config()
            notion_config = config.get("notion", {})
            auto_upload = notion_config.get("auto_upload", False)
            parent_url = notion_config.get("default_parent_url")
            
            if auto_upload and parent_url:
                print("\nNotion에 자동 업로드 중...")
                client = NotionClient()
                parent_id = client.get_page_id_from_url(parent_url)
                
                # 대본 내용 조합
                script_content = f"""# {episode_title}

**방송일:** {broadcast_date}
**주제:** {main_topic}

## 오프닝

{opening["result"]}

"""
                if 'news_summary' in locals():
                    script_content += f"""## 뉴스 요약 섹션

{news_summary}

"""
                
                page = client.create_page(
                    parent_page_id=parent_id,
                    title=f"{episode_title} - {broadcast_date}",
                    content=script_content
                )
                print(f"[OK] Notion 페이지 생성 완료!")
                print(f"   URL: {page.get('url', 'N/A')}")
        except Exception as e:
            print(f"\n[WARNING] Notion 업로드 실패: {e}")
            print("   (대본은 정상적으로 생성되었습니다)")
    
    print("=" * 50)
    print("생성 완료!")
    print("=" * 50)
    print()
    print("팁: 생성된 내용을 ep1.md 파일에 복사하여 사용하세요.")


if __name__ == "__main__":
    # Windows 콘솔 인코딩 설정
    import sys
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n작업이 취소되었습니다.")
    except EOFError:
        print("\n\n대화형 입력이 필요합니다. 터미널에서 직접 실행해주세요.")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()

