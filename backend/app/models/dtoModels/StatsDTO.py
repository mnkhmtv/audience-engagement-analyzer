# app/models/dtoModels/StatsDTO.py
from uuid import UUID
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from app.models.dtoModels.EntityDTO import Entity


class BestLectureDTO(Entity):
    lecture_id: UUID
    title: str
    score: float
    date: datetime


class MyStatsSummaryDTO(Entity):
    user_id: UUID
    lectures_count: int
    avg_engagement: Optional[float] = None
    avg_attention: Optional[float] = None
    avg_score: Optional[float] = None
    best_lecture: Optional[BestLectureDTO] = None


class ProfessorStatsItemDTO(Entity):
    user_id: UUID
    name: str
    lectures_count: int
    avg_engagement: Optional[float] = None
    avg_attention: Optional[float] = None
    avg_score: Optional[float] = None


class ProfessorLeaderboardDTO(BaseModel):
    items: List[ProfessorStatsItemDTO]
