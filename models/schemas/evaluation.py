"""
평가 스키마
AI 평가 결과의 데이터 모델
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .base import BaseSchema, TimestampMixin


class EvaluationCategory(str, Enum):
    """평가 카테고리"""
    CREATIVITY = "creativity"           # 창의성
    CONSISTENCY = "consistency"         # 일관성
    EMOTION = "emotion"                 # 감정 전달
    PACING = "pacing"                   # 페이싱
    DIALOGUE = "dialogue"               # 대화 퀄리티
    STRUCTURE = "structure"             # 구조
    OVERALL = "overall"                 # 종합


class SeverityLevel(str, Enum):
    """심각도 레벨"""
    INFO = "info"                       # 참고 사항
    WARNING = "warning"                 # 경고
    ERROR = "error"                     # 심각한 문제


class ClicheType(str, Enum):
    """클리셰 유형"""
    DIALOGUE = "dialogue"               # 대사 클리셰
    PLOT = "plot"                       # 플롯 클리셰
    CHARACTER = "character"             # 캐릭터 클리셰
    ENDING = "ending"                   # 결말 클리셰
    TRANSITION = "transition"           # 전환 클리셰


class EvaluationIssue(BaseModel):
    """평가에서 발견된 이슈"""
    category: EvaluationCategory
    severity: SeverityLevel
    message: str
    line_reference: Optional[int] = None  # 해당 라인 번호
    suggestion: Optional[str] = None       # 개선 제안


class ClicheDetection(BaseModel):
    """클리셰 감지 결과"""
    cliche_type: ClicheType
    detected_text: str
    explanation: str
    alternatives: List[str] = Field(default_factory=list)  # 대안 제시


class EvaluationBase(BaseModel):
    """평가 기본 필드"""
    scene_id: int = Field(..., description="평가 대상 장면 ID")


class EvaluationCreate(EvaluationBase):
    """평가 생성 스키마 (AI가 생성)"""
    # 점수들 (0.0 ~ 1.0)
    creativity_score: float = Field(..., ge=0.0, le=1.0, description="창의성 점수")
    consistency_score: float = Field(..., ge=0.0, le=1.0, description="일관성 점수")
    emotion_score: float = Field(..., ge=0.0, le=1.0, description="감정 전달 점수")
    pacing_score: float = Field(..., ge=0.0, le=1.0, description="페이싱 점수")
    dialogue_score: float = Field(..., ge=0.0, le=1.0, description="대화 퀄리티 점수")
    overall_score: float = Field(..., ge=0.0, le=1.0, description="종합 점수")
    
    # 클리셰 감지
    cliche_detected: bool = False
    cliches: List[ClicheDetection] = Field(default_factory=list)
    
    # 이슈 목록
    issues: List[EvaluationIssue] = Field(default_factory=list)
    
    # 전체 피드백
    summary: str = Field(..., description="평가 요약")
    suggestions: List[str] = Field(default_factory=list, description="개선 제안들")
    
    # 강점
    strengths: List[str] = Field(default_factory=list, description="잘된 점들")


class Evaluation(EvaluationBase, TimestampMixin, BaseSchema):
    """평가 전체 스키마"""
    id: int
    
    # 점수들
    creativity_score: float
    consistency_score: float
    emotion_score: float
    pacing_score: float
    dialogue_score: float
    overall_score: float
    
    # 클리셰 감지
    cliche_detected: bool = False
    cliches: List[ClicheDetection] = Field(default_factory=list)
    
    # 이슈 목록
    issues: List[EvaluationIssue] = Field(default_factory=list)
    
    # 피드백
    summary: str
    suggestions: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    
    # 평가 모델 정보
    evaluator_model: Optional[str] = None
    evaluation_version: str = "1.0"


class EvaluationResult(BaseModel):
    """평가 결과 요약 (빠른 조회용)"""
    scene_id: int
    overall_score: float
    creativity_score: float
    cliche_detected: bool
    issue_count: int
    needs_revision: bool = Field(
        ..., 
        description="수정이 필요한지 여부 (overall_score < 0.6 또는 심각한 이슈 존재)"
    )
    summary: str
    
    @classmethod
    def from_evaluation(cls, eval: Evaluation) -> "EvaluationResult":
        """Evaluation에서 결과 요약 생성"""
        has_errors = any(
            issue.severity == SeverityLevel.ERROR 
            for issue in eval.issues
        )
        return cls(
            scene_id=eval.scene_id,
            overall_score=eval.overall_score,
            creativity_score=eval.creativity_score,
            cliche_detected=eval.cliche_detected,
            issue_count=len(eval.issues),
            needs_revision=eval.overall_score < 0.6 or has_errors,
            summary=eval.summary
        )


class EvaluationComparison(BaseModel):
    """버전 간 평가 비교"""
    scene_id: int
    version_1: int
    version_2: int
    score_diff: Dict[str, float]  # 카테고리별 점수 차이
    improvements: List[str]        # 개선된 점
    regressions: List[str]         # 나빠진 점
    recommendation: str            # 어떤 버전을 추천하는지

