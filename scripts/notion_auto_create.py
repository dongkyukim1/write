"""
Notion 자동 페이지 생성 스크립트
생성된 대본/소설을 Notion 페이지로 자동 생성합니다.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv(project_root / ".env")

try:
    from utils.notion.notion_client import NotionClient
except ImportError as e:
    print(f"오류: {e}")
    print("notion-client 패키지를 설치하세요: pip install notion-client")
    sys.exit(1)


def create_script_page(notion_url: str, script_file: Path, title: Optional[str] = None):
    """
    방송 대본을 Notion 페이지로 생성
    
    Args:
        notion_url: 부모 Notion 페이지 URL
        script_file: 대본 파일 경로
        title: 페이지 제목 (없으면 파일명 사용)
    """
    try:
        client = NotionClient()
        parent_id = client.get_page_id_from_url(notion_url)
        
        # 파일 읽기
        with open(script_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 제목 설정
        if not title:
            title = script_file.stem
        
        # 페이지 생성
        print(f"Notion 페이지 생성 중: {title}")
        page = client.create_page(
            parent_page_id=parent_id,
            title=title,
            content=content
        )
        
        print(f"[OK] 페이지 생성 완료!")
        print(f"   URL: {page.get('url', 'N/A')}")
        return page
    
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_novel_chapter_page(notion_url: str, novel_id: str, chapter_num: int):
    """
    소설 챕터를 Notion 페이지로 생성
    
    Args:
        notion_url: 부모 Notion 페이지 URL
        novel_id: 소설 ID
        chapter_num: 챕터 번호
    """
    try:
        client = NotionClient()
        parent_id = client.get_page_id_from_url(notion_url)
        
        # 챕터 파일 읽기
        chapter_file = project_root / "novels" / novel_id / "chapters" / f"chapter_{chapter_num:03d}.md"
        
        if not chapter_file.exists():
            print(f"❌ 챕터 파일을 찾을 수 없습니다: {chapter_file}")
            return None
        
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 체크포인트에서 소설 정보 가져오기
        checkpoint_file = project_root / "novels" / novel_id / "checkpoints" / f"{novel_id}_checkpoint.json"
        novel_title = novel_id
        if checkpoint_file.exists():
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
                novel_title = checkpoint.get('title', novel_id)
        
        # 페이지 제목
        title = f"{novel_title} - 챕터 {chapter_num}"
        
        # 페이지 생성
        print(f"Notion 페이지 생성 중: {title}")
        page = client.create_page(
            parent_page_id=parent_id,
            title=title,
            content=content
        )
        
        print(f"[OK] 페이지 생성 완료!")
        print(f"   URL: {page.get('url', 'N/A')}")
        return page
    
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_novel_summary_page(notion_url: str, novel_id: str):
    """
    소설 요약 페이지 생성
    
    Args:
        notion_url: 부모 Notion 페이지 URL
        novel_id: 소설 ID
    """
    try:
        client = NotionClient()
        parent_id = client.get_page_id_from_url(notion_url)
        
        # 체크포인트 읽기
        checkpoint_file = project_root / "novels" / novel_id / "checkpoints" / f"{novel_id}_checkpoint.json"
        
        if not checkpoint_file.exists():
            print(f"❌ 체크포인트 파일을 찾을 수 없습니다: {checkpoint_file}")
            return None
        
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
        
        # 요약 내용 생성
        title = checkpoint.get('title', novel_id)
        genre = checkpoint.get('genre', 'N/A')
        chapters = checkpoint.get('chapters', [])
        
        content = f"""# {title}

## 기본 정보
- 장르: {genre}
- 총 챕터: {len(chapters)}개
- 생성일: {checkpoint.get('last_updated', 'N/A')}

## 세계관 설정
{checkpoint.get('world_setting', 'N/A')}

## 등장인물
"""
        for char_name, char_info in checkpoint.get('characters', {}).items():
            content += f"- **{char_name}**: {char_info.get('description', 'N/A')}\n"
        
        content += "\n## 플롯 구조\n"
        content += checkpoint.get('plot_outline', 'N/A')
        
        content += "\n## 챕터 목록\n"
        for ch in chapters:
            content += f"- 챕터 {ch.get('chapter', 'N/A')}: {ch.get('goal', 'N/A')}\n"
        
        # 페이지 생성
        print(f"Notion 요약 페이지 생성 중: {title}")
        page = client.create_page(
            parent_page_id=parent_id,
            title=f"{title} - 요약",
            content=content
        )
        
        print(f"[OK] 페이지 생성 완료!")
        print(f"   URL: {page.get('url', 'N/A')}")
        return page
    
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Notion 페이지 자동 생성')
    parser.add_argument('notion_url', help='부모 Notion 페이지 URL')
    parser.add_argument('--type', choices=['script', 'chapter', 'summary'], 
                       required=True, help='생성할 페이지 타입')
    parser.add_argument('--script-file', type=Path, help='대본 파일 (script 타입일 때)')
    parser.add_argument('--title', help='페이지 제목')
    parser.add_argument('--novel-id', help='소설 ID (chapter/summary 타입일 때)')
    parser.add_argument('--chapter', type=int, help='챕터 번호 (chapter 타입일 때)')
    
    args = parser.parse_args()
    
    if args.type == 'script':
        if not args.script_file:
            print("❌ 오류: --script-file이 필요합니다.")
            return
        create_script_page(args.notion_url, args.script_file, args.title)
    
    elif args.type == 'chapter':
        if not args.novel_id or not args.chapter:
            print("❌ 오류: --novel-id와 --chapter가 필요합니다.")
            return
        create_novel_chapter_page(args.notion_url, args.novel_id, args.chapter)
    
    elif args.type == 'summary':
        if not args.novel_id:
            print("❌ 오류: --novel-id가 필요합니다.")
            return
        create_novel_summary_page(args.notion_url, args.novel_id)


if __name__ == "__main__":
    main()

