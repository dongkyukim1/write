"""
컨텍스트 빌더 서비스
AI가 대본 생성 시 참조할 컨텍스트를 구성합니다.

MCP의 핵심 기능: AI에게 허용된 세계관/규칙/캐릭터 정보 제공
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
from sqlalchemy.orm import Session

import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.database.crud import (
    get_project, get_episode, get_episodes_by_project,
    get_scenes_by_episode, get_characters_by_project,
    get_callbacks_by_project, get_scene
)


class ContextBuilder:
    """
    컨텍스트 빌더
    
    AI가 대본 생성 시 참조할 모든 컨텍스트를 구성합니다.
    - 세계관 설정
    - 캐릭터 정보 및 규칙
    - 이전 장면 요약
    - 미해결 복선
    - 스타일 가이드
    """
    
    def __init__(self, db: Session):
        """
        Args:
            db: 데이터베이스 세션
        """
        self.db = db
    
    def build_full_context(self, 
                          project_id: int,
                          episode_id: Optional[int] = None,
                          current_scene_number: Optional[int] = None) -> Dict[str, Any]:
        """
        전체 컨텍스트를 빌드합니다.
        
        Args:
            project_id: 프로젝트 ID
            episode_id: 현재 에피소드 ID (선택)
            current_scene_number: 현재 장면 번호 (선택)
        
        Returns:
            AI에게 전달할 전체 컨텍스트
        """
        project = get_project(self.db, project_id)
        if not project:
            raise ValueError(f"프로젝트 ID {project_id}를 찾을 수 없습니다.")
        
        context = {
            "project": self._build_project_context(project),
            "world_rules": self._build_world_rules(project),
            "characters": self._build_characters_context(project_id),
            "style_guide": self._build_style_guide(project),
            "forbidden_elements": self._build_forbidden_list(project_id)
        }
        
        # 에피소드 컨텍스트
        if episode_id:
            context["episode"] = self._build_episode_context(episode_id)
            context["previous_scenes"] = self._build_previous_scenes_context(
                episode_id, current_scene_number
            )
        
        # 미해결 복선
        context["unresolved_callbacks"] = self._build_callbacks_context(project_id)
        
        return context
    
    def build_prompt_context(self, 
                            project_id: int,
                            episode_id: Optional[int] = None,
                            scene_goal: Optional[str] = None,
                            target_characters: Optional[List[int]] = None) -> str:
        """
        프롬프트에 삽입할 컨텍스트 문자열을 생성합니다.
        
        Args:
            project_id: 프로젝트 ID
            episode_id: 에피소드 ID
            scene_goal: 장면 목표
            target_characters: 참여할 캐릭터 ID 목록
        
        Returns:
            프롬프트용 컨텍스트 문자열
        """
        context = self.build_full_context(project_id, episode_id)
        
        lines = []
        
        # 프로젝트 정보
        lines.append("## 프로젝트 정보")
        lines.append(f"제목: {context['project']['title']}")
        lines.append(f"장르: {context['project']['genre'] or 'N/A'}")
        lines.append(f"타입: {context['project']['project_type']}")
        lines.append("")
        
        # 세계관 규칙
        if context['world_rules']:
            lines.append("## 세계관 규칙 (반드시 준수)")
            for rule in context['world_rules']:
                lines.append(f"- {rule}")
            lines.append("")
        
        # 캐릭터 정보
        lines.append("## 등장인물")
        characters = context['characters']
        
        # target_characters가 있으면 해당 캐릭터만 필터링
        if target_characters:
            characters = [c for c in characters if c['id'] in target_characters]
        
        for char in characters:
            lines.append(f"### {char['name']} ({char['role']})")
            if char['personality_summary']:
                lines.append(f"성격: {char['personality_summary']}")
            if char['speech_pattern']:
                lines.append(f"말투: {char['speech_pattern']}")
            if char['current_state']:
                lines.append(f"현재 상태: {char['current_state']}")
            if char['forbidden_actions']:
                lines.append(f"금지: {', '.join(char['forbidden_actions'])}")
            lines.append("")
        
        # 스타일 가이드
        if context['style_guide']:
            lines.append("## 문체 가이드")
            lines.append(context['style_guide'])
            lines.append("")
        
        # 금지 요소
        if context['forbidden_elements']:
            lines.append("## 금지 요소 (절대 사용 금지)")
            for item in context['forbidden_elements']:
                lines.append(f"- {item}")
            lines.append("")
        
        # 이전 장면 요약
        if 'previous_scenes' in context and context['previous_scenes']:
            lines.append("## 이전 장면 요약")
            for scene in context['previous_scenes'][-3:]:  # 최근 3개만
                lines.append(f"- 장면 {scene['scene_number']}: {scene['summary']}")
            lines.append("")
        
        # 미해결 복선
        if context['unresolved_callbacks']:
            lines.append("## 미해결 복선 (회수 고려)")
            for callback in context['unresolved_callbacks'][:5]:  # 최근 5개만
                lines.append(f"- {callback['content']}")
            lines.append("")
        
        # 장면 목표
        if scene_goal:
            lines.append("## 이번 장면 목표")
            lines.append(scene_goal)
            lines.append("")
        
        return "\n".join(lines)
    
    def _build_project_context(self, project) -> Dict[str, Any]:
        """프로젝트 기본 정보"""
        return {
            "id": project.id,
            "title": project.title,
            "project_type": project.project_type,
            "genre": project.genre,
            "target_audience": project.target_audience,
            "tone": project.tone
        }
    
    def _build_world_rules(self, project) -> List[str]:
        """세계관 규칙 파싱"""
        if not project.world_setting:
            return []
        
        # 줄바꿈으로 규칙 분리
        rules = [
            line.strip() 
            for line in project.world_setting.split('\n') 
            if line.strip() and not line.strip().startswith('#')
        ]
        return rules
    
    def _build_characters_context(self, project_id: int) -> List[Dict[str, Any]]:
        """캐릭터 컨텍스트 빌드"""
        characters = get_characters_by_project(self.db, project_id)
        
        return [
            {
                "id": char.id,
                "name": char.name,
                "role": char.role,
                "personality_summary": char.personality_description or "",
                "speech_pattern": char.speech_pattern or "",
                "current_state": char.current_state,
                "key_traits": char.personality_traits or [],
                "forbidden_actions": char.forbidden_actions or [],
                "speech_examples": (char.speech_examples or [])[:3]
            }
            for char in characters
        ]
    
    def _build_style_guide(self, project) -> str:
        """스타일 가이드"""
        return project.style_guide or ""
    
    def _build_forbidden_list(self, project_id: int) -> List[str]:
        """금지 요소 목록 (모든 캐릭터의 금지 항목 통합)"""
        characters = get_characters_by_project(self.db, project_id)
        
        forbidden = set()
        for char in characters:
            if char.forbidden_actions:
                for action in char.forbidden_actions:
                    forbidden.add(f"{char.name}: {action}")
        
        return list(forbidden)
    
    def _build_episode_context(self, episode_id: int) -> Dict[str, Any]:
        """에피소드 컨텍스트"""
        episode = get_episode(self.db, episode_id)
        if not episode:
            return {}
        
        return {
            "id": episode.id,
            "episode_number": episode.episode_number,
            "title": episode.title,
            "main_topic": episode.main_topic,
            "sub_topics": episode.sub_topics or [],
            "notes": episode.notes
        }
    
    def _build_previous_scenes_context(self, 
                                       episode_id: int,
                                       current_scene_number: Optional[int] = None) -> List[Dict]:
        """이전 장면들의 요약"""
        scenes = get_scenes_by_episode(self.db, episode_id)
        
        if current_scene_number:
            scenes = [s for s in scenes if s.scene_number < current_scene_number]
        
        return [
            {
                "scene_number": scene.scene_number,
                "scene_type": scene.scene_type,
                "title": scene.title or "",
                "goal": scene.goal or "",
                "summary": self._summarize_content(scene.content),
                "emotion_curve": scene.emotion_curve
            }
            for scene in scenes[-5:]  # 최근 5개만
        ]
    
    def _summarize_content(self, content: str, max_length: int = 150) -> str:
        """내용 요약 (간단 버전)"""
        if not content:
            return ""
        
        # 첫 몇 줄만 추출
        lines = content.split('\n')[:3]
        summary = ' '.join(lines)
        
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return summary
    
    def _build_callbacks_context(self, project_id: int) -> List[Dict]:
        """미해결 복선 목록"""
        callbacks = get_callbacks_by_project(self.db, project_id, resolved=False)
        
        return [
            {
                "id": cb.id,
                "content": cb.content,
                "setup_episode": cb.setup_episode_number,
                "importance": cb.importance
            }
            for cb in callbacks
        ]
    
    def get_character_context_for_scene(self, 
                                        project_id: int,
                                        character_ids: List[int]) -> List[Dict]:
        """
        특정 장면에 참여하는 캐릭터들의 컨텍스트만 추출
        """
        all_characters = self._build_characters_context(project_id)
        return [c for c in all_characters if c['id'] in character_ids]


def get_context_for_generation(db: Session,
                              project_id: int,
                              episode_id: Optional[int] = None,
                              scene_goal: Optional[str] = None,
                              character_ids: Optional[List[int]] = None) -> str:
    """
    대본 생성용 컨텍스트 헬퍼 함수
    
    Args:
        db: 데이터베이스 세션
        project_id: 프로젝트 ID
        episode_id: 에피소드 ID
        scene_goal: 장면 목표
        character_ids: 참여 캐릭터 ID 목록
    
    Returns:
        프롬프트에 삽입할 컨텍스트 문자열
    """
    builder = ContextBuilder(db)
    return builder.build_prompt_context(
        project_id=project_id,
        episode_id=episode_id,
        scene_goal=scene_goal,
        target_characters=character_ids
    )

