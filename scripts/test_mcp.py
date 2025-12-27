"""
MCP 서버 연결 테스트 스크립트
"""

import sys
import time
import requests
from pathlib import Path
from threading import Thread

# Windows 콘솔 인코딩 설정
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp_server.mcp_server import MCPServer, run_mcp_server


def test_mcp_server_direct():
    """MCP 서버 직접 테스트 (서버 실행 없이)"""
    print("=" * 60)
    print("MCP 서버 직접 테스트")
    print("=" * 60)
    print()
    
    try:
        server = MCPServer()
        
        # 프로바이더 목록 확인
        providers = server.list_providers()
        print(f"[OK] 사용 가능한 프로바이더: {providers}")
        
        if not providers:
            print("[WARNING] 경고: 사용 가능한 프로바이더가 없습니다.")
            print("   .env 파일에 API 키가 설정되어 있는지 확인하세요.")
            return False
        
        # 프로바이더 정보 확인
        for provider in providers:
            info = server.get_provider_info(provider)
            print(f"\n[{provider}] 정보:")
            print(f"   모델: {info.get('model', 'N/A')}")
            print(f"   Temperature: {info.get('temperature', 'N/A')}")
            print(f"   Max Tokens: {info.get('max_tokens', 'N/A')}")
        
        # 간단한 텍스트 생성 테스트
        import asyncio
        print("\n[TEST] 텍스트 생성 테스트...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            server.generate_text(
                "한 문장으로 '안녕하세요'라고 인사해주세요.",
                provider=providers[0],
                temperature=0.7,
                max_tokens=50
            )
        )
        loop.close()
        
        if result.get("success"):
            print(f"[OK] 생성 성공!")
            print(f"   결과: {result.get('text', '')[:100]}...")
            return True
        else:
            print(f"[ERROR] 생성 실패: {result.get('error', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mcp_server_http(port=8001, timeout=5):
    """MCP HTTP 서버 테스트"""
    print("\n" + "=" * 60)
    print("MCP HTTP 서버 테스트")
    print("=" * 60)
    print()
    
    # 서버를 별도 스레드에서 실행
    server_thread = Thread(target=run_mcp_server, args=(port,), daemon=True)
    server_thread.start()
    
    # 서버 시작 대기
    print(f"서버 시작 대기 중... (최대 {timeout}초)")
    time.sleep(2)
    
    try:
        # 헬스 체크
        print("1. 헬스 체크...")
        response = requests.get(f"http://localhost:{port}/health", timeout=2)
        if response.status_code == 200:
            print("   [OK] 헬스 체크 성공")
        else:
            print(f"   [ERROR] 헬스 체크 실패: {response.status_code}")
            return False
        
        # 프로바이더 목록 조회
        print("2. 프로바이더 목록 조회...")
        response = requests.get(f"http://localhost:{port}/providers", timeout=2)
        if response.status_code == 200:
            data = response.json()
            providers = data.get("providers", [])
            print(f"   [OK] 프로바이더: {providers}")
            if not providers:
                print("   [WARNING] 경고: 사용 가능한 프로바이더가 없습니다.")
                return False
        else:
            print(f"   [ERROR] 실패: {response.status_code}")
            return False
        
        # 텍스트 생성 테스트
        print("3. 텍스트 생성 테스트...")
        response = requests.post(
            f"http://localhost:{port}",
            json={
                "action": "generate",
                "prompt": "한 문장으로 '안녕하세요'라고 인사해주세요.",
                "provider": providers[0],
                "temperature": 0.7,
                "max_tokens": 50
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"   [OK] 생성 성공!")
                print(f"   결과: {data.get('text', '')[:100]}...")
                return True
            else:
                print(f"   [ERROR] 생성 실패: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   [ERROR] HTTP 오류: {response.status_code}")
            print(f"   응답: {response.text[:200]}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("   [ERROR] 서버에 연결할 수 없습니다.")
        print("   서버가 시작되지 않았거나 포트가 사용 중일 수 있습니다.")
        return False
    except Exception as e:
        print(f"   [ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """메인 함수"""
    print("MCP 서버 연결 테스트")
    print("=" * 60)
    print()
    
    # 직접 테스트
    direct_success = test_mcp_server_direct()
    
    if not direct_success:
        print("\n[WARNING] 직접 테스트 실패. HTTP 서버 테스트를 건너뜁니다.")
        print("\n해결 방법:")
        print("   1. .env 파일에 API 키가 설정되어 있는지 확인")
        print("   2. python scripts/test_api.py 로 API 키 확인")
        return
    
    # HTTP 서버 테스트 (선택사항)
    print("\nHTTP 서버 테스트를 진행하시겠습니까? (y/n): ", end="")
    try:
        choice = input().strip().lower()
        if choice == 'y':
            http_success = test_mcp_server_http()
            if http_success:
                print("\n[OK] 모든 테스트 통과!")
            else:
                print("\n[WARNING] HTTP 서버 테스트 실패")
        else:
            print("\nHTTP 서버 테스트를 건너뜁니다.")
    except:
        # 대화형 입력이 불가능한 경우 자동으로 테스트
        print("\nHTTP 서버 테스트를 자동으로 진행합니다...")
        http_success = test_mcp_server_http()
    
    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n테스트가 취소되었습니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()

