from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic import ConfigDict


class LectureCreateResponseDTO(BaseModel):
    id: UUID
    title: str
    subject: str | None = None
    status: str
    progress: int
    created_at: datetime
    video_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AnalysisResultDTO(BaseModel):
    lecture_id: UUID
    avg_engagement: float = Field(..., ge=0.0, le=1.0)
    avg_attention: float = Field(..., ge=0.0, le=1.0)
    score: float = Field(..., ge=0.0, le=1.0)
    metrics_path: str
    summary_json: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LectureShortDTO(BaseModel):
    id: UUID
    title: str
    subject: str | None = None
    status: str
    progress: int
    created_at: datetime
    video_url: str | None = None
    analysis: AnalysisResultDTO | None = None

    model_config = ConfigDict(from_attributes=True)


class LectureDetailDTO(LectureShortDTO):
    video_tmp_path: str | None = None
    thumbnail_path: str | None = None
    error_message: str | None = None


class LectureWithAnalysisDTO(LectureDetailDTO):
    pass
