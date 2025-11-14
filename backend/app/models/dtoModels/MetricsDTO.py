# app/models/dtoModels/MetricsDTO.py
from uuid import UUID
from typing import List
from pydantic import BaseModel


class MetricsPointDTO(BaseModel):
    timestamp_sec: float
    n_faces_total: int
    n_faces_analyzed: int
    engagement_ratio: float
    engagement_posprob_mean: float
    attention_ratio: float
    yaw_mean: float
    pitch_mean: float
    roll_mean: float


class MetricsTimeSeriesDTO(BaseModel):
    lecture_id: UUID
    points: List[MetricsPointDTO]
