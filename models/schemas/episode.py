"""
에피소드 스키마
에피소드 단위의 데이터 모델
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

from .base import BaseSchema, TimestampMixin


class EpisodeStatus(str, Enum):
    """에피소드 상태"""
    OUTLINE = "outline"             # 구성안 작성 중
    DRAFT = "draft"                 # 초안 작성 중
    FIRST_EDIT = "first_edit"       # 1차 수정
    FINAL = "final"                 # 최종본
    BROADCAST = "broadcast"         # 방송 완료


class EpisodeBase(BaseModel):
    """에피소드 기본 필드"""
    project_id: int = Field(..., description="프로젝트 ID")
    episode_number: int = Field(..., description="에피소드 번호")
    title: str = Field(..., description="에피소드 제목")
    summary: Optional[str] = Field(None, description="에피소드 요약")
    broadcast_date: Optional[datetime] = Field(None, description="방송 예정일")


class EpisodeCreate(EpisodeBase):
    """에피소드 생성 스키마"""
    main_topic: Optional[str] = Field(None, description="메인 토픽")
    sub_topics: Optional[List[str]] = Field(default_factory=list, description="서브 토픽들")
    target_runtime: Optional[int] = Field(None, description="목표 러닝타임 (분)")
    notes: Optional[str] = Field(None, description="작가 노트")


class EpisodeUpdate(BaseModel):
    """에피소드 수정 스키마"""
    title: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[EpisodeStatus] = None
    main_topic: Optional[str] = None
    sub_topics: Optional[List[str]] = None
    broadcast_date: Optional[datetime] = None
    notes: Optional[str] = None


class Episode(EpisodeBase, TimestampMixin, BaseSchema):
    """에피소드 전체 스키마"""
    id: int
    status: EpisodeStatus = EpisodeStatus.OUTLINE
    main_topic: Optional[str] = None
    sub_topics: List[str] = Field(default_factory=list)
    target_runtime: Optional[int] = None
    actual_runtime: Optional[int] = None
    notes: Optional[str] = None
    
    # 통계 정보
    total_scenes: int = 0
    word_count: int = 0
    avg_creativity_score: Optional[float] = None
    
    # 에피소드 구조 분석
    structure_summary: Optional[str] = None  # AI가 분석한 구조 요약

