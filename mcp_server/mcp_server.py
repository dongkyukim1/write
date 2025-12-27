"""
MCP (Model Context Protocol) 서버
로컬 모델과 통신하기 위한 MCP 서버 구현
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

load_dotenv(project_root / ".env")


class MCPServer:
    """MCP 서버 클래스"""
    
    def __init__(self):
        self.providers = {}
        self._initialize_providers()
    
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
    
    async def generate_text(self, prompt: str, provider: str = "openai", 
                           temperature: float = 0.7, max_tokens: int = 2000) -> Dict[str, Any]:
        """텍스트 생성"""
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
    
    async def generate_stream(self, prompt: str, provider: str = "openai",
                            temperature: float = 0.7, max_tokens: int = 2000):
        """스트리밍 텍스트 생성"""
        if provider not in self.providers:
            yield {"error": f"프로바이더 {provider}를 사용할 수 없습니다."}
            return
        
        try:
            for chunk in self.providers[provider].generate_stream(
                prompt,
                temperature=temperature,
                max_tokens=max_tokens
            ):
                yield {"chunk": chunk, "provider": provider}
        except Exception as e:
            yield {"error": str(e)}
    
    def list_providers(self) -> List[str]:
        """사용 가능한 프로바이더 목록"""
        return list(self.providers.keys())
    
    def get_provider_info(self, provider: str) -> Dict[str, Any]:
        """프로바이더 정보 조회"""
        if provider not in self.providers:
            return {"error": f"프로바이더 {provider}를 사용할 수 없습니다."}
        
        config = get_model_config(provider, "creative")
        return {
            "name": provider,
            "model": config.get("model", "N/A"),
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 2000)
        }


# HTTP 서버로 MCP 서버 실행 (간단한 구현)
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
            
            if action == 'generate':
                prompt = data.get('prompt', '')
                provider = data.get('provider', 'openai')
                temperature = data.get('temperature', 0.7)
                max_tokens = data.get('max_tokens', 2000)
                
                # 비동기 함수를 동기적으로 실행
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.mcp_server.generate_text(prompt, provider, temperature, max_tokens)
                )
                loop.close()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json_lib.dumps(result, ensure_ascii=False).encode('utf-8'))
            
            elif action == 'list_providers':
                providers = self.mcp_server.list_providers()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json_lib.dumps({"providers": providers}, ensure_ascii=False).encode('utf-8'))
            
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Unknown action"}')
        
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json_lib.dumps({"error": str(e)}, ensure_ascii=False).encode('utf-8'))
    
    def do_GET(self):
        """GET 요청 처리"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
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
    print(f"MCP 서버가 http://localhost:{port}에서 실행 중입니다.")
    print("종료하려면 Ctrl+C를 누르세요.")
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

