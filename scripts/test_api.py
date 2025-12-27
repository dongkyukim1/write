"""
API 연동 테스트 스크립트
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 환경 변수 로드
load_dotenv(project_root / ".env")

from models import get_provider, get_model_config, get_api_key

def test_api():
    """API 연동 테스트"""
    print("=" * 50)
    print("API 연동 테스트")
    print("=" * 50)
    print()
    
    # API 키 확인
    openai_key = get_api_key("openai")
    claude_key = get_api_key("claude")
    
    if not openai_key and not claude_key:
        print("오류: API 키가 설정되지 않았습니다.")
        return False
    
    # 테스트할 프로바이더 선택
    if openai_key:
        print("OpenAI 테스트 중...")
        try:
            config = get_model_config("openai", "creative")
            provider = get_provider("openai", openai_key, config)
            
            test_prompt = "매불쇼 스타일로 '이번 주 날씨가 추웠다'는 주제로 짧은 오프닝 멘트를 작성해주세요. (2-3문장)"
            result = provider.generate(test_prompt, temperature=0.8, max_tokens=200)
            
            print("성공!")
            print("-" * 50)
            print(result)
            print("-" * 50)
            return True
        except Exception as e:
            print(f"오류: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    if claude_key:
        print("Claude 테스트 중...")
        try:
            config = get_model_config("claude", "creative")
            provider = get_provider("claude", claude_key, config)
            
            test_prompt = "매불쇼 스타일로 '이번 주 날씨가 추웠다'는 주제로 짧은 오프닝 멘트를 작성해주세요. (2-3문장)"
            result = provider.generate(test_prompt, temperature=0.8, max_tokens=200)
            
            print("성공!")
            print("-" * 50)
            print(result)
            print("-" * 50)
            return True
        except Exception as e:
            print(f"오류: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return False

if __name__ == "__main__":
    try:
        success = test_api()
        if success:
            print("\nAPI 연동이 정상적으로 작동합니다!")
        else:
            print("\nAPI 연동에 문제가 있습니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()

