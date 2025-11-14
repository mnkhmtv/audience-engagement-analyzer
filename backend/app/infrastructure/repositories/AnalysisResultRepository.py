from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dbModels.AnalysisResultEntity import AnalysisResultEntity


class AnalysisResultRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        *,
        lecture_id: UUID,
        avg_engagement: float,
        avg_attention: float,
        score: float,
        metrics_path: str,
        summary_json: str | None,
    ) -> AnalysisResultEntity:
        entity = AnalysisResultEntity(
            lecture_id=lecture_id,
            avg_engagement=avg_engagement,
            avg_attention=avg_attention,
            score=score,
            metrics_path=metrics_path,
            summary_json=summary_json,
        )
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def get_by_lecture_id(self, lecture_id: UUID) -> AnalysisResultEntity | None:
        stmt = select(AnalysisResultEntity).where(AnalysisResultEntity.lecture_id == lecture_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
