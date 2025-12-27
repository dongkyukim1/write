"""
장면(Scene) API 라우터
대본의 핵심 단위 - 구조화된 메타데이터 포함
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from models.database import get_db
from models.database.crud import (
    create_scene, get_scene, get_scene_by_scene_id,
    get_scenes_by_episode, update_scene, delete_scene,
    get_episode, get_evaluation_by_scene
)
from models.schemas import SceneCreate, SceneUpdate
from models.schemas.scene import ConflictType, EmotionCurve, DialogDensity, SceneType

router = APIRouter()


@router.post("/", response_model=dict, summary="장면 생성")
async def create_new_scene(
    scene: SceneCreate,
    db: Session = Depends(get_db)
):
    """
    새 장면 생성
    
    구조화된 메타데이터와 함께 장면을 저장합니다.
    
    - **episode_id**: 에피소드 ID (필수)
    - **scene_number**: 장면 번호 (필수)
    - **scene_type**: 장면 타입 (opening, talk, highlight 등)
    - **emotion_curve**: 감정 흐름 (예: ["tension", "climax", "resolution"])
    - **conflict_type**: 갈등 유형 (relationship, internal, external 등)
    - **dialog_density**: 대화 밀도 (high, medium, low)
    - **content**: 장면 본문
    """
    try:
        db_scene = create_scene(db, scene)
        return {
            "id": db_scene.id,
            "scene_id": db_scene.scene_id,
            "scene_number": db_scene.scene_number,
            "message": "장면이 생성되었습니다."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{scene_id}", response_model=dict, summary="장면 상세 조회")
async def get_scene_detail(
    scene_id: int,
    db: Session = Depends(get_db)
):
    """장면 상세 정보를 조회합니다."""
    db_scene = get_scene(db, scene_id)
    if not db_scene:
        raise HTTPException(status_code=404, detail="장면을 찾을 수 없습니다.")
    
    evaluation_summary = None
    if db_scene.evaluation:
        evaluation_summary = {
            "overall_score": db_scene.evaluation.overall_score,
            "creativity_score": db_scene.evaluation.creativity_score,
            "cliche_detected": db_scene.evaluation.cliche_detected,
            "summary": db_scene.evaluation.summary
        }
    
    return {
        "id": db_scene.id,
        "scene_id": db_scene.scene_id,
        "episode_id": db_scene.episode_id,
        "scene_number": db_scene.scene_number,
        "scene_type": db_scene.scene_type,
        "title": db_scene.title,
        "goal": db_scene.goal,
        "emotion_curve": db_scene.emotion_curve,
        "conflict_type": db_scene.conflict_type,
        "dialog_density": db_scene.dialog_density,
        "character_ids": db_scene.character_ids,
        "content": db_scene.content,
        "writer_notes": db_scene.writer_notes,
        "ai_generated": db_scene.ai_generated,
        "human_edited": db_scene.human_edited,
        "word_count": db_scene.word_count,
        "version": db_scene.version,
        "evaluation": evaluation_summary,
        "created_at": db_scene.created_at.isoformat(),
        "updated_at": db_scene.updated_at.isoformat()
    }


@router.get("/by-scene-id/{scene_id_str}", response_model=dict, summary="장면 ID로 조회")
async def get_scene_by_id_string(
    scene_id_str: str,
    db: Session = Depends(get_db)
):
    """장면 ID 문자열(예: S01E03_SC02)로 장면을 조회합니다."""
    db_scene = get_scene_by_scene_id(db, scene_id_str)
    if not db_scene:
        raise HTTPException(status_code=404, detail="장면을 찾을 수 없습니다.")
    
    return {
        "id": db_scene.id,
        "scene_id": db_scene.scene_id,
        "episode_id": db_scene.episode_id,
        "scene_number": db_scene.scene_number,
        "scene_type": db_scene.scene_type,
        "title": db_scene.title,
        "content": db_scene.content,
        "word_count": db_scene.word_count
    }


@router.put("/{scene_id}", response_model=dict, summary="장면 수정")
async def update_existing_scene(
    scene_id: int,
    scene: SceneUpdate,
    db: Session = Depends(get_db)
):
    """
    장면을 수정합니다.
    
    수정 시 human_edited 플래그를 True로 설정하는 것을 권장합니다.
    """
    db_scene = update_scene(db, scene_id, scene)
    if not db_scene:
        raise HTTPException(status_code=404, detail="장면을 찾을 수 없습니다.")
    
    return {
        "id": db_scene.id,
        "scene_id": db_scene.scene_id,
        "message": "장면이 수정되었습니다."
    }


@router.delete("/{scene_id}", summary="장면 삭제")
async def delete_existing_scene(
    scene_id: int,
    db: Session = Depends(get_db)
):
    """장면을 삭제합니다."""
    success = delete_scene(db, scene_id)
    if not success:
        raise HTTPException(status_code=404, detail="장면을 찾을 수 없습니다.")
    
    return {"message": "장면이 삭제되었습니다."}


@router.post("/{scene_id}/mark-ai-generated", response_model=dict, summary="AI 생성 표시")
async def mark_as_ai_generated(
    scene_id: int,
    prompt: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """장면을 AI 생성으로 표시합니다."""
    db_scene = get_scene(db, scene_id)
    if not db_scene:
        raise HTTPException(status_code=404, detail="장면을 찾을 수 없습니다.")
    
    db_scene.ai_generated = True
    if prompt:
        db_scene.generation_prompt = prompt
    
    db.commit()
    
    return {
        "id": db_scene.id,
        "scene_id": db_scene.scene_id,
        "ai_generated": True,
        "message": "AI 생성으로 표시되었습니다."
    }


@router.post("/{scene_id}/mark-human-edited", response_model=dict, summary="사람 수정 표시")
async def mark_as_human_edited(
    scene_id: int,
    db: Session = Depends(get_db)
):
    """장면을 사람이 수정한 것으로 표시합니다."""
    db_scene = get_scene(db, scene_id)
    if not db_scene:
        raise HTTPException(status_code=404, detail="장면을 찾을 수 없습니다.")
    
    db_scene.human_edited = True
    db.commit()
    
    return {
        "id": db_scene.id,
        "scene_id": db_scene.scene_id,
        "human_edited": True,
        "message": "사람 수정으로 표시되었습니다."
    }


@router.get("/search/by-metadata", response_model=List[dict], summary="메타데이터로 장면 검색")
async def search_scenes_by_metadata(
    conflict_type: Optional[ConflictType] = None,
    emotion: Optional[EmotionCurve] = None,
    dialog_density: Optional[DialogDensity] = None,
    scene_type: Optional[SceneType] = None,
    ai_generated: Optional[bool] = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    메타데이터로 장면을 검색합니다.
    
    "이런 장면 다시 만들어줘" 기능을 위한 엔드포인트입니다.
    """
    from models.database.models import SceneModel
    
    query = db.query(SceneModel)
    
    if conflict_type:
        query = query.filter(SceneModel.conflict_type == conflict_type.value)
    
    if dialog_density:
        query = query.filter(SceneModel.dialog_density == dialog_density.value)
    
    if scene_type:
        query = query.filter(SceneModel.scene_type == scene_type.value)
    
    if ai_generated is not None:
        query = query.filter(SceneModel.ai_generated == ai_generated)
    
    # emotion_curve는 JSON 배열이므로 별도 처리 필요
    scenes = query.limit(limit).all()
    
    # emotion 필터링 (Python에서 처리)
    if emotion:
        scenes = [s for s in scenes if emotion.value in (s.emotion_curve or [])]
    
    return [
        {
            "id": scene.id,
            "scene_id": scene.scene_id,
            "episode_id": scene.episode_id,
            "scene_type": scene.scene_type,
            "title": scene.title,
            "goal": scene.goal,
            "emotion_curve": scene.emotion_curve,
            "conflict_type": scene.conflict_type,
            "dialog_density": scene.dialog_density,
            "word_count": scene.word_count,
            "content_preview": (scene.content or "")[:200] + "..." if scene.content and len(scene.content) > 200 else scene.content
        }
        for scene in scenes
    ]

