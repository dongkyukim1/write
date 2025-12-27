"""
Notion API 클라이언트
Notion 페이지에 자동으로 콘텐츠를 생성합니다.
"""

import os
import json
from typing import Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv

try:
    from notion_client import Client
    NOTION_AVAILABLE = True
except ImportError:
    NOTION_AVAILABLE = False
    print("경고: notion-client가 설치되지 않았습니다. 'pip install notion-client' 실행하세요.")


class NotionClient:
    """Notion API 클라이언트"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: Notion API 키 (없으면 환경 변수에서 로드)
        """
        if not NOTION_AVAILABLE:
            raise ImportError("notion-client 패키지가 필요합니다. 'pip install notion-client' 실행하세요.")
        
        if api_key is None:
            project_root = Path(__file__).parent.parent.parent
            load_dotenv(project_root / ".env")
            api_key = os.getenv("NOTION_API_KEY")
        
        if not api_key:
            raise ValueError("Notion API 키가 필요합니다. .env 파일에 NOTION_API_KEY를 설정하세요.")
        
        self.client = Client(auth=api_key)
    
    def create_page(self, parent_page_id: str, title: str, content: str = "", 
                   properties: Optional[Dict] = None) -> Dict:
        """
        하위 페이지 생성
        
        Args:
            parent_page_id: 부모 페이지 ID (URL에서 복사)
            title: 페이지 제목
            content: 페이지 내용 (마크다운 형식)
            properties: 추가 속성 (선택사항)
        
        Returns:
            생성된 페이지 정보
        """
        # 페이지 속성 설정
        page_properties = {
            "title": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        }
        
        if properties:
            page_properties.update(properties)
        
        # 페이지 생성
        new_page = self.client.pages.create(
            parent={"page_id": parent_page_id},
            properties=page_properties
        )
        
        # 내용이 있으면 블록 추가
        if content:
            self.add_content(new_page["id"], content)
        
        return new_page
    
    def add_content(self, page_id: str, content: str):
        """
        페이지에 내용 추가
        
        Args:
            page_id: 페이지 ID
            content: 추가할 내용 (마크다운 형식)
        """
        # 마크다운을 Notion 블록으로 변환
        blocks = self._markdown_to_blocks(content)
        
        if blocks:
            self.client.blocks.children.append(
                block_id=page_id,
                children=blocks
            )
    
    def _markdown_to_blocks(self, markdown: str) -> List[Dict]:
        """
        마크다운을 Notion 블록으로 변환
        
        Args:
            markdown: 마크다운 텍스트
        
        Returns:
            Notion 블록 리스트
        """
        blocks = []
        lines = markdown.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 제목 처리
            if line.startswith('# '):
                blocks.append({
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"type": "text", "text": {"content": line[2:].strip()}}]
                    }
                })
            elif line.startswith('## '):
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": line[3:].strip()}}]
                    }
                })
            elif line.startswith('### '):
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": line[4:].strip()}}]
                    }
                })
            # 리스트 처리
            elif line.startswith('- ') or line.startswith('* '):
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": line[2:].strip()}}]
                    }
                })
            # 일반 텍스트
            else:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": line}}]
                    }
                })
        
        return blocks
    
    def get_page_id_from_url(self, url: str) -> str:
        """
        Notion URL에서 페이지 ID 추출
        
        Args:
            url: Notion 페이지 URL
        
        Returns:
            페이지 ID (하이픈 포함 형식)
        """
        # URL 형식: https://www.notion.so/Page-Title-2d2e7fbfc5a78081840fdc817d264771
        # 또는: https://www.notion.so/2d2e7fbfc5a78081840fdc817d264771
        
        # 쿼리 파라미터 제거
        if '?' in url:
            url = url.split('?')[0]
        
        # 마지막 부분에서 32자리 hex ID 추출
        parts = url.rstrip('/').split('/')
        last_part = parts[-1]
        
        # 32자리 hex ID 추출 (하이픈 제거된 형식)
        import re
        hex_pattern = r'([0-9a-f]{32})'
        match = re.search(hex_pattern, last_part)
        
        if match:
            page_id = match.group(1)
            # 하이픈 추가 (Notion API 형식: 8-4-4-4-12)
            formatted_id = f"{page_id[:8]}-{page_id[8:12]}-{page_id[12:16]}-{page_id[16:20]}-{page_id[20:]}"
            return formatted_id
        
        # 이미 하이픈이 있는 형식인 경우
        if len(last_part) == 36 and last_part.count('-') == 4:
            return last_part
        
        # 마지막 32자리만 추출 시도
        if len(last_part) >= 32:
            page_id = last_part[-32:]
            formatted_id = f"{page_id[:8]}-{page_id[8:12]}-{page_id[12:16]}-{page_id[16:20]}-{page_id[20:]}"
            return formatted_id
        
        return last_part

