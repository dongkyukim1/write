"""
평가 API 라우터
AI 평가 결과 관리
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from models.database import get_db
from models.database.crud import (
    create_evaluation, get_evaluation, get_evaluation_by_scene,
    update_evaluation, get_scene
)
from models.schemas import EvaluationCreate
from models.schemas.evaluation import EvaluationResult

router = APIRouter()


@router.post("/", response_model=dict, summary="평가 저장")
async def save_evaluation(
    evaluation: EvaluationCreate,
    db: Session = Depends(get_db)
):
    """
    장면에 대한 AI 평가 결과를 저장합니다.
    
    - **scene_id**: 평가 대상 장면 ID (필수)
    - **creativity_score**: 창의성 점수 (0.0 ~ 1.0)
    - **consistency_score**: 일관성 점수
    - **emotion_score**: 감정 전달 점수
    - **pacing_score**: 페이싱 점수
    - **dialogue_score**: 대화 퀄리티 점수
    - **overall_score**: 종합 점수
    - **cliche_detected**: 클리셰 감지 여부
    - **cliches**: 감지된 클리셰 목록
    - **issues**: 발견된 이슈 목록
    - **summary**: 평가 요약
    - **suggestions**: 개선 제안 목록
    """
    # 장면 존재 확인
    scene = get_scene(db, evaluation.scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="장면을 찾을 수 없습니다.")
    
    # 기존 평가가 있으면 교체
    db_evaluation = update_evaluation(db, evaluation.scene_id, evaluation)
    
    return {
        "id": db_evaluation.id,
        "scene_id": db_evaluation.scene_id,
        "overall_score": db_evaluation.overall_score,
        "creativity_score": db_evaluation.creativity_score,
        "cliche_detected": db_evaluation.cliche_detected,
        "message": "평가가 저장되었습니다."
    }


@router.get("/by-scene/{scene_id}", response_model=dict, summary="장면의 평가 조회")
async def get_scene_evaluation(
    scene_id: int,
    db: Session = Depends(get_db)
):
    """장면에 대한 평가 결과를 조회합니다."""
    db_evaluation = get_evaluation_by_scene(db, scene_id)
    if not db_evaluation:
        raise HTTPException(status_code=404, detail="평가를 찾을 수 없습니다.")
    
    return {
        "id": db_evaluation.id,
        "scene_id": db_evaluation.scene_id,
        "scores": {
            "creativity": db_evaluation.creativity_score,
            "consistency": db_evaluation.consistency_score,
            "emotion": db_evaluation.emotion_score,
            "pacing": db_evaluation.pacing_score,
            "dialogue": db_evaluation.dialogue_score,
            "overall": db_evaluation.overall_score
        },
        "cliche_detected": db_evaluation.cliche_detected,
        "cliches": db_evaluation.cliches,
        "issues": db_evaluation.issues,
        "summary": db_evaluation.summary,
        "suggestions": db_evaluation.suggestions,
        "strengths": db_evaluation.strengths,
        "evaluator_model": db_evaluation.evaluator_model,
        "created_at": db_evaluation.created_at.isoformat()
    }


@router.get("/by-scene/{scene_id}/summary", response_model=dict, summary="평가 요약 조회")
async def get_evaluation_summary(
    scene_id: int,
    db: Session = Depends(get_db)
):
    """장면 평가의 간략한 요약을 조회합니다."""
    db_evaluation = get_evaluation_by_scene(db, scene_id)
    if not db_evaluation:
        raise HTTPException(status_code=404, detail="평가를 찾을 수 없습니다.")
    
    needs_revision = (
        db_evaluation.overall_score < 0.6 or 
        any(issue.get('severity') == 'error' for issue in db_evaluation.issues)
    )
    
    return {
        "scene_id": scene_id,
        "overall_score": db_evaluation.overall_score,
        "creativity_score": db_evaluation.creativity_score,
        "cliche_detected": db_evaluation.cliche_detected,
        "issue_count": len(db_evaluation.issues),
        "needs_revision": needs_revision,
        "summary": db_evaluation.summary
    }


@router.get("/needs-revision", response_model=List[dict], summary="수정 필요 장면 목록")
async def list_scenes_needing_revision(
    project_id: Optional[int] = None,
    threshold: float = Query(0.6, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    """
    수정이 필요한 장면 목록을 조회합니다.
    
    overall_score가 threshold 미만이거나 심각한 이슈가 있는 장면을 반환합니다.
    """
    from models.database.models import EvaluationModel, SceneModel, EpisodeModel
    
    query = db.query(EvaluationModel, SceneModel).join(
        SceneModel, EvaluationModel.scene_id == SceneModel.id
    ).filter(
        EvaluationModel.overall_score < threshold
    )
    
    if project_id:
        query = query.join(EpisodeModel).filter(EpisodeModel.project_id == project_id)
    
    results = query.all()
    
    return [
        {
            "scene_id": scene.id,
            "scene_id_str": scene.scene_id,
            "episode_id": scene.episode_id,
            "title": scene.title,
            "overall_score": eval.overall_score,
            "creativity_score": eval.creativity_score,
            "cliche_detected": eval.cliche_detected,
            "issue_count": len(eval.issues),
            "summary": eval.summary,
            "top_suggestions": eval.suggestions[:3] if eval.suggestions else []
        }
        for eval, scene in results
    ]


@router.get("/statistics", response_model=dict, summary="평가 통계")
async def get_evaluation_statistics(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """프로젝트 또는 전체 평가 통계를 조회합니다."""
    from sqlalchemy import func
    from models.database.models import EvaluationModel, SceneModel, EpisodeModel
    
    query = db.query(
        func.avg(EvaluationModel.overall_score).label('avg_overall'),
        func.avg(EvaluationModel.creativity_score).label('avg_creativity'),
        func.avg(EvaluationModel.consistency_score).label('avg_consistency'),
        func.avg(EvaluationModel.emotion_score).label('avg_emotion'),
        func.avg(EvaluationModel.pacing_score).label('avg_pacing'),
        func.avg(EvaluationModel.dialogue_score).label('avg_dialogue'),
        func.count(EvaluationModel.id).label('total_evaluations'),
        func.sum(func.cast(EvaluationModel.cliche_detected, Integer)).label('cliche_count')
    )
    
    if project_id:
        query = query.join(SceneModel).join(EpisodeModel).filter(
            EpisodeModel.project_id == project_id
        )
    
    from sqlalchemy import Integer
    result = query.first()
    
    return {
        "total_evaluations": result.total_evaluations or 0,
        "average_scores": {
            "overall": round(result.avg_overall or 0, 3),
            "creativity": round(result.avg_creativity or 0, 3),
            "consistency": round(result.avg_consistency or 0, 3),
            "emotion": round(result.avg_emotion or 0, 3),
            "pacing": round(result.avg_pacing or 0, 3),
            "dialogue": round(result.avg_dialogue or 0, 3)
        },
        "cliche_detection_rate": round(
            (result.cliche_count or 0) / max(result.total_evaluations or 1, 1), 
            3
        )
    }

