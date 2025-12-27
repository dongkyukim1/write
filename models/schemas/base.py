"""
기본 스키마 클래스
모든 스키마가 상속받는 공통 설정을 정의합니다.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    """기본 스키마 클래스"""
    
    class Config:
        # ORM 모드 활성화 (SQLAlchemy 모델과 호환)
        from_attributes = True
        # JSON 인코딩 시 datetime을 ISO 형식으로
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TimestampMixin(BaseModel):
    """타임스탬프 믹스인"""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class IDMixin(BaseModel):
    """ID 믹스인"""
    id: Optional[int] = None

