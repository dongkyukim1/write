"""
대본 포맷팅 유틸리티
대본을 읽기 쉽게 포맷팅합니다.
"""

import re
from typing import List, Dict


def format_talk_show_script(script: str, speakers: List[str]) -> str:
    """
    토크쇼 대본을 포맷팅합니다.
    
    Args:
        script: 원본 대본 텍스트
        speakers: 진행자 이름 리스트 (예: ["최욱", "정영진"])
    
    Returns:
        포맷팅된 대본
    
    사용 예시:
        script = "최욱: 안녕하세요\\n정영진: 네 안녕하세요"
        formatted = format_talk_show_script(script, ["최욱", "정영진"])
    """
    lines = script.strip().split("\n")
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            formatted_lines.append("")
            continue
        
        # 진행자 이름으로 시작하는지 확인
        speaker_found = False
        for speaker in speakers:
            if line.startswith(f"{speaker}:"):
                # 진행자 멘트 포맷팅
                formatted_lines.append(f"\n**{speaker}:**")
                content = line[len(f"{speaker}:"):].strip()
                if content:
                    formatted_lines.append(f"  {content}")
                speaker_found = True
                break
        
        if not speaker_found:
            # 일반 텍스트 (작가 노트 등)
            if line.startswith("#") or line.startswith("**"):
                formatted_lines.append(line)
            else:
                formatted_lines.append(f"  {line}")
    
    return "\n".join(formatted_lines)


def extract_speaker_lines(script: str, speaker: str) -> List[str]:
    """
    특정 진행자의 멘트만 추출합니다.
    
    Args:
        script: 대본 텍스트
        speaker: 진행자 이름
    
    Returns:
        해당 진행자의 멘트 리스트
    
    사용 예시:
        최욱_멘트 = extract_speaker_lines(script, "최욱")
    """
    pattern = rf"^{speaker}:\s*(.+)$"
    matches = re.findall(pattern, script, re.MULTILINE)
    return matches


def calculate_running_time(script: str, words_per_minute: int = 150) -> float:
    """
    대본의 예상 러닝타임을 계산합니다.
    
    Args:
        script: 대본 텍스트
        words_per_minute: 분당 단어 수 (기본값: 150)
    
    Returns:
        예상 러닝타임 (분)
    
    사용 예시:
        time = calculate_running_time(script)
        print(f"예상 러닝타임: {time:.1f}분")
    """
    # 한글 기준으로 단어 수 계산 (간단한 방법)
    # 실제로는 더 정교한 계산 필요
    words = len(script.split())
    minutes = words / words_per_minute
    return minutes


def format_markdown_script(script: str) -> str:
    """
    마크다운 형식으로 대본을 포맷팅합니다.
    
    Args:
        script: 원본 대본
    
    Returns:
        마크다운 형식의 대본
    """
    # 기본 포맷팅
    formatted = script
    
    # 섹션 헤더 강조
    formatted = re.sub(r"^## (.+)$", r"## \1", formatted, flags=re.MULTILINE)
    
    # 진행자 이름 강조
    formatted = re.sub(r"^(\w+):", r"**\1:**", formatted, flags=re.MULTILINE)
    
    return formatted

