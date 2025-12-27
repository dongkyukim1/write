"""
프로젝트 API 라우터
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from models.database import get_db
from models.database.crud import (
    create_project, get_project, get_projects, 
    update_project, delete_project, get_project_stats
)
from models.database.models import SynopsisModel
from models.schemas import ProjectCreate, ProjectUpdate, Project
from models.schemas.project import ProjectStatus

router = APIRouter()


# 시놉시스 스키마
class SynopsisCreate(BaseModel):
    title: str
    logline: Optional[str] = None
    premise: Optional[str] = None
    theme: Optional[str] = None
    genre: Optional[str] = None
    target_audience: Optional[str] = None
    estimated_length: Optional[str] = None
    content: Optional[str] = None
    plot_points: Optional[List[dict]] = []
    character_arcs: Optional[List[dict]] = []
    notes: Optional[str] = None
    version: int = 1


class SynopsisUpdate(BaseModel):
    title: Optional[str] = None
    logline: Optional[str] = None
    premise: Optional[str] = None
    theme: Optional[str] = None
    genre: Optional[str] = None
    target_audience: Optional[str] = None
    estimated_length: Optional[str] = None
    content: Optional[str] = None
    plot_points: Optional[List[dict]] = None
    character_arcs: Optional[List[dict]] = None
    notes: Optional[str] = None
    version: Optional[int] = None


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


# ==================== 시놉시스 API ====================

@router.get("/{project_id}/synopsis", response_model=dict, summary="시놉시스 조회")
async def get_synopsis(
    project_id: int,
    db: Session = Depends(get_db)
):
    """프로젝트의 시놉시스를 조회합니다."""
    # 프로젝트 존재 확인
    db_project = get_project(db, project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    # 시놉시스 조회
    synopsis = db.query(SynopsisModel).filter(SynopsisModel.project_id == project_id).first()
    if not synopsis:
        raise HTTPException(status_code=404, detail="시놉시스가 없습니다.")
    
    return {
        "id": synopsis.id,
        "project_id": synopsis.project_id,
        "title": synopsis.title,
        "logline": synopsis.logline,
        "premise": synopsis.premise,
        "theme": synopsis.theme,
        "genre": synopsis.genre,
        "target_audience": synopsis.target_audience,
        "estimated_length": synopsis.estimated_length,
        "content": synopsis.content,
        "plot_points": synopsis.plot_points or [],
        "character_arcs": synopsis.character_arcs or [],
        "notes": synopsis.notes,
        "version": synopsis.version,
        "ai_generated": synopsis.ai_generated,
        "created_at": synopsis.created_at.isoformat(),
        "updated_at": synopsis.updated_at.isoformat()
    }


@router.post("/{project_id}/synopsis", response_model=dict, summary="시놉시스 생성")
async def create_synopsis(
    project_id: int,
    synopsis_data: SynopsisCreate,
    db: Session = Depends(get_db)
):
    """프로젝트의 시놉시스를 생성합니다. (프로젝트당 1개)"""
    # 프로젝트 존재 확인
    db_project = get_project(db, project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    # 기존 시놉시스 확인
    existing = db.query(SynopsisModel).filter(SynopsisModel.project_id == project_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 시놉시스가 존재합니다. PUT 메서드로 수정하세요.")
    
    # 새 시놉시스 생성
    new_synopsis = SynopsisModel(
        project_id=project_id,
        title=synopsis_data.title,
        logline=synopsis_data.logline,
        premise=synopsis_data.premise,
        theme=synopsis_data.theme,
        genre=synopsis_data.genre,
        target_audience=synopsis_data.target_audience,
        estimated_length=synopsis_data.estimated_length,
        content=synopsis_data.content,
        plot_points=synopsis_data.plot_points or [],
        character_arcs=synopsis_data.character_arcs or [],
        notes=synopsis_data.notes,
        version=synopsis_data.version
    )
    
    db.add(new_synopsis)
    db.commit()
    db.refresh(new_synopsis)
    
    return {
        "id": new_synopsis.id,
        "project_id": new_synopsis.project_id,
        "title": new_synopsis.title,
        "message": "시놉시스가 생성되었습니다."
    }


@router.put("/{project_id}/synopsis", response_model=dict, summary="시놉시스 수정")
async def update_synopsis(
    project_id: int,
    synopsis_data: SynopsisUpdate,
    db: Session = Depends(get_db)
):
    """프로젝트의 시놉시스를 수정합니다."""
    # 프로젝트 존재 확인
    db_project = get_project(db, project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    # 시놉시스 조회
    synopsis = db.query(SynopsisModel).filter(SynopsisModel.project_id == project_id).first()
    if not synopsis:
        raise HTTPException(status_code=404, detail="시놉시스가 없습니다. POST 메서드로 먼저 생성하세요.")
    
    # 업데이트할 필드만 적용
    update_data = synopsis_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(synopsis, field, value)
    
    db.commit()
    db.refresh(synopsis)
    
    return {
        "id": synopsis.id,
        "project_id": synopsis.project_id,
        "title": synopsis.title,
        "version": synopsis.version,
        "message": "시놉시스가 수정되었습니다."
    }


@router.delete("/{project_id}/synopsis", summary="시놉시스 삭제")
async def delete_synopsis(
    project_id: int,
    db: Session = Depends(get_db)
):
    """프로젝트의 시놉시스를 삭제합니다."""
    # 시놉시스 조회
    synopsis = db.query(SynopsisModel).filter(SynopsisModel.project_id == project_id).first()
    if not synopsis:
        raise HTTPException(status_code=404, detail="시놉시스가 없습니다.")
    
    db.delete(synopsis)
    db.commit()
    
    return {"message": "시놉시스가 삭제되었습니다."}

