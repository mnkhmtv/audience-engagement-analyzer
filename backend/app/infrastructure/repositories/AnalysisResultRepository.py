from __future__ import annotations

from typing import Sequence
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

    async def list_by_lecture_ids(
        self, lecture_ids: Sequence[UUID]
    ) -> dict[UUID, AnalysisResultEntity]:
        if not lecture_ids:
            return {}

        stmt = select(AnalysisResultEntity).where(
            AnalysisResultEntity.lecture_id.in_(lecture_ids)
        )
        result = await self.session.execute(stmt)
        analyses = result.scalars().all()
        return {analysis.lecture_id: analysis for analysis in analyses}
