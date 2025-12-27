"""
Notion 자동 업로드 설정 스크립트
"""

import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent

def setup_notion_auto():
    """Notion 자동 업로드 설정"""
    print("=" * 60)
    print("Notion 자동 업로드 설정")
    print("=" * 60)
    print()
    
    # 설정 파일 경로
    config_file = project_root / "config" / "settings.json"
    
    # 현재 설정 로드
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {}
    
    # Notion 설정 확인
    if "notion" not in config:
        config["notion"] = {}
    
    # 기본 URL 설정
    default_url = "https://www.notion.so/2d2e7fbfc5a78081840fdc817d264771?source=copy_link"
    
    print(f"현재 설정:")
    print(f"  부모 페이지 URL: {config['notion'].get('default_parent_url', '설정 안 됨')}")
    print(f"  자동 업로드: {config['notion'].get('auto_upload', False)}")
    print()
    
    # URL 확인
    current_url = config['notion'].get('default_parent_url', default_url)
    print(f"부모 페이지 URL을 설정하세요:")
    print(f"  (Enter로 기본값 사용: {default_url})")
    new_url = input("URL: ").strip()
    
    if new_url:
        config['notion']['default_parent_url'] = new_url
    elif not current_url:
        config['notion']['default_parent_url'] = default_url
    
    # 자동 업로드 활성화
    print()
    print("자동 업로드를 활성화하시겠습니까? (y/n) [y]: ", end="")
    auto_upload_choice = input().strip().lower()
    
    if auto_upload_choice == 'n':
        config['notion']['auto_upload'] = False
        print("자동 업로드가 비활성화되었습니다.")
    else:
        config['notion']['auto_upload'] = True
        print("자동 업로드가 활성화되었습니다.")
    
    # 설정 저장
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print()
    print("=" * 60)
    print("설정 완료!")
    print("=" * 60)
    print()
    print("이제 대본/소설을 생성하면 자동으로 Notion에 업로드됩니다.")
    print()
    print("주의사항:")
    print("1. Notion 페이지에 Integration이 연결되어 있어야 합니다")
    print("2. .env 파일에 NOTION_API_KEY가 설정되어 있어야 합니다")


if __name__ == "__main__":
    try:
        setup_notion_auto()
    except KeyboardInterrupt:
        print("\n\n설정이 취소되었습니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()


