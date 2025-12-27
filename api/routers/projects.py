"""
프로젝트 API 라우터
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from models.database import get_db
from models.database.crud import (
    create_project, get_project, get_projects, 
    update_project, delete_project, get_project_stats
)
from models.schemas import ProjectCreate, ProjectUpdate, Project
from models.schemas.project import ProjectStatus

router = APIRouter()


@router.post("/", response_model=dict, summary="프로젝트 생성")
async def create_new_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    """
    새 프로젝트(대본 시리즈) 생성
    
    - **title**: 프로젝트 제목 (필수)
    - **project_type**: 프로젝트 타입 (talk_show, drama, movie 등)
    - **world_setting**: 세계관 설정
    - **style_guide**: 문체 가이드
    """
    db_project = create_project(db, project)
    return {
        "id": db_project.id,
        "title": db_project.title,
        "message": "프로젝트가 생성되었습니다."
    }


@router.get("/", response_model=List[dict], summary="프로젝트 목록 조회")
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """프로젝트 목록을 조회합니다."""
    projects = get_projects(db, skip=skip, limit=limit)
    return [
        {
            "id": p.id,
            "title": p.title,
            "project_type": p.project_type,
            "status": p.status,
            "episode_count": len(p.episodes),
            "character_count": len(p.characters),
            "created_at": p.created_at.isoformat(),
            "updated_at": p.updated_at.isoformat()
        }
        for p in projects
    ]


@router.get("/{project_id}", response_model=dict, summary="프로젝트 상세 조회")
async def get_project_detail(
    project_id: int,
    db: Session = Depends(get_db)
):
    """프로젝트 상세 정보를 조회합니다."""
    db_project = get_project(db, project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    stats = get_project_stats(db, project_id)
    
    return {
        "id": db_project.id,
        "title": db_project.title,
        "project_type": db_project.project_type,
        "description": db_project.description,
        "genre": db_project.genre,
        "target_audience": db_project.target_audience,
        "tone": db_project.tone,
        "status": db_project.status,
        "world_setting": db_project.world_setting,
        "style_guide": db_project.style_guide,
        "statistics": stats,
        "created_at": db_project.created_at.isoformat(),
        "updated_at": db_project.updated_at.isoformat()
    }


@router.put("/{project_id}", response_model=dict, summary="프로젝트 수정")
async def update_existing_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """프로젝트 정보를 수정합니다."""
    db_project = update_project(db, project_id, project)
    if not db_project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    return {
        "id": db_project.id,
        "title": db_project.title,
        "message": "프로젝트가 수정되었습니다."
    }


@router.delete("/{project_id}", summary="프로젝트 삭제")
async def delete_existing_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """프로젝트를 삭제합니다. (관련된 모든 에피소드, 장면, 캐릭터도 삭제됨)"""
    success = delete_project(db, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    return {"message": "프로젝트가 삭제되었습니다."}


@router.get("/{project_id}/context", response_model=dict, summary="프로젝트 컨텍스트 조회")
async def get_project_context(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    MCP에서 사용할 프로젝트 컨텍스트를 조회합니다.
    
    세계관 설정, 캐릭터 정보, 스타일 가이드 등이 포함됩니다.
    """
    db_project = get_project(db, project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    characters_context = []
    for char in db_project.characters:
        characters_context.append({
            "name": char.name,
            "role": char.role,
            "personality": char.personality_description or "",
            "speech_pattern": char.speech_pattern or "",
            "current_state": char.current_state,
            "forbidden_actions": char.forbidden_actions or []
        })
    
    return {
        "project_id": db_project.id,
        "title": db_project.title,
        "project_type": db_project.project_type,
        "world_setting": db_project.world_setting or "",
        "style_guide": db_project.style_guide or "",
        "tone": db_project.tone or "",
        "characters": characters_context
    }

