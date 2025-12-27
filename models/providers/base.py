"""
LLM 프로바이더 기본 클래스
각 프로바이더는 이 클래스를 상속받아 구현합니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseLLMProvider(ABC):
    """LLM 프로바이더 기본 클래스"""
    
    def __init__(self, api_key: str, config: Optional[Dict] = None):
        """
        Args:
            api_key: API 키
            config: 추가 설정 딕셔너리
        """
        self.api_key = api_key
        self.config = config or {}
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        프롬프트를 받아서 텍스트를 생성합니다.
        
        Args:
            prompt: 입력 프롬프트
            **kwargs: 추가 파라미터 (temperature, max_tokens 등)
        
        Returns:
            생성된 텍스트
        """
        pass
    
    @abstractmethod
    def generate_stream(self, prompt: str, **kwargs):
        """
        스트리밍 방식으로 텍스트를 생성합니다.
        
        Args:
            prompt: 입력 프롬프트
            **kwargs: 추가 파라미터
        
        Yields:
            생성된 텍스트 청크
        """
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI 프로바이더 구현"""
    
    def __init__(self, api_key: str, config: Optional[Dict] = None):
        super().__init__(api_key, config)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.model = config.get("model", "gpt-4") if config else "gpt-4"
        except ImportError:
            raise ImportError("openai 패키지가 설치되지 않았습니다. 'pip install openai' 실행하세요.")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        OpenAI API를 사용하여 텍스트 생성
        
        사용 예시:
            provider = OpenAIProvider(api_key="sk-...")
            result = provider.generate(
                prompt="소설의 첫 문장을 써주세요",
                temperature=0.9,
                max_tokens=500
            )
        """
        temperature = kwargs.get("temperature", self.config.get("temperature", 0.7))
        max_tokens = kwargs.get("max_tokens", self.config.get("max_tokens", 2000))
        model = kwargs.get("model", self.model)
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "당신은 전문 작가입니다. 요청에 따라 창의적이고 전문적인 글을 작성합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API 호출 실패: {e}")
    
    def generate_stream(self, prompt: str, **kwargs):
        """스트리밍 생성"""
        temperature = kwargs.get("temperature", self.config.get("temperature", 0.7))
        max_tokens = kwargs.get("max_tokens", self.config.get("max_tokens", 2000))
        model = kwargs.get("model", self.model)
        
        try:
            stream = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "당신은 전문 작가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API 스트리밍 실패: {e}")


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude 프로바이더 구현"""
    
    def __init__(self, api_key: str, config: Optional[Dict] = None):
        super().__init__(api_key, config)
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key)
            self.model = config.get("model", "claude-3-sonnet-20240229") if config else "claude-3-sonnet-20240229"
        except ImportError:
            raise ImportError("anthropic 패키지가 설치되지 않았습니다. 'pip install anthropic' 실행하세요.")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Claude API를 사용하여 텍스트 생성"""
        temperature = kwargs.get("temperature", self.config.get("temperature", 0.7))
        max_tokens = kwargs.get("max_tokens", self.config.get("max_tokens", 2000))
        model = kwargs.get("model", self.model)
        
        try:
            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system="당신은 전문 작가입니다. 요청에 따라 창의적이고 전문적인 글을 작성합니다.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            raise RuntimeError(f"Claude API 호출 실패: {e}")
    
    def generate_stream(self, prompt: str, **kwargs):
        """스트리밍 생성"""
        temperature = kwargs.get("temperature", self.config.get("temperature", 0.7))
        max_tokens = kwargs.get("max_tokens", self.config.get("max_tokens", 2000))
        model = kwargs.get("model", self.model)
        
        try:
            with self.client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system="당신은 전문 작가입니다.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            raise RuntimeError(f"Claude API 스트리밍 실패: {e}")


def get_provider(provider_name: str, api_key: str, config: Optional[Dict] = None) -> BaseLLMProvider:
    """
    프로바이더 이름으로 인스턴스 생성
    
    Args:
        provider_name: 'openai' 또는 'claude'
        api_key: API 키
        config: 추가 설정
    
    Returns:
        프로바이더 인스턴스
    
    사용 예시:
        provider = get_provider("openai", api_key="sk-...")
        result = provider.generate("프롬프트")
    """
    providers = {
        "openai": OpenAIProvider,
        "claude": ClaudeProvider,
    }
    
    if provider_name.lower() not in providers:
        raise ValueError(f"지원하지 않는 프로바이더: {provider_name}")
    
    return providers[provider_name.lower()](api_key, config)

