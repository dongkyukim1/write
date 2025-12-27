"""
장면(Scene) 스키마
대본의 핵심 단위 - 구조화된 메타데이터 포함
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .base import BaseSchema, TimestampMixin


class ConflictType(str, Enum):
    """갈등 유형"""
    RELATIONSHIP = "relationship"       # 인물 간 관계 갈등
    INTERNAL = "internal"               # 내면 갈등
    EXTERNAL = "external"               # 외부 상황 갈등
    IDEOLOGICAL = "ideological"         # 가치관/이념 갈등
    COMEDIC = "comedic"                 # 코미디적 갈등
    NONE = "none"                       # 갈등 없음


class EmotionCurve(str, Enum):
    """감정 곡선 단계"""
    CALM = "calm"                       # 평온
    RISING = "rising"                   # 상승
    TENSION = "tension"                 # 긴장
    CLIMAX = "climax"                   # 절정
    FALLING = "falling"                 # 하강
    RESOLUTION = "resolution"           # 해소
    EXPLOSIVE = "explosive"             # 폭발
    SILENCE = "silence"                 # 침묵/여운


class DialogDensity(str, Enum):
    """대화 밀도"""
    HIGH = "high"                       # 대화 많음
    MEDIUM = "medium"                   # 중간
    LOW = "low"                         # 대화 적음 (나레이션/지문 위주)


class SceneType(str, Enum):
    """장면 타입"""
    OPENING = "opening"                 # 오프닝
    TALK = "talk"                       # 본격 토크
    NEWS_SUMMARY = "news_summary"       # 뉴스 요약
    HIGHLIGHT = "highlight"             # 하이라이트
    CLOSING = "closing"                 # 마무리
    TRANSITION = "transition"           # 전환
    INTERVIEW = "interview"             # 인터뷰
    NARRATION = "narration"             # 나레이션
    ACTION = "action"                   # 액션
    DIALOGUE = "dialogue"               # 대화


class SceneBase(BaseModel):
    """장면 기본 필드"""
    episode_id: int = Field(..., description="에피소드 ID")
    scene_number: int = Field(..., description="장면 번호")
    scene_type: SceneType = Field(default=SceneType.DIALOGUE, description="장면 타입")
    title: Optional[str] = Field(None, description="장면 제목/설명")


class SceneCreate(SceneBase):
    """장면 생성 스키마"""
    # 메타데이터
    goal: Optional[str] = Field(None, description="이 장면의 목표")
    emotion_curve: List[EmotionCurve] = Field(
        default_factory=list, 
        description="감정 흐름 곡선"
    )
    conflict_type: ConflictType = Field(
        default=ConflictType.NONE, 
        description="갈등 유형"
    )
    dialog_density: DialogDensity = Field(
        default=DialogDensity.MEDIUM, 
        description="대화 밀도"
    )
    
    # 참여 캐릭터
    character_ids: List[int] = Field(default_factory=list, description="참여 캐릭터 ID들")
    
    # 본문
    content: str = Field(default="", description="장면 본문")
    
    # 작가 노트
    writer_notes: Optional[str] = Field(None, description="작가 노트")


class SceneUpdate(BaseModel):
    """장면 수정 스키마"""
    title: Optional[str] = None
    scene_type: Optional[SceneType] = None
    goal: Optional[str] = None
    emotion_curve: Optional[List[EmotionCurve]] = None
    conflict_type: Optional[ConflictType] = None
    dialog_density: Optional[DialogDensity] = None
    character_ids: Optional[List[int]] = None
    content: Optional[str] = None
    writer_notes: Optional[str] = None
    human_edited: Optional[bool] = None


class Scene(SceneBase, TimestampMixin, BaseSchema):
    """장면 전체 스키마"""
    id: int
    scene_id: str = Field(..., description="고유 장면 ID (예: S01E03_SC02)")
    
    # 메타데이터
    goal: Optional[str] = None
    emotion_curve: List[EmotionCurve] = Field(default_factory=list)
    conflict_type: ConflictType = ConflictType.NONE
    dialog_density: DialogDensity = DialogDensity.MEDIUM
    
    # 참여 캐릭터
    character_ids: List[int] = Field(default_factory=list)
    
    # 본문
    content: str = ""
    
    # 생성 정보
    ai_generated: bool = False
    human_edited: bool = False
    generation_prompt: Optional[str] = None
    
    # 작가 노트
    writer_notes: Optional[str] = None
    
    # 통계
    word_count: int = 0
    estimated_runtime: Optional[int] = None  # 초 단위
    
    # 평가 정보 (별도 테이블 참조)
    evaluation_id: Optional[int] = None
    
    # 버전 관리
    version: int = 1
    parent_scene_id: Optional[int] = None  # 이전 버전 참조


class SceneWithEvaluation(Scene):
    """평가 정보가 포함된 장면"""
    evaluation: Optional[Any] = None  # Evaluation 타입 (순환 참조 방지)

