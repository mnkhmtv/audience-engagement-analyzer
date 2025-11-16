from typing import Annotated, Optional
from uuid import UUID
from pathlib import Path

from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
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


def _build_video_url(lecture_id: UUID) -> str:
    return f"/lectures/{lecture_id}/video"

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

    dto = LectureCreateResponseDTO.model_validate(lecture)
    if lecture.video_tmp_path:
        dto.video_url = _build_video_url(lecture.id)
    return dto


@router.get("/", response_model=list[LectureShortDTO])
async def list_my_lectures(
    current_user: Annotated[UserOutDTO, Depends(get_current_user_service)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    repo = LectureRepository(session)
    analysis_repo = AnalysisResultRepository(session)
    lectures = await repo.list_by_owner(current_user.id)
    analysis_map = await analysis_repo.list_by_lecture_ids([lecture.id for lecture in lectures])
    result: list[LectureShortDTO] = []
    for lecture in lectures:
        dto = LectureShortDTO.model_validate(lecture)
        if lecture.video_tmp_path:
            dto.video_url = _build_video_url(lecture.id)
        analysis = analysis_map.get(lecture.id)
        if analysis:
            dto.analysis = AnalysisResultDTO.model_validate(analysis)
        result.append(dto)
    return result


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
    if lecture.video_tmp_path:
        dto.video_url = _build_video_url(lecture.id)
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


@router.get("/{lecture_id}/video")
async def get_lecture_video(
    lecture_id: UUID,
    current_user: Annotated[UserOutDTO, Depends(get_current_user_service)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    lecture_repo = LectureRepository(session)
    lecture = await lecture_repo.get_by_id(lecture_id)
    if lecture is None or lecture.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="�>���Ő�? �?�� �?�����?��?��")

    if not lecture.video_tmp_path:
        raise HTTPException(status_code=404, detail="Video file not found")

    video_path = Path(lecture.video_tmp_path)
    if not video_path.is_absolute():
        base_dir = Path(__file__).resolve().parents[3]
        video_path = (base_dir / video_path).resolve()

    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file missing on server")

    return FileResponse(video_path, media_type="video/mp4", filename=video_path.name)
