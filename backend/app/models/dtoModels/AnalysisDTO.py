from __future__ import annotations

from typing import List, Dict
from uuid import UUID
from pydantic import BaseModel, Field
from pydantic import ConfigDict


class FaceEmotion(BaseModel):
    label: str
    prob: float


class FaceMetrics(BaseModel):
    bbox: tuple[int, int, int, int] | None = None  # x, y, w, h in pixels
    yaw_deg: float | None = None
    pitch_deg: float | None = None
    roll_deg: float | None = None
    attention: float = 0.0  # [0, 1]
    affect: float = 0.0  # [0, 1] (mapped from emotions)
    engagement: float = 0.0  # [0, 1]
    top_emotion: FaceEmotion | None = None
    emotions: Dict[str, float] = Field(default_factory=dict)
    looking_target: str | None = None  # "screen/left/right/up/down"


class FrameMetrics(BaseModel):
    ts_sec: float
    faces: List[FaceMetrics]
    engagement_ratio: float = 0.0  # share of positive emotions
    attention_ratio: float = 0.0  # mean attention across faces
    positive_faces: int = 0
    face_count: int = 0


class TimelineHighlight(BaseModel):
    ts_sec: float
    window_start_sec: float
    window_end_sec: float
    engagement_ratio: float
    attention_ratio: float
    label: str


class AnalysisSummary(BaseModel):
    lecture_id: UUID
    frames_analyzed: int
    faces_total: int
    avg_attention: float
    avg_engagement: float
    score: float
    emotion_hist: Dict[str, float] = Field(default_factory=dict)  # normalized distribution
    top_peaks: List[TimelineHighlight] = Field(default_factory=list)
    top_dips: List[TimelineHighlight] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class AnalysisResultOut(BaseModel):
    id: UUID
    lecture_id: UUID
    avg_engagement: float
    avg_attention: float
    score: float
    metrics_path: str
    summary_json: str | None
    model_config = ConfigDict(from_attributes=True)


class AnalyzeVideoResponse(BaseModel):
    summary: AnalysisSummary
    metrics_path: str
    db_record: AnalysisResultOut
    frames: List[FrameMetrics]
    model_config = ConfigDict(from_attributes=True)

