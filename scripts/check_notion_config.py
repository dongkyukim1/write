"""Notion 설정 확인"""

import json
from pathlib import Path

config_file = Path(__file__).parent.parent / "config" / "settings.json"
config = json.load(open(config_file, 'r', encoding='utf-8'))

print("=" * 60)
print("Notion 자동 업로드 설정")
print("=" * 60)
print()
print(f"부모 페이지 URL: {config['notion']['default_parent_url']}")
print(f"자동 업로드: {config['notion']['auto_upload']}")
print()
print("=" * 60)


