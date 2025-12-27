"""
프로젝트 스키마
대본 시리즈/프로젝트 단위의 데이터 모델
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

from .base import BaseSchema, TimestampMixin


class ProjectType(str, Enum):
    """프로젝트 타입"""
    TALK_SHOW = "talk_show"        # 토크쇼/팟캐스트
    DRAMA = "drama"                 # 드라마
    MOVIE = "movie"                 # 영화
    WEB_DRAMA = "web_drama"         # 웹드라마
    VARIETY = "variety"             # 예능
    DOCUMENTARY = "documentary"     # 다큐멘터리
    OTHER = "other"


class ProjectStatus(str, Enum):
    """프로젝트 상태"""
    DRAFT = "draft"                 # 초안 작성 중
    IN_PROGRESS = "in_progress"     # 진행 중
    REVIEW = "review"               # 검토 중
    COMPLETED = "completed"         # 완료
    ARCHIVED = "archived"           # 보관됨


class ProjectBase(BaseModel):
    """프로젝트 기본 필드"""
    title: str = Field(..., description="프로젝트 제목")
    project_type: ProjectType = Field(default=ProjectType.TALK_SHOW, description="프로젝트 타입")
    description: Optional[str] = Field(None, description="프로젝트 설명")
    genre: Optional[str] = Field(None, description="장르")
    target_audience: Optional[str] = Field(None, description="타겟 시청자")
    tone: Optional[str] = Field(None, description="전체적인 톤앤매너")


class ProjectCreate(ProjectBase):
    """프로젝트 생성 스키마"""
    world_setting: Optional[str] = Field(None, description="세계관 설정")
    style_guide: Optional[str] = Field(None, description="문체 가이드")


class ProjectUpdate(BaseModel):
    """프로젝트 수정 스키마"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    world_setting: Optional[str] = None
    style_guide: Optional[str] = None


class Project(ProjectBase, TimestampMixin, BaseSchema):
    """프로젝트 전체 스키마"""
    id: int
    status: ProjectStatus = ProjectStatus.DRAFT
    world_setting: Optional[str] = None
    style_guide: Optional[str] = None
    total_episodes: int = 0
    total_scenes: int = 0
    
    # 통계 정보
    total_word_count: int = 0
    avg_creativity_score: Optional[float] = None

