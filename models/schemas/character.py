"""
캐릭터 스키마
등장인물/진행자의 데이터 모델
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .base import BaseSchema, TimestampMixin


class CharacterRole(str, Enum):
    """캐릭터 역할"""
    PROTAGONIST = "protagonist"         # 주인공
    ANTAGONIST = "antagonist"           # 적대자
    SUPPORTING = "supporting"           # 조연
    HOST = "host"                       # 진행자 (토크쇼)
    CO_HOST = "co_host"                 # 공동 진행자
    GUEST = "guest"                     # 게스트
    NARRATOR = "narrator"               # 나레이터
    EXTRA = "extra"                     # 엑스트라


class PersonalityTrait(str, Enum):
    """성격 특성"""
    CYNICAL = "cynical"                 # 냉소적
    WARM = "warm"                       # 따뜻한
    HUMOROUS = "humorous"               # 유머러스
    SERIOUS = "serious"                 # 진지한
    EMOTIONAL = "emotional"             # 감정적
    RATIONAL = "rational"               # 이성적
    SARCASTIC = "sarcastic"             # 풍자적
    EMPATHETIC = "empathetic"           # 공감형
    PROVOCATIVE = "provocative"         # 도발적
    CALM = "calm"                       # 침착한


class CharacterBase(BaseModel):
    """캐릭터 기본 필드"""
    project_id: int = Field(..., description="프로젝트 ID")
    name: str = Field(..., description="캐릭터 이름")
    role: CharacterRole = Field(default=CharacterRole.SUPPORTING, description="역할")


class CharacterCreate(CharacterBase):
    """캐릭터 생성 스키마"""
    # 기본 정보
    description: Optional[str] = Field(None, description="캐릭터 설명")
    backstory: Optional[str] = Field(None, description="배경 스토리")
    
    # 성격
    personality_traits: List[PersonalityTrait] = Field(
        default_factory=list, 
        description="성격 특성들"
    )
    personality_description: Optional[str] = Field(None, description="성격 상세 설명")
    
    # 말투/스타일
    speech_pattern: Optional[str] = Field(None, description="말투 특징")
    speech_examples: List[str] = Field(
        default_factory=list, 
        description="대사 예시"
    )
    
    # 금지 설정
    forbidden_actions: List[str] = Field(
        default_factory=list, 
        description="이 캐릭터가 하면 안 되는 것들"
    )


class CharacterUpdate(BaseModel):
    """캐릭터 수정 스키마"""
    name: Optional[str] = None
    role: Optional[CharacterRole] = None
    description: Optional[str] = None
    backstory: Optional[str] = None
    personality_traits: Optional[List[PersonalityTrait]] = None
    personality_description: Optional[str] = None
    speech_pattern: Optional[str] = None
    speech_examples: Optional[List[str]] = None
    current_state: Optional[str] = None
    forbidden_actions: Optional[List[str]] = None


class Character(CharacterBase, TimestampMixin, BaseSchema):
    """캐릭터 전체 스키마"""
    id: int
    
    # 기본 정보
    description: Optional[str] = None
    backstory: Optional[str] = None
    
    # 성격
    personality_traits: List[PersonalityTrait] = Field(default_factory=list)
    personality_description: Optional[str] = None
    
    # 말투/스타일
    speech_pattern: Optional[str] = None
    speech_examples: List[str] = Field(default_factory=list)
    
    # 현재 상태 (에피소드 진행에 따라 변함)
    current_state: Optional[str] = None
    
    # 금지 설정
    forbidden_actions: List[str] = Field(default_factory=list)
    
    # 통계
    total_appearances: int = 0
    total_dialogues: int = 0


class CharacterRelationship(BaseModel):
    """캐릭터 관계 스키마"""
    character_id: int
    related_character_id: int
    relationship_type: str = Field(..., description="관계 유형 (예: 친구, 라이벌, 연인)")
    description: Optional[str] = Field(None, description="관계 상세 설명")
    dynamics: Optional[str] = Field(None, description="관계 역학 (예: 티키타카, 대립)")


class CharacterContext(BaseModel):
    """MCP에서 사용할 캐릭터 컨텍스트"""
    name: str
    role: CharacterRole
    personality_summary: str
    speech_pattern: str
    current_state: Optional[str]
    key_traits: List[str]
    forbidden_actions: List[str]
    
    @classmethod
    def from_character(cls, char: Character) -> "CharacterContext":
        """Character 모델에서 컨텍스트 생성"""
        return cls(
            name=char.name,
            role=char.role,
            personality_summary=char.personality_description or "",
            speech_pattern=char.speech_pattern or "",
            current_state=char.current_state,
            key_traits=[t.value for t in char.personality_traits],
            forbidden_actions=char.forbidden_actions
        )

