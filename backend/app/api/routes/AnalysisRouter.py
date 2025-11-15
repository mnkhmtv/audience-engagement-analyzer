from __future__ import annotations

import os
import shutil
import tempfile
from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.dtoModels.AnalysisDTO import AnalyzeVideoResponse
from app.services.VideoAnalysisService import VideoAnalysisService
from app.infrastructure.repositories.AnalysisResultRepository import AnalysisResultRepository
from app.infrastructure.db.session import fastapi_get_db

router = APIRouter(prefix="/analysis", tags=["analysis"])


def get_video_service() -> VideoAnalysisService:
    return VideoAnalysisService()


@router.post("/video", response_model=AnalyzeVideoResponse)
async def analyze_video(
    lecture_id: Annotated[UUID, Query(..., description="Lecture UUID to attach analysis to")],
    file: Annotated[UploadFile, File(...)],
    session: Annotated[AsyncSession, Depends(fastapi_get_db)],
    service: Annotated[VideoAnalysisService, Depends(get_video_service)],
    sample_sec: float = Query(settings.FRAME_SAMPLE_SEC, ge=0.1, le=10.0),
):
    """Анализ видео с детекцией лиц, эмоций и внимания"""
    analysis_repo = AnalysisResultRepository(session)
    
    # Save UploadFile to temp path for OpenCV
    with tempfile.TemporaryDirectory() as td:
        tmp_path = os.path.join(td, file.filename or "upload.mp4")
        with open(tmp_path, "wb") as out:
            shutil.copyfileobj(file.file, out)
        
        return await service.analyze_video(
            upload_tmp_path=tmp_path,
            lecture_id=lecture_id,
            sample_sec=sample_sec,
            session=session,
            analysis_repo=analysis_repo,
        )

