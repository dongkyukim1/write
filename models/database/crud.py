"""
CRUD 함수
데이터베이스 CRUD 작업을 수행하는 함수들
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from .models import (
    ProjectModel, EpisodeModel, SceneModel, 
    CharacterModel, EvaluationModel, CallbackModel
)
from models.schemas import (
    ProjectCreate, ProjectUpdate, Project,
    EpisodeCreate, EpisodeUpdate, Episode,
    SceneCreate, SceneUpdate, Scene,
    CharacterCreate, CharacterUpdate, Character,
    EvaluationCreate, Evaluation
)


# ==================== Project CRUD ====================

def create_project(db: Session, project: ProjectCreate) -> ProjectModel:
    """프로젝트 생성"""
    db_project = ProjectModel(
        title=project.title,
        project_type=project.project_type.value,
        description=project.description,
        genre=project.genre,
        target_audience=project.target_audience,
        tone=project.tone,
        world_setting=project.world_setting,
        style_guide=project.style_guide
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_project(db: Session, project_id: int) -> Optional[ProjectModel]:
    """프로젝트 조회"""
    return db.query(ProjectModel).filter(ProjectModel.id == project_id).first()


def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[ProjectModel]:
    """프로젝트 목록 조회"""
    return db.query(ProjectModel).offset(skip).limit(limit).all()


def update_project(db: Session, project_id: int, project: ProjectUpdate) -> Optional[ProjectModel]:
    """프로젝트 수정"""
    db_project = get_project(db, project_id)
    if not db_project:
        return None
    
    update_data = project.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(value, 'value'):  # Enum 처리
            value = value.value
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: Session, project_id: int) -> bool:
    """프로젝트 삭제"""
    db_project = get_project(db, project_id)
    if not db_project:
        return False
    
    db.delete(db_project)
    db.commit()
    return True


# ==================== Episode CRUD ====================

def create_episode(db: Session, episode: EpisodeCreate) -> EpisodeModel:
    """에피소드 생성"""
    db_episode = EpisodeModel(
        project_id=episode.project_id,
        episode_number=episode.episode_number,
        title=episode.title,
        summary=episode.summary,
        main_topic=episode.main_topic,
        sub_topics=episode.sub_topics or [],
        broadcast_date=episode.broadcast_date,
        target_runtime=episode.target_runtime,
        notes=episode.notes
    )
    db.add(db_episode)
    db.commit()
    db.refresh(db_episode)
    return db_episode


def get_episode(db: Session, episode_id: int) -> Optional[EpisodeModel]:
    """에피소드 조회"""
    return db.query(EpisodeModel).filter(EpisodeModel.id == episode_id).first()


def get_episodes_by_project(db: Session, project_id: int) -> List[EpisodeModel]:
    """프로젝트의 에피소드 목록 조회"""
    return db.query(EpisodeModel).filter(
        EpisodeModel.project_id == project_id
    ).order_by(EpisodeModel.episode_number).all()


def update_episode(db: Session, episode_id: int, episode: EpisodeUpdate) -> Optional[EpisodeModel]:
    """에피소드 수정"""
    db_episode = get_episode(db, episode_id)
    if not db_episode:
        return None
    
    update_data = episode.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(value, 'value'):
            value = value.value
        setattr(db_episode, field, value)
    
    db.commit()
    db.refresh(db_episode)
    return db_episode


def delete_episode(db: Session, episode_id: int) -> bool:
    """에피소드 삭제"""
    db_episode = get_episode(db, episode_id)
    if not db_episode:
        return False
    
    db.delete(db_episode)
    db.commit()
    return True


# ==================== Scene CRUD ====================

def generate_scene_id(db: Session, episode: EpisodeModel, scene_number: int) -> str:
    """장면 ID 생성 (예: S01E03_SC02) - 중복 시 suffix 추가"""
    season = 1  # 기본값, 필요시 확장
    base_id = f"S{season:02d}E{episode.episode_number:02d}_SC{scene_number:02d}"
    
    # 중복 체크
    existing = db.query(SceneModel).filter(SceneModel.scene_id == base_id).first()
    if not existing:
        return base_id
    
    # 중복이면 suffix 추가
    suffix = 1
    while True:
        new_id = f"{base_id}_{suffix}"
        existing = db.query(SceneModel).filter(SceneModel.scene_id == new_id).first()
        if not existing:
            return new_id
        suffix += 1
        if suffix > 100:  # 무한 루프 방지
            import time
            return f"{base_id}_{int(time.time())}"


def create_scene(db: Session, scene: SceneCreate) -> SceneModel:
    """장면 생성"""
    episode = get_episode(db, scene.episode_id)
    if not episode:
        raise ValueError(f"에피소드 ID {scene.episode_id}를 찾을 수 없습니다.")
    
    scene_id = generate_scene_id(db, episode, scene.scene_number)
    
    db_scene = SceneModel(
        episode_id=scene.episode_id,
        scene_number=scene.scene_number,
        scene_id=scene_id,
        scene_type=scene.scene_type.value,
        title=scene.title,
        goal=scene.goal,
        emotion_curve=[e.value for e in scene.emotion_curve],
        conflict_type=scene.conflict_type.value,
        dialog_density=scene.dialog_density.value,
        character_ids=scene.character_ids,
        content=scene.content,
        writer_notes=scene.writer_notes,
        word_count=len(scene.content) if scene.content else 0
    )
    db.add(db_scene)
    db.commit()
    db.refresh(db_scene)
    return db_scene


def get_scene(db: Session, scene_id: int) -> Optional[SceneModel]:
    """장면 조회 (DB ID로)"""
    return db.query(SceneModel).filter(SceneModel.id == scene_id).first()


def get_scene_by_scene_id(db: Session, scene_id: str) -> Optional[SceneModel]:
    """장면 조회 (장면 ID로, 예: S01E03_SC02)"""
    return db.query(SceneModel).filter(SceneModel.scene_id == scene_id).first()


def get_scenes_by_episode(db: Session, episode_id: int) -> List[SceneModel]:
    """에피소드의 장면 목록 조회"""
    return db.query(SceneModel).filter(
        SceneModel.episode_id == episode_id
    ).order_by(SceneModel.scene_number).all()


def update_scene(db: Session, scene_id: int, scene: SceneUpdate) -> Optional[SceneModel]:
    """장면 수정"""
    db_scene = get_scene(db, scene_id)
    if not db_scene:
        return None
    
    update_data = scene.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == 'emotion_curve' and value:
            value = [e.value if hasattr(e, 'value') else e for e in value]
        elif hasattr(value, 'value'):
            value = value.value
        setattr(db_scene, field, value)
    
    # 내용이 수정되면 word_count 업데이트
    if scene.content is not None:
        db_scene.word_count = len(scene.content)
    
    db.commit()
    db.refresh(db_scene)
    return db_scene


def delete_scene(db: Session, scene_id: int) -> bool:
    """장면 삭제"""
    db_scene = get_scene(db, scene_id)
    if not db_scene:
        return False
    
    db.delete(db_scene)
    db.commit()
    return True


# ==================== Character CRUD ====================

def create_character(db: Session, character: CharacterCreate) -> CharacterModel:
    """캐릭터 생성"""
    db_character = CharacterModel(
        project_id=character.project_id,
        name=character.name,
        role=character.role.value,
        description=character.description,
        backstory=character.backstory,
        personality_traits=[t.value for t in character.personality_traits],
        personality_description=character.personality_description,
        speech_pattern=character.speech_pattern,
        speech_examples=character.speech_examples,
        forbidden_actions=character.forbidden_actions
    )
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character


def get_character(db: Session, character_id: int) -> Optional[CharacterModel]:
    """캐릭터 조회"""
    return db.query(CharacterModel).filter(CharacterModel.id == character_id).first()


def get_characters_by_project(db: Session, project_id: int) -> List[CharacterModel]:
    """프로젝트의 캐릭터 목록 조회"""
    return db.query(CharacterModel).filter(
        CharacterModel.project_id == project_id
    ).all()


def update_character(db: Session, character_id: int, character: CharacterUpdate) -> Optional[CharacterModel]:
    """캐릭터 수정"""
    db_character = get_character(db, character_id)
    if not db_character:
        return None
    
    update_data = character.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == 'personality_traits' and value:
            value = [t.value if hasattr(t, 'value') else t for t in value]
        elif hasattr(value, 'value'):
            value = value.value
        setattr(db_character, field, value)
    
    db.commit()
    db.refresh(db_character)
    return db_character


def delete_character(db: Session, character_id: int) -> bool:
    """캐릭터 삭제"""
    db_character = get_character(db, character_id)
    if not db_character:
        return False
    
    db.delete(db_character)
    db.commit()
    return True


# ==================== Evaluation CRUD ====================

def create_evaluation(db: Session, evaluation: EvaluationCreate) -> EvaluationModel:
    """평가 생성"""
    db_evaluation = EvaluationModel(
        scene_id=evaluation.scene_id,
        creativity_score=evaluation.creativity_score,
        consistency_score=evaluation.consistency_score,
        emotion_score=evaluation.emotion_score,
        pacing_score=evaluation.pacing_score,
        dialogue_score=evaluation.dialogue_score,
        overall_score=evaluation.overall_score,
        cliche_detected=evaluation.cliche_detected,
        cliches=[c.model_dump() for c in evaluation.cliches],
        issues=[i.model_dump() for i in evaluation.issues],
        summary=evaluation.summary,
        suggestions=evaluation.suggestions,
        strengths=evaluation.strengths
    )
    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)
    return db_evaluation


def get_evaluation(db: Session, evaluation_id: int) -> Optional[EvaluationModel]:
    """평가 조회"""
    return db.query(EvaluationModel).filter(EvaluationModel.id == evaluation_id).first()


def get_evaluation_by_scene(db: Session, scene_id: int) -> Optional[EvaluationModel]:
    """장면의 평가 조회"""
    return db.query(EvaluationModel).filter(EvaluationModel.scene_id == scene_id).first()


def update_evaluation(db: Session, scene_id: int, evaluation: EvaluationCreate) -> EvaluationModel:
    """평가 업데이트 (기존 평가 교체)"""
    db_evaluation = get_evaluation_by_scene(db, scene_id)
    if db_evaluation:
        db.delete(db_evaluation)
        db.commit()
    
    return create_evaluation(db, evaluation)


# ==================== Callback (복선) CRUD ====================

def create_callback(db: Session, project_id: int, content: str, 
                   setup_scene_id: Optional[int] = None,
                   setup_episode_number: Optional[int] = None,
                   description: Optional[str] = None,
                   importance: str = "medium") -> CallbackModel:
    """복선 생성"""
    db_callback = CallbackModel(
        project_id=project_id,
        content=content,
        description=description,
        setup_scene_id=setup_scene_id,
        setup_episode_number=setup_episode_number,
        importance=importance
    )
    db.add(db_callback)
    db.commit()
    db.refresh(db_callback)
    return db_callback


def get_callbacks_by_project(db: Session, project_id: int, 
                             resolved: Optional[bool] = None) -> List[CallbackModel]:
    """프로젝트의 복선 목록 조회"""
    query = db.query(CallbackModel).filter(CallbackModel.project_id == project_id)
    if resolved is not None:
        query = query.filter(CallbackModel.resolved == resolved)
    return query.all()


def resolve_callback(db: Session, callback_id: int, 
                    payoff_scene_id: int, payoff_episode_number: int) -> Optional[CallbackModel]:
    """복선 회수"""
    db_callback = db.query(CallbackModel).filter(CallbackModel.id == callback_id).first()
    if not db_callback:
        return None
    
    db_callback.resolved = True
    db_callback.payoff_scene_id = payoff_scene_id
    db_callback.payoff_episode_number = payoff_episode_number
    
    db.commit()
    db.refresh(db_callback)
    return db_callback


# ==================== 통계 함수 ====================

def get_project_stats(db: Session, project_id: int) -> Dict[str, Any]:
    """프로젝트 통계 조회"""
    project = get_project(db, project_id)
    if not project:
        return {}
    
    total_episodes = len(project.episodes)
    total_scenes = sum(len(ep.scenes) for ep in project.episodes)
    total_words = db.query(func.sum(SceneModel.word_count)).join(EpisodeModel).filter(
        EpisodeModel.project_id == project_id
    ).scalar() or 0
    
    # 평균 평가 점수
    avg_scores = db.query(
        func.avg(EvaluationModel.overall_score),
        func.avg(EvaluationModel.creativity_score)
    ).join(SceneModel).join(EpisodeModel).filter(
        EpisodeModel.project_id == project_id
    ).first()
    
    return {
        "total_episodes": total_episodes,
        "total_scenes": total_scenes,
        "total_words": total_words,
        "total_characters": len(project.characters),
        "avg_overall_score": avg_scores[0],
        "avg_creativity_score": avg_scores[1]
    }

