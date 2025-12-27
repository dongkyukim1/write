"""
모델 설정 관리 모듈
설정 파일을 로드하고 모델별 설정을 관리합니다.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional


def load_config(config_path: Optional[str] = None) -> Dict:
    """
    설정 파일을 로드합니다.
    
    Args:
        config_path: 설정 파일 경로 (기본값: config/settings.json)
    
    Returns:
        설정 딕셔너리
    
    사용 예시:
        config = load_config()
        model_name = config["default_model"]["model"]
    """
    if config_path is None:
        # 현재 파일 기준으로 config 폴더 찾기
        current_dir = Path(__file__).parent.parent.parent
        config_path = current_dir / "config" / "settings.json"
    
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_model_config(provider: str, model_type: str = "creative") -> Dict:
    """
    특정 프로바이더와 모델 타입의 설정을 가져옵니다.
    
    Args:
        provider: 프로바이더 이름 ('openai', 'claude')
        model_type: 모델 타입 ('creative', 'structured', 'fast')
    
    Returns:
        모델 설정 딕셔너리
    
    사용 예시:
        config = get_model_config("openai", "creative")
        temperature = config["temperature"]  # 0.9
    """
    settings = load_config()
    
    if provider not in settings["models"]:
        raise ValueError(f"지원하지 않는 프로바이더: {provider}")
    
    provider_config = settings["models"][provider]
    
    if "models" not in provider_config:
        raise ValueError(f"프로바이더 설정에 models가 없습니다: {provider}")
    
    if model_type not in provider_config["models"]:
        # 기본값 사용
        model_type = list(provider_config["models"].keys())[0]
    
    return provider_config["models"][model_type]


def get_api_key(provider: str) -> Optional[str]:
    """
    환경 변수에서 API 키를 가져옵니다.
    
    Args:
        provider: 프로바이더 이름
    
    Returns:
        API 키 또는 None
    
    사용 예시:
        api_key = get_api_key("openai")
        if not api_key:
            print("API 키를 설정해주세요")
    """
    key_map = {
        "openai": "OPENAI_API_KEY",
        "claude": "ANTHROPIC_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
    }
    
    env_key = key_map.get(provider.lower())
    if env_key:
        return os.getenv(env_key)
    
    return None

