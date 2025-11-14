from __future__ import annotations

from typing import Sequence
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dbModels.LectureEntity import LectureEntity, LectureStatusEnum


class LectureRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        *,
        owner_id: UUID,
        title: str,
        subject: str | None,
        video_tmp_path: str | None,
    ) -> LectureEntity:
        lecture = LectureEntity(
            owner_id=owner_id,
            title=title,
            subject=subject,
            status=LectureStatusEnum.pending,
            progress=0,
            video_tmp_path=video_tmp_path,
        )
        self.session.add(lecture)
        await self.session.flush()  # чтобы получить lecture.id
        return lecture

    async def get_by_id(self, lecture_id: UUID) -> LectureEntity | None:
        stmt = select(LectureEntity).where(LectureEntity.id == lecture_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_owner(self, owner_id: UUID) -> Sequence[LectureEntity]:
        stmt = (
            select(LectureEntity)
            .where(LectureEntity.owner_id == owner_id)
            .order_by(LectureEntity.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_status(
        self,
        lecture_id: UUID,
        *,
        status: str,
        progress: int | None = None,
        error_message: str | None = None,
    ) -> None:
        values: dict = {"status": status}
        if progress is not None:
            values["progress"] = progress
        if error_message is not None:
            values["error_message"] = error_message

        stmt = (
            update(LectureEntity)
            .where(LectureEntity.id == lecture_id)
            .values(**values)
        )
        await self.session.execute(stmt)

    async def update_paths(
        self,
        lecture_id: UUID,
        *,
        video_tmp_path: str | None = None,
        thumbnail_path: str | None = None,
    ) -> None:
        values: dict = {}
        if video_tmp_path is not None:
            values["video_tmp_path"] = video_tmp_path
        if thumbnail_path is not None:
            values["thumbnail_path"] = thumbnail_path

        if not values:
            return

        stmt = (
            update(LectureEntity)
            .where(LectureEntity.id == lecture_id)
            .values(**values)
        )
        await self.session.execute(stmt)
