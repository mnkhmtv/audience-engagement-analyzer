from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import fastapi_get_db as get_async_session
from app.services.VideoAnalysisService import VideoAnalysisService
from app.services.AuthorizationService import get_current_user_service
from app.models.dtoModels.LectureDTO import (
    LectureCreateResponseDTO,
    LectureShortDTO,
    LectureWithAnalysisDTO,
    AnalysisResultDTO,
)
from app.models.dtoModels.UserDTO import UserOutDTO
from app.infrastructure.repositories.LectureRepository import LectureRepository
from app.infrastructure.repositories.AnalysisResultRepository import AnalysisResultRepository

router = APIRouter(prefix="/lectures", tags=["lectures"])

def get_video_analysis_service() -> VideoAnalysisService:
    return VideoAnalysisService()

@router.post("/upload")
async def upload_lecture(
    title: Annotated[str, Form(...)],
    file: Annotated[UploadFile, File(...)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[UserOutDTO, Depends(get_current_user_service)],
    service: Annotated[VideoAnalysisService, Depends(get_video_analysis_service)],
    subject: Annotated[str, Form()] = None,
):
    # простая проверка типа файла
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Файл должен быть видео")

    lecture = await service.create_lecture_and_run_analysis(
        session=session,
        owner_id=current_user.id,
        title=title,
        subject=subject,
        upload_file=file,
    )

    if lecture is None:
        raise HTTPException(status_code=500, detail="Не удалось создать лекцию")

    return LectureCreateResponseDTO.model_validate(lecture)


@router.get("/", response_model=list[LectureShortDTO])
async def list_my_lectures(
    current_user: Annotated[UserOutDTO, Depends(get_current_user_service)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    repo = LectureRepository(session)
    lectures = await repo.list_by_owner(current_user.id)
    return [LectureShortDTO.model_validate(l) for l in lectures]


@router.get("/{lecture_id}", response_model=LectureWithAnalysisDTO)
async def get_lecture_detail(
    lecture_id: UUID,
    current_user: Annotated[UserOutDTO, Depends(get_current_user_service)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    lecture_repo = LectureRepository(session)
    analysis_repo = AnalysisResultRepository(session)

    lecture = await lecture_repo.get_by_id(lecture_id)
    if lecture is None or lecture.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Лекция не найдена")

    analysis = await analysis_repo.get_by_lecture_id(lecture_id)

    dto = LectureWithAnalysisDTO.model_validate(lecture)
    if analysis:
        dto.analysis = AnalysisResultDTO.model_validate(analysis)

    return dto


@router.get("/{lecture_id}/analysis", response_model=AnalysisResultDTO)
async def get_lecture_analysis(
    lecture_id: UUID,
    current_user: Annotated[UserOutDTO, Depends(get_current_user_service)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    lecture_repo = LectureRepository(session)
    analysis_repo = AnalysisResultRepository(session)

    lecture = await lecture_repo.get_by_id(lecture_id)
    if lecture is None or lecture.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Лекция не найдена")

    analysis = await analysis_repo.get_by_lecture_id(lecture_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Результат анализа пока не готов")

    return AnalysisResultDTO.model_validate(analysis)
