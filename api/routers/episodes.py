"""
에피소드 API 라우터
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from models.database import get_db
from models.database.crud import (
    create_episode, get_episode, get_episodes_by_project,
    update_episode, delete_episode, get_scenes_by_episode,
    get_project
)
from models.schemas import EpisodeCreate, EpisodeUpdate

router = APIRouter()


@router.post("/", response_model=dict, summary="에피소드 생성")
async def create_new_episode(
    episode: EpisodeCreate,
    db: Session = Depends(get_db)
):
    """
    새 에피소드 생성
    
    - **project_id**: 프로젝트 ID (필수)
    - **episode_number**: 에피소드 번호 (필수)
    - **title**: 에피소드 제목 (필수)
    - **main_topic**: 메인 토픽
    - **sub_topics**: 서브 토픽 리스트
    """
    # 프로젝트 존재 확인
    project = get_project(db, episode.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    db_episode = create_episode(db, episode)
    return {
        "id": db_episode.id,
        "episode_number": db_episode.episode_number,
        "title": db_episode.title,
        "message": "에피소드가 생성되었습니다."
    }


@router.get("/by-project/{project_id}", response_model=List[dict], summary="프로젝트별 에피소드 목록")
async def list_episodes_by_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """프로젝트의 에피소드 목록을 조회합니다."""
    episodes = get_episodes_by_project(db, project_id)
    return [
        {
            "id": ep.id,
            "episode_number": ep.episode_number,
            "title": ep.title,
            "status": ep.status,
            "main_topic": ep.main_topic,
            "scene_count": len(ep.scenes),
            "broadcast_date": ep.broadcast_date.isoformat() if ep.broadcast_date else None,
            "created_at": ep.created_at.isoformat()
        }
        for ep in episodes
    ]


@router.get("/{episode_id}", response_model=dict, summary="에피소드 상세 조회")
async def get_episode_detail(
    episode_id: int,
    db: Session = Depends(get_db)
):
    """에피소드 상세 정보를 조회합니다."""
    db_episode = get_episode(db, episode_id)
    if not db_episode:
        raise HTTPException(status_code=404, detail="에피소드를 찾을 수 없습니다.")
    
    # 총 글자 수 계산
    total_words = sum(scene.word_count for scene in db_episode.scenes)
    
    return {
        "id": db_episode.id,
        "project_id": db_episode.project_id,
        "episode_number": db_episode.episode_number,
        "title": db_episode.title,
        "summary": db_episode.summary,
        "status": db_episode.status,
        "main_topic": db_episode.main_topic,
        "sub_topics": db_episode.sub_topics,
        "target_runtime": db_episode.target_runtime,
        "actual_runtime": db_episode.actual_runtime,
        "broadcast_date": db_episode.broadcast_date.isoformat() if db_episode.broadcast_date else None,
        "notes": db_episode.notes,
        "structure_summary": db_episode.structure_summary,
        "scene_count": len(db_episode.scenes),
        "total_words": total_words,
        "created_at": db_episode.created_at.isoformat(),
        "updated_at": db_episode.updated_at.isoformat()
    }


@router.put("/{episode_id}", response_model=dict, summary="에피소드 수정")
async def update_existing_episode(
    episode_id: int,
    episode: EpisodeUpdate,
    db: Session = Depends(get_db)
):
    """에피소드 정보를 수정합니다."""
    db_episode = update_episode(db, episode_id, episode)
    if not db_episode:
        raise HTTPException(status_code=404, detail="에피소드를 찾을 수 없습니다.")
    
    return {
        "id": db_episode.id,
        "title": db_episode.title,
        "message": "에피소드가 수정되었습니다."
    }


@router.delete("/{episode_id}", summary="에피소드 삭제")
async def delete_existing_episode(
    episode_id: int,
    db: Session = Depends(get_db)
):
    """에피소드를 삭제합니다. (관련된 모든 장면도 삭제됨)"""
    success = delete_episode(db, episode_id)
    if not success:
        raise HTTPException(status_code=404, detail="에피소드를 찾을 수 없습니다.")
    
    return {"message": "에피소드가 삭제되었습니다."}


@router.get("/{episode_id}/scenes", response_model=List[dict], summary="에피소드의 장면 목록")
async def list_episode_scenes(
    episode_id: int,
    db: Session = Depends(get_db)
):
    """에피소드에 포함된 장면 목록을 조회합니다."""
    db_episode = get_episode(db, episode_id)
    if not db_episode:
        raise HTTPException(status_code=404, detail="에피소드를 찾을 수 없습니다.")
    
    scenes = get_scenes_by_episode(db, episode_id)
    return [
        {
            "id": scene.id,
            "scene_id": scene.scene_id,
            "scene_number": scene.scene_number,
            "scene_type": scene.scene_type,
            "title": scene.title,
            "goal": scene.goal,
            "conflict_type": scene.conflict_type,
            "dialog_density": scene.dialog_density,
            "word_count": scene.word_count,
            "ai_generated": scene.ai_generated,
            "human_edited": scene.human_edited,
            "has_evaluation": scene.evaluation is not None
        }
        for scene in scenes
    ]


@router.get("/{episode_id}/full-script", response_model=dict, summary="에피소드 전체 대본")
async def get_full_script(
    episode_id: int,
    db: Session = Depends(get_db)
):
    """에피소드의 전체 대본을 조회합니다."""
    db_episode = get_episode(db, episode_id)
    if not db_episode:
        raise HTTPException(status_code=404, detail="에피소드를 찾을 수 없습니다.")
    
    scenes = get_scenes_by_episode(db, episode_id)
    
    full_content = []
    for scene in scenes:
        scene_header = f"## 장면 {scene.scene_number}: {scene.title or ''}"
        if scene.scene_type:
            scene_header += f" ({scene.scene_type})"
        
        full_content.append(scene_header)
        if scene.goal:
            full_content.append(f"**목표**: {scene.goal}")
        full_content.append("")
        full_content.append(scene.content or "")
        full_content.append("")
        full_content.append("---")
        full_content.append("")
    
    return {
        "episode_id": episode_id,
        "title": db_episode.title,
        "full_script": "\n".join(full_content),
        "scene_count": len(scenes),
        "total_words": sum(s.word_count for s in scenes)
    }

