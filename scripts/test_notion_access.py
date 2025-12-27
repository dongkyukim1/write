"""
Notion 페이지 접근 테스트
Integration이 제대로 연결되었는지 확인
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv(project_root / ".env")

def test_notion_page_access():
    """Notion 페이지 접근 테스트"""
    print("=" * 60)
    print("Notion 페이지 접근 테스트")
    print("=" * 60)
    print()
    
    # API 키 확인
    api_key = os.getenv("NOTION_API_KEY")
    if not api_key:
        print("[ERROR] NOTION_API_KEY가 설정되지 않았습니다.")
        return False
    
    print(f"[OK] API 키 확인됨: {api_key[:20]}...")
    
    # 클라이언트 초기화
    try:
        from utils.notion.notion_client import NotionClient
        client = NotionClient()
        print("[OK] NotionClient 초기화 성공")
    except Exception as e:
        print(f"[ERROR] NotionClient 초기화 실패: {e}")
        return False
    
    # 페이지 ID 추출
    test_url = "https://www.notion.so/2d2e7fbfc5a78081840fdc817d264771?source=copy_link"
    page_id = client.get_page_id_from_url(test_url)
    print(f"\n페이지 ID: {page_id}")
    
    # 페이지 접근 테스트
    print("\n페이지 접근 테스트 중...")
    try:
        page = client.client.pages.retrieve(page_id)
        print("[OK] 페이지 접근 성공!")
        
        # 페이지 정보 출력
        properties = page.get('properties', {})
        title_prop = properties.get('title', {})
        if title_prop:
            title_array = title_prop.get('title', [])
            if title_array:
                page_title = title_array[0].get('plain_text', 'N/A')
                print(f"   페이지 제목: {page_title}")
        
        print(f"   페이지 URL: {page.get('url', 'N/A')}")
        
        # 하위 페이지 생성 테스트
        print("\n하위 페이지 생성 테스트 중...")
        test_page = client.create_page(
            parent_page_id=page_id,
            title="테스트 페이지 - 자동 생성",
            content="이것은 테스트 페이지입니다."
        )
        
        print("[OK] 하위 페이지 생성 성공!")
        print(f"   생성된 페이지 URL: {test_page.get('url', 'N/A')}")
        print("\n[OK] 모든 테스트 통과!")
        print("\n이제 대본/소설 생성 시 자동으로 Notion에 업로드됩니다.")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n[ERROR] 페이지 접근 실패: {error_msg}")
        
        if "Could not find page" in error_msg:
            print("\n해결 방법:")
            print("1. Notion 페이지를 열기")
            print("   https://www.notion.so/2d2e7fbfc5a78081840fdc817d264771")
            print("2. 우측 상단 '...' 메뉴 클릭")
            print("3. 'Connections' → 'Add connections' 클릭")
            print("4. 만든 Integration 선택")
            print("5. 다시 테스트")
        elif "Unauthorized" in error_msg:
            print("\n해결 방법:")
            print("1. .env 파일의 NOTION_API_KEY 확인")
            print("2. Notion Integration 페이지에서 새 토큰 생성")
            print("3. .env 파일 업데이트")
        
        return False


if __name__ == "__main__":
    try:
        test_notion_page_access()
    except Exception as e:
        print(f"\n[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()

