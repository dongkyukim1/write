"""
Pydantic 스키마 모듈
대본 작성 시스템의 모든 데이터 모델을 정의합니다.
"""

from .project import Project, ProjectCreate, ProjectUpdate
from .episode import Episode, EpisodeCreate, EpisodeUpdate
from .scene import Scene, SceneCreate, SceneUpdate, EmotionCurve, ConflictType
from .character import Character, CharacterCreate, CharacterUpdate, CharacterRelationship
from .evaluation import Evaluation, EvaluationCreate, EvaluationResult

__all__ = [
    # Project
    "Project", "ProjectCreate", "ProjectUpdate",
    # Episode
    "Episode", "EpisodeCreate", "EpisodeUpdate",
    # Scene
    "Scene", "SceneCreate", "SceneUpdate", "EmotionCurve", "ConflictType",
    # Character
    "Character", "CharacterCreate", "CharacterUpdate", "CharacterRelationship",
    # Evaluation
    "Evaluation", "EvaluationCreate", "EvaluationResult",
]

