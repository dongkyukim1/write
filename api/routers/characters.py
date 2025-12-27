"""
캐릭터 API 라우터
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from models.database import get_db
from models.database.crud import (
    create_character, get_character, get_characters_by_project,
    update_character, delete_character, get_project
)
from models.schemas import CharacterCreate, CharacterUpdate
from models.schemas.character import CharacterContext

router = APIRouter()


@router.post("/", response_model=dict, summary="캐릭터 생성")
async def create_new_character(
    character: CharacterCreate,
    db: Session = Depends(get_db)
):
    """
    새 캐릭터 생성
    
    - **project_id**: 프로젝트 ID (필수)
    - **name**: 캐릭터 이름 (필수)
    - **role**: 역할 (protagonist, host, co_host 등)
    - **personality_traits**: 성격 특성 리스트
    - **speech_pattern**: 말투 특징
    - **forbidden_actions**: 금지 설정 리스트
    """
    # 프로젝트 존재 확인
    project = get_project(db, character.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    db_character = create_character(db, character)
    return {
        "id": db_character.id,
        "name": db_character.name,
        "role": db_character.role,
        "message": "캐릭터가 생성되었습니다."
    }


@router.get("/by-project/{project_id}", response_model=List[dict], summary="프로젝트별 캐릭터 목록")
async def list_characters_by_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """프로젝트의 캐릭터 목록을 조회합니다."""
    characters = get_characters_by_project(db, project_id)
    return [
        {
            "id": char.id,
            "name": char.name,
            "role": char.role,
            "description": char.description,
            "personality_traits": char.personality_traits,
            "current_state": char.current_state,
            "total_appearances": char.total_appearances
        }
        for char in characters
    ]


@router.get("/{character_id}", response_model=dict, summary="캐릭터 상세 조회")
async def get_character_detail(
    character_id: int,
    db: Session = Depends(get_db)
):
    """캐릭터 상세 정보를 조회합니다."""
    db_character = get_character(db, character_id)
    if not db_character:
        raise HTTPException(status_code=404, detail="캐릭터를 찾을 수 없습니다.")
    
    return {
        "id": db_character.id,
        "project_id": db_character.project_id,
        "name": db_character.name,
        "role": db_character.role,
        "description": db_character.description,
        "backstory": db_character.backstory,
        "personality_traits": db_character.personality_traits,
        "personality_description": db_character.personality_description,
        "speech_pattern": db_character.speech_pattern,
        "speech_examples": db_character.speech_examples,
        "current_state": db_character.current_state,
        "forbidden_actions": db_character.forbidden_actions,
        "total_appearances": db_character.total_appearances,
        "total_dialogues": db_character.total_dialogues,
        "created_at": db_character.created_at.isoformat(),
        "updated_at": db_character.updated_at.isoformat()
    }


@router.put("/{character_id}", response_model=dict, summary="캐릭터 수정")
async def update_existing_character(
    character_id: int,
    character: CharacterUpdate,
    db: Session = Depends(get_db)
):
    """캐릭터 정보를 수정합니다."""
    db_character = update_character(db, character_id, character)
    if not db_character:
        raise HTTPException(status_code=404, detail="캐릭터를 찾을 수 없습니다.")
    
    return {
        "id": db_character.id,
        "name": db_character.name,
        "message": "캐릭터가 수정되었습니다."
    }


@router.delete("/{character_id}", summary="캐릭터 삭제")
async def delete_existing_character(
    character_id: int,
    db: Session = Depends(get_db)
):
    """캐릭터를 삭제합니다."""
    success = delete_character(db, character_id)
    if not success:
        raise HTTPException(status_code=404, detail="캐릭터를 찾을 수 없습니다.")
    
    return {"message": "캐릭터가 삭제되었습니다."}


@router.put("/{character_id}/state", response_model=dict, summary="캐릭터 현재 상태 업데이트")
async def update_character_state(
    character_id: int,
    state: str,
    db: Session = Depends(get_db)
):
    """
    캐릭터의 현재 상태를 업데이트합니다.
    
    에피소드 진행에 따른 캐릭터 상태 변화를 추적합니다.
    """
    db_character = get_character(db, character_id)
    if not db_character:
        raise HTTPException(status_code=404, detail="캐릭터를 찾을 수 없습니다.")
    
    db_character.current_state = state
    db.commit()
    
    return {
        "id": db_character.id,
        "name": db_character.name,
        "current_state": state,
        "message": "캐릭터 상태가 업데이트되었습니다."
    }


@router.get("/{character_id}/context", response_model=dict, summary="MCP용 캐릭터 컨텍스트")
async def get_character_context(
    character_id: int,
    db: Session = Depends(get_db)
):
    """
    MCP에서 사용할 캐릭터 컨텍스트를 조회합니다.
    
    AI가 대본 생성 시 참조할 캐릭터 정보를 압축된 형태로 반환합니다.
    """
    db_character = get_character(db, character_id)
    if not db_character:
        raise HTTPException(status_code=404, detail="캐릭터를 찾을 수 없습니다.")
    
    return {
        "name": db_character.name,
        "role": db_character.role,
        "personality_summary": db_character.personality_description or "",
        "speech_pattern": db_character.speech_pattern or "",
        "current_state": db_character.current_state,
        "key_traits": db_character.personality_traits or [],
        "forbidden_actions": db_character.forbidden_actions or [],
        "speech_examples": db_character.speech_examples[:3] if db_character.speech_examples else []
    }


@router.post("/{character_id}/add-speech-example", response_model=dict, summary="대사 예시 추가")
async def add_speech_example(
    character_id: int,
    example: str,
    db: Session = Depends(get_db)
):
    """캐릭터에 대사 예시를 추가합니다."""
    db_character = get_character(db, character_id)
    if not db_character:
        raise HTTPException(status_code=404, detail="캐릭터를 찾을 수 없습니다.")
    
    examples = db_character.speech_examples or []
    examples.append(example)
    db_character.speech_examples = examples
    db.commit()
    
    return {
        "id": db_character.id,
        "name": db_character.name,
        "speech_examples_count": len(examples),
        "message": "대사 예시가 추가되었습니다."
    }

