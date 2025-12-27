"""
MCP (Model Context Protocol) 서버 - 고급 버전
Cursor IDE와 통합하여 대본 작성을 지원하는 MCP 서버

핵심 기능:
- 캐릭터/세계관 컨텍스트 자동 제공
- 설정 검증 및 규칙 체크
- 대본 생성 및 평가 도구
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))

from models import get_provider, get_model_config, get_api_key
from models.database import get_db_context, init_db
from models.database.crud import (
    get_project, get_projects, get_characters_by_project,
    get_episode, get_scenes_by_episode, get_callbacks_by_project
)
from services.context_builder import ContextBuilder
from services.evaluator import SceneEvaluator

load_dotenv(project_root / ".env")


class MCPServer:
    """
    MCP 서버 - 향상된 버전
    
    Cursor IDE에서 사용할 수 있는 다양한 도구를 제공합니다.
    """
    
    def __init__(self):
        self.providers = {}
        self._initialize_providers()
        
        # 데이터베이스 초기화
        try:
            init_db()
        except Exception as e:
            print(f"DB 초기화 경고: {e}")
    
    def _initialize_providers(self):
        """프로바이더 초기화"""
        for provider_name in ["openai", "claude"]:
            api_key = get_api_key(provider_name)
            if api_key:
                try:
                    config = get_model_config(provider_name, "creative")
                    self.providers[provider_name] = get_provider(provider_name, api_key, config)
                except Exception as e:
                    print(f"프로바이더 {provider_name} 초기화 실패: {e}")
    
    # ==================== 컨텍스트 도구 ====================
    
    def get_project_context(self, project_id: int) -> Dict[str, Any]:
        """
        프로젝트 전체 컨텍스트 조회
        
        Cursor에서 대본 작성 시 자동으로 세계관과 캐릭터 정보를 로드합니다.
        
        Args:
            project_id: 프로젝트 ID
        
        Returns:
            프로젝트 컨텍스트 (세계관, 캐릭터, 스타일 가이드 등)
        """
        with get_db_context() as db:
            builder = ContextBuilder(db)
            return builder.build_full_context(project_id)
    
    def get_character_context(self, project_id: int, character_names: Optional[List[str]] = None) -> List[Dict]:
        """
        캐릭터 컨텍스트 조회
        
        특정 캐릭터들의 성격, 말투, 금지 설정을 가져옵니다.
        
        Args:
            project_id: 프로젝트 ID
            character_names: 조회할 캐릭터 이름 목록 (None이면 전체)
        
        Returns:
            캐릭터 컨텍스트 목록
        """
        with get_db_context() as db:
            characters = get_characters_by_project(db, project_id)
            
            if character_names:
                characters = [c for c in characters if c.name in character_names]
            
            return [
                {
                    "name": char.name,
                    "role": char.role,
                    "personality": char.personality_description or "",
                    "speech_pattern": char.speech_pattern or "",
                    "speech_examples": char.speech_examples[:3] if char.speech_examples else [],
                    "current_state": char.current_state,
                    "forbidden_actions": char.forbidden_actions or []
                }
                for char in characters
            ]
    
    def get_world_rules(self, project_id: int) -> Dict[str, Any]:
        """
        세계관 규칙 조회
        
        AI가 준수해야 할 세계관 규칙을 가져옵니다.
        
        Args:
            project_id: 프로젝트 ID
        
        Returns:
            세계관 규칙 정보
        """
        with get_db_context() as db:
            project = get_project(db, project_id)
            if not project:
                return {"error": "프로젝트를 찾을 수 없습니다."}
            
            rules = []
            if project.world_setting:
                rules = [
                    line.strip() 
                    for line in project.world_setting.split('\n') 
                    if line.strip() and not line.strip().startswith('#')
                ]
            
            return {
                "project_id": project_id,
                "title": project.title,
                "rules": rules,
                "tone": project.tone,
                "style_guide": project.style_guide
            }
    
    def get_scene_history(self, episode_id: int, limit: int = 5) -> List[Dict]:
        """
        이전 장면 히스토리 조회
        
        현재 에피소드의 이전 장면들을 요약해서 가져옵니다.
        
        Args:
            episode_id: 에피소드 ID
            limit: 가져올 장면 수
        
        Returns:
            이전 장면 요약 목록
        """
        with get_db_context() as db:
            scenes = get_scenes_by_episode(db, episode_id)
            
            return [
                {
                    "scene_number": scene.scene_number,
                    "scene_id": scene.scene_id,
                    "title": scene.title,
                    "goal": scene.goal,
                    "emotion_curve": scene.emotion_curve,
                    "summary": self._summarize(scene.content, 200)
                }
                for scene in scenes[-limit:]
            ]
    
    def get_unresolved_callbacks(self, project_id: int) -> List[Dict]:
        """
        미해결 복선 조회
        
        회수되지 않은 복선/떡밥 목록을 가져옵니다.
        
        Args:
            project_id: 프로젝트 ID
        
        Returns:
            미해결 복선 목록
        """
        with get_db_context() as db:
            callbacks = get_callbacks_by_project(db, project_id, resolved=False)
            
            return [
                {
                    "id": cb.id,
                    "content": cb.content,
                    "setup_episode": cb.setup_episode_number,
                    "importance": cb.importance
                }
                for cb in callbacks
            ]
    
    # ==================== 검증 도구 ====================
    
    def validate_scene(self, project_id: int, content: str) -> Dict[str, Any]:
        """
        장면 검증
        
        작성된 장면이 세계관/캐릭터 설정과 충돌하지 않는지 검증합니다.
        
        Args:
            project_id: 프로젝트 ID
            content: 검증할 장면 내용
        
        Returns:
            검증 결과 (issues, warnings)
        """
        issues = []
        warnings = []
        
        with get_db_context() as db:
            project = get_project(db, project_id)
            if not project:
                return {"error": "프로젝트를 찾을 수 없습니다."}
            
            characters = get_characters_by_project(db, project_id)
            
            # 캐릭터 금지 설정 검사
            for char in characters:
                if char.forbidden_actions:
                    for forbidden in char.forbidden_actions:
                        if forbidden.lower() in content.lower():
                            issues.append({
                                "type": "forbidden_action",
                                "character": char.name,
                                "detail": f"'{forbidden}' 행동이 금지되어 있습니다."
                            })
            
            # 세계관 규칙 검사 (간단 버전)
            if project.world_setting:
                # "~없음", "~금지" 패턴 찾기
                import re
                no_patterns = re.findall(r'(\w+)\s*(없음|금지)', project.world_setting)
                for pattern in no_patterns:
                    keyword = pattern[0]
                    if keyword in content:
                        warnings.append({
                            "type": "world_rule_violation",
                            "detail": f"'{keyword}'이(가) 세계관 설정에서 금지/없음으로 설정되어 있습니다."
                        })
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def check_character_consistency(self, project_id: int, character_name: str, dialogue: str) -> Dict[str, Any]:
        """
        캐릭터 일관성 검사
        
        대사가 캐릭터의 말투/성격과 일치하는지 검사합니다.
        
        Args:
            project_id: 프로젝트 ID
            character_name: 캐릭터 이름
            dialogue: 검사할 대사
        
        Returns:
            일관성 검사 결과
        """
        with get_db_context() as db:
            characters = get_characters_by_project(db, project_id)
            character = next((c for c in characters if c.name == character_name), None)
            
            if not character:
                return {"error": f"캐릭터 '{character_name}'을(를) 찾을 수 없습니다."}
            
            # AI로 일관성 검사
            if "openai" in self.providers:
                provider = self.providers["openai"]
                
                prompt = f"""다음 캐릭터의 대사가 캐릭터 설정과 일관성이 있는지 평가해주세요.

## 캐릭터 정보
이름: {character.name}
성격: {character.personality_description or 'N/A'}
말투: {character.speech_pattern or 'N/A'}
대사 예시: {character.speech_examples[:2] if character.speech_examples else 'N/A'}

## 검사할 대사
"{dialogue}"

## 평가 형식 (JSON)
{{
    "consistent": true/false,
    "score": 0.0-1.0,
    "issues": ["이슈1", "이슈2"],
    "suggestions": ["제안1", "제안2"]
}}

JSON만 출력:"""
                
                try:
                    response = provider.generate(prompt, temperature=0.3, max_tokens=500)
                    import re
                    json_match = re.search(r'\{[\s\S]*\}', response)
                    if json_match:
                        return json.loads(json_match.group())
                except:
                    pass
            
            return {"consistent": True, "score": 0.5, "issues": [], "suggestions": []}
    
    # ==================== 생성 도구 ====================
    
    async def generate_text(self, prompt: str, provider: str = "openai", 
                           temperature: float = 0.7, max_tokens: int = 2000) -> Dict[str, Any]:
        """텍스트 생성 (기본)"""
        if provider not in self.providers:
            return {"error": f"프로바이더 {provider}를 사용할 수 없습니다."}
        
        try:
            result = self.providers[provider].generate(
                prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return {
                "success": True,
                "text": result,
                "provider": provider
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_with_context(self, 
                             project_id: int,
                             prompt: str,
                             episode_id: Optional[int] = None,
                             character_names: Optional[List[str]] = None,
                             provider: str = "openai") -> Dict[str, Any]:
        """
        컨텍스트가 포함된 텍스트 생성
        
        프로젝트의 세계관/캐릭터 정보를 자동으로 포함하여 생성합니다.
        
        Args:
            project_id: 프로젝트 ID
            prompt: 사용자 프롬프트
            episode_id: 에피소드 ID (선택)
            character_names: 포함할 캐릭터 이름 목록
            provider: AI 프로바이더
        
        Returns:
            생성 결과
        """
        if provider not in self.providers:
            return {"error": f"프로바이더 {provider}를 사용할 수 없습니다."}
        
        with get_db_context() as db:
            builder = ContextBuilder(db)
            
            # 캐릭터 ID 조회
            character_ids = None
            if character_names:
                characters = get_characters_by_project(db, project_id)
                character_ids = [c.id for c in characters if c.name in character_names]
            
            context = builder.build_prompt_context(
                project_id=project_id,
                episode_id=episode_id,
                scene_goal=prompt,
                target_characters=character_ids
            )
        
        full_prompt = f"""{context}

## 요청
{prompt}

위 컨텍스트를 참고하여 요청을 수행해주세요.
캐릭터의 말투와 성격, 세계관 규칙을 반드시 준수하세요.
"""
        
        try:
            result = self.providers[provider].generate(
                full_prompt,
                temperature=0.8,
                max_tokens=3000
            )
            return {
                "success": True,
                "text": result,
                "provider": provider,
                "context_included": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==================== 평가 도구 ====================
    
    def evaluate_scene(self, content: str, project_id: Optional[int] = None) -> Dict[str, Any]:
        """
        장면 평가
        
        창의성, 클리셰, 감정 강도 등을 평가합니다.
        
        Args:
            content: 평가할 장면 내용
            project_id: 프로젝트 ID (컨텍스트 포함 시)
        
        Returns:
            평가 결과
        """
        try:
            evaluator = SceneEvaluator()
            
            context = None
            characters = None
            
            if project_id:
                with get_db_context() as db:
                    project = get_project(db, project_id)
                    if project:
                        context = {
                            "world_setting": project.world_setting,
                            "style_guide": project.style_guide
                        }
                        chars = get_characters_by_project(db, project_id)
                        characters = [
                            {"name": c.name, "speech_pattern": c.speech_pattern}
                            for c in chars
                        ]
            
            evaluation = evaluator.evaluate(content, context, characters)
            
            return {
                "overall_score": evaluation.overall_score,
                "creativity_score": evaluation.creativity_score,
                "consistency_score": evaluation.consistency_score,
                "emotion_score": evaluation.emotion_score,
                "pacing_score": evaluation.pacing_score,
                "dialogue_score": evaluation.dialogue_score,
                "cliche_detected": evaluation.cliche_detected,
                "cliches": [c.model_dump() for c in evaluation.cliches],
                "issues": [i.model_dump() for i in evaluation.issues],
                "summary": evaluation.summary,
                "suggestions": evaluation.suggestions,
                "strengths": evaluation.strengths
            }
        except Exception as e:
            return {"error": str(e)}
    
    def quick_evaluate(self, content: str) -> Dict[str, Any]:
        """
        빠른 평가 (규칙 기반만)
        
        AI 호출 없이 빠르게 기본 평가를 수행합니다.
        """
        try:
            evaluator = SceneEvaluator()
            return evaluator.quick_evaluate(content)
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== 유틸리티 ====================
    
    def _summarize(self, content: str, max_length: int = 150) -> str:
        """내용 요약"""
        if not content:
            return ""
        
        lines = content.split('\n')[:3]
        summary = ' '.join(lines)
        
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return summary
    
    def list_providers(self) -> List[str]:
        """사용 가능한 프로바이더 목록"""
        return list(self.providers.keys())
    
    def list_projects(self) -> List[Dict]:
        """프로젝트 목록 조회"""
        with get_db_context() as db:
            projects = get_projects(db)
            return [
                {
                    "id": p.id,
                    "title": p.title,
                    "project_type": p.project_type,
                    "status": p.status
                }
                for p in projects
            ]
    
    def get_tools_list(self) -> List[Dict]:
        """
        사용 가능한 도구 목록
        
        MCP 클라이언트에게 제공할 도구 정보
        """
        return [
            {
                "name": "get_project_context",
                "description": "프로젝트 전체 컨텍스트 조회 (세계관, 캐릭터, 스타일 가이드)",
                "parameters": {"project_id": "int"}
            },
            {
                "name": "get_character_context",
                "description": "캐릭터 컨텍스트 조회 (성격, 말투, 금지 설정)",
                "parameters": {"project_id": "int", "character_names": "List[str] (optional)"}
            },
            {
                "name": "get_world_rules",
                "description": "세계관 규칙 조회",
                "parameters": {"project_id": "int"}
            },
            {
                "name": "get_scene_history",
                "description": "이전 장면 히스토리 조회",
                "parameters": {"episode_id": "int", "limit": "int (default: 5)"}
            },
            {
                "name": "get_unresolved_callbacks",
                "description": "미해결 복선 조회",
                "parameters": {"project_id": "int"}
            },
            {
                "name": "validate_scene",
                "description": "장면 검증 (설정 충돌 검사)",
                "parameters": {"project_id": "int", "content": "str"}
            },
            {
                "name": "check_character_consistency",
                "description": "캐릭터 일관성 검사",
                "parameters": {"project_id": "int", "character_name": "str", "dialogue": "str"}
            },
            {
                "name": "generate_with_context",
                "description": "컨텍스트 포함 텍스트 생성",
                "parameters": {"project_id": "int", "prompt": "str", "episode_id": "int (optional)"}
            },
            {
                "name": "evaluate_scene",
                "description": "장면 평가 (창의성, 클리셰, 감정 강도)",
                "parameters": {"content": "str", "project_id": "int (optional)"}
            },
            {
                "name": "quick_evaluate",
                "description": "빠른 평가 (규칙 기반)",
                "parameters": {"content": "str"}
            }
        ]


# HTTP 서버 구현
from http.server import HTTPServer, BaseHTTPRequestHandler
import json as json_lib

class MCPHandler(BaseHTTPRequestHandler):
    """MCP HTTP 핸들러"""
    
    mcp_server = MCPServer()
    
    def do_POST(self):
        """POST 요청 처리"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json_lib.loads(post_data.decode('utf-8'))
            action = data.get('action')
            params = data.get('params', {})
            
            # 액션별 처리
            result = self._handle_action(action, params)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json_lib.dumps(result, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json_lib.dumps({"error": str(e)}, ensure_ascii=False).encode('utf-8'))
    
    def _handle_action(self, action: str, params: dict) -> dict:
        """액션 처리"""
        actions = {
            'generate': lambda: asyncio.run(self.mcp_server.generate_text(**params)),
            'generate_with_context': lambda: self.mcp_server.generate_with_context(**params),
            'get_project_context': lambda: self.mcp_server.get_project_context(**params),
            'get_character_context': lambda: self.mcp_server.get_character_context(**params),
            'get_world_rules': lambda: self.mcp_server.get_world_rules(**params),
            'get_scene_history': lambda: self.mcp_server.get_scene_history(**params),
            'get_unresolved_callbacks': lambda: self.mcp_server.get_unresolved_callbacks(**params),
            'validate_scene': lambda: self.mcp_server.validate_scene(**params),
            'check_character_consistency': lambda: self.mcp_server.check_character_consistency(**params),
            'evaluate_scene': lambda: self.mcp_server.evaluate_scene(**params),
            'quick_evaluate': lambda: self.mcp_server.quick_evaluate(**params),
            'list_providers': lambda: {"providers": self.mcp_server.list_providers()},
            'list_projects': lambda: {"projects": self.mcp_server.list_projects()},
            'list_tools': lambda: {"tools": self.mcp_server.get_tools_list()}
        }
        
        if action in actions:
            return actions[action]()
        else:
            return {"error": f"Unknown action: {action}"}
    
    def do_GET(self):
        """GET 요청 처리"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "version": "2.0"}')
        elif self.path == '/tools':
            tools = self.mcp_server.get_tools_list()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json_lib.dumps({"tools": tools}, ensure_ascii=False).encode('utf-8'))
        elif self.path == '/providers':
            providers = self.mcp_server.list_providers()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json_lib.dumps({"providers": providers}, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()


def run_mcp_server(port: int = 8001):
    """MCP 서버 실행"""
    server = HTTPServer(('localhost', port), MCPHandler)
    print(f"MCP 서버 v2.0이 http://localhost:{port}에서 실행 중입니다.")
    print("\n사용 가능한 엔드포인트:")
    print("  GET  /health    - 헬스 체크")
    print("  GET  /tools     - 도구 목록")
    print("  GET  /providers - 프로바이더 목록")
    print("  POST /          - 액션 실행")
    print("\n종료하려면 Ctrl+C를 누르세요.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n서버를 종료합니다.")
        server.shutdown()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='MCP 서버 실행')
    parser.add_argument('--port', type=int, default=8001, help='서버 포트 (기본: 8001)')
    args = parser.parse_args()
    run_mcp_server(args.port)
