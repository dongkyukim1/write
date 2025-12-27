"""
SQLAlchemy ORM 모델
데이터베이스 테이블 정의
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, 
    DateTime, ForeignKey, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from .schema import Base

# Enum 타입들 임포트
from models.schemas.project import ProjectType, ProjectStatus
from models.schemas.episode import EpisodeStatus
from models.schemas.scene import SceneType, ConflictType, DialogDensity
from models.schemas.character import CharacterRole


class ProjectModel(Base):
    """프로젝트 테이블"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    project_type = Column(String(50), default=ProjectType.TALK_SHOW.value)
    description = Column(Text, nullable=True)
    genre = Column(String(100), nullable=True)
    target_audience = Column(String(255), nullable=True)
    tone = Column(Text, nullable=True)
    status = Column(String(50), default=ProjectStatus.DRAFT.value)
    
    # 세계관 및 스타일
    world_setting = Column(Text, nullable=True)
    style_guide = Column(Text, nullable=True)
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 관계
    episodes = relationship("EpisodeModel", back_populates="project", cascade="all, delete-orphan")
    characters = relationship("CharacterModel", back_populates="project", cascade="all, delete-orphan")


class EpisodeModel(Base):
    """에피소드 테이블"""
    __tablename__ = "episodes"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    episode_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    status = Column(String(50), default=EpisodeStatus.OUTLINE.value)
    
    # 토픽 정보
    main_topic = Column(String(255), nullable=True)
    sub_topics = Column(JSON, default=list)  # List[str]
    
    # 시간 정보
    broadcast_date = Column(DateTime, nullable=True)
    target_runtime = Column(Integer, nullable=True)  # 분 단위
    actual_runtime = Column(Integer, nullable=True)
    
    # 작가 노트
    notes = Column(Text, nullable=True)
    
    # 구조 분석
    structure_summary = Column(Text, nullable=True)
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 관계
    project = relationship("ProjectModel", back_populates="episodes")
    scenes = relationship("SceneModel", back_populates="episode", cascade="all, delete-orphan")


class SceneModel(Base):
    """장면 테이블 - 핵심 테이블"""
    __tablename__ = "scenes"
    
    id = Column(Integer, primary_key=True, index=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=False, index=True)
    scene_number = Column(Integer, nullable=False)
    scene_id = Column(String(50), unique=True, index=True)  # 예: S01E03_SC02
    scene_type = Column(String(50), default=SceneType.DIALOGUE.value)
    title = Column(String(255), nullable=True)
    
    # 메타데이터 - 구조화된 정보
    goal = Column(Text, nullable=True)
    emotion_curve = Column(JSON, default=list)  # List[EmotionCurve]
    conflict_type = Column(String(50), default=ConflictType.NONE.value)
    dialog_density = Column(String(50), default=DialogDensity.MEDIUM.value)
    
    # 참여 캐릭터
    character_ids = Column(JSON, default=list)  # List[int]
    
    # 본문
    content = Column(Text, default="")
    
    # 생성 정보
    ai_generated = Column(Boolean, default=False)
    human_edited = Column(Boolean, default=False)
    generation_prompt = Column(Text, nullable=True)
    
    # 작가 노트
    writer_notes = Column(Text, nullable=True)
    
    # 통계
    word_count = Column(Integer, default=0)
    estimated_runtime = Column(Integer, nullable=True)  # 초 단위
    
    # 버전 관리
    version = Column(Integer, default=1)
    parent_scene_id = Column(Integer, ForeignKey("scenes.id"), nullable=True)
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 관계
    episode = relationship("EpisodeModel", back_populates="scenes")
    evaluation = relationship("EvaluationModel", back_populates="scene", uselist=False)
    parent_scene = relationship("SceneModel", remote_side=[id])


class CharacterModel(Base):
    """캐릭터 테이블"""
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    role = Column(String(50), default=CharacterRole.SUPPORTING.value)
    
    # 기본 정보
    description = Column(Text, nullable=True)
    backstory = Column(Text, nullable=True)
    
    # 성격
    personality_traits = Column(JSON, default=list)  # List[PersonalityTrait]
    personality_description = Column(Text, nullable=True)
    
    # 말투/스타일
    speech_pattern = Column(Text, nullable=True)
    speech_examples = Column(JSON, default=list)  # List[str]
    
    # 현재 상태
    current_state = Column(Text, nullable=True)
    
    # 금지 설정
    forbidden_actions = Column(JSON, default=list)  # List[str]
    
    # 통계
    total_appearances = Column(Integer, default=0)
    total_dialogues = Column(Integer, default=0)
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 관계
    project = relationship("ProjectModel", back_populates="characters")


class EvaluationModel(Base):
    """평가 테이블"""
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    scene_id = Column(Integer, ForeignKey("scenes.id"), nullable=False, unique=True, index=True)
    
    # 점수들 (0.0 ~ 1.0)
    creativity_score = Column(Float, nullable=False)
    consistency_score = Column(Float, nullable=False)
    emotion_score = Column(Float, nullable=False)
    pacing_score = Column(Float, nullable=False)
    dialogue_score = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False)
    
    # 클리셰 감지
    cliche_detected = Column(Boolean, default=False)
    cliches = Column(JSON, default=list)  # List[ClicheDetection]
    
    # 이슈 목록
    issues = Column(JSON, default=list)  # List[EvaluationIssue]
    
    # 피드백
    summary = Column(Text, nullable=False)
    suggestions = Column(JSON, default=list)  # List[str]
    strengths = Column(JSON, default=list)  # List[str]
    
    # 평가 모델 정보
    evaluator_model = Column(String(100), nullable=True)
    evaluation_version = Column(String(20), default="1.0")
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 관계
    scene = relationship("SceneModel", back_populates="evaluation")


class CallbackModel(Base):
    """복선/떡밥 테이블"""
    __tablename__ = "callbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    
    # 복선 내용
    content = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    
    # 설치/회수 정보
    setup_scene_id = Column(Integer, ForeignKey("scenes.id"), nullable=True)
    setup_episode_number = Column(Integer, nullable=True)
    
    payoff_scene_id = Column(Integer, ForeignKey("scenes.id"), nullable=True)
    payoff_episode_number = Column(Integer, nullable=True)
    
    # 상태
    resolved = Column(Boolean, default=False)
    importance = Column(String(20), default="medium")  # low, medium, high
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class SynopsisModel(Base):
    """시놉시스 테이블 - 프로젝트당 1개"""
    __tablename__ = "synopses"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, unique=True, index=True)
    
    # 기본 정보
    title = Column(String(255), nullable=False)
    logline = Column(Text, nullable=True)  # 한 문장 요약
    premise = Column(Text, nullable=True)  # 전제
    theme = Column(Text, nullable=True)    # 주제
    
    # 분류
    genre = Column(String(100), nullable=True)
    target_audience = Column(String(255), nullable=True)
    estimated_length = Column(String(100), nullable=True)  # 예: "10부작", "120분"
    
    # 본문
    content = Column(Text, nullable=True)  # 메인 시놉시스 내용
    
    # 구조화된 데이터
    plot_points = Column(JSON, default=list)      # List[{title, description}]
    character_arcs = Column(JSON, default=list)   # List[{character_name, start_state, end_state, key_moment}]
    
    # 메타
    notes = Column(Text, nullable=True)
    version = Column(Integer, default=1)
    
    # AI 생성 여부
    ai_generated = Column(Boolean, default=False)
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

