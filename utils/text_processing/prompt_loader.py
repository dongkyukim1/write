"""
프롬프트 템플릿 로더
프롬프트 파일을 읽고 변수를 치환합니다.
"""

import re
from pathlib import Path
from typing import Dict, Optional


def load_prompt_template(
    template_path: str,
    base_dir: Optional[str] = None,
    **variables
) -> str:
    """
    프롬프트 템플릿 파일을 로드하고 변수를 치환합니다.
    
    Args:
        template_path: 템플릿 파일 경로 (prompts/ 폴더 기준)
        base_dir: 기본 디렉토리 (기본값: 프로젝트 루트)
        **variables: 치환할 변수들
    
    Returns:
        변수가 치환된 프롬프트 문자열
    
    사용 예시:
        prompt = load_prompt_template(
            "story/novel_generator.md",
            topic="SF 소설",
            length="중편",
            style="모던"
        )
    """
    if base_dir is None:
        # 현재 파일 기준으로 프로젝트 루트 찾기
        current_file = Path(__file__)
        base_dir = current_file.parent.parent.parent
    
    base_path = Path(base_dir)
    full_path = base_path / "prompts" / template_path
    
    if not full_path.exists():
        raise FileNotFoundError(f"템플릿 파일을 찾을 수 없습니다: {full_path}")
    
    # 파일 읽기
    with open(full_path, "r", encoding="utf-8") as f:
        template = f.read()
    
    # 변수 치환: {{변수명}} 형식
    def replace_var(match):
        var_name = match.group(1).strip()
        return str(variables.get(var_name, match.group(0)))
    
    result = re.sub(r"\{\{(\w+)\}\}", replace_var, template)
    
    return result


def extract_variables(template: str) -> list:
    """
    템플릿에서 사용된 변수 목록을 추출합니다.
    
    Args:
        template: 템플릿 문자열
    
    Returns:
        변수 이름 리스트
    
    사용 예시:
        template = "{{topic}}에 대한 {{style}} 스타일의 소설"
        vars = extract_variables(template)
        # ['topic', 'style']
    """
    pattern = r"\{\{(\w+)\}\}"
    matches = re.findall(pattern, template)
    return list(set(matches))  # 중복 제거


def validate_template(template_path: str, **variables) -> tuple[bool, list]:
    """
    템플릿에 필요한 변수가 모두 제공되었는지 검증합니다.
    
    Args:
        template_path: 템플릿 파일 경로
        **variables: 제공된 변수들
    
    Returns:
        (검증 통과 여부, 누락된 변수 리스트)
    
    사용 예시:
        is_valid, missing = validate_template(
            "story/novel_generator.md",
            topic="SF",
            length="중편"
        )
        if not is_valid:
            print(f"누락된 변수: {missing}")
    """
    base_path = Path(__file__).parent.parent.parent
    full_path = base_path / "prompts" / template_path
    
    with open(full_path, "r", encoding="utf-8") as f:
        template = f.read()
    
    required_vars = extract_variables(template)
    provided_vars = set(variables.keys())
    missing_vars = [var for var in required_vars if var not in provided_vars]
    
    return len(missing_vars) == 0, missing_vars

