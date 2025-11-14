from __future__ import annotations

import json
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from uuid import UUID

import cv2
import numpy as np
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.infrastructure.core import settings as core_settings
from app.infrastructure.repositories.LectureRepository import LectureRepository
from app.infrastructure.repositories.AnalysisResultRepository import AnalysisResultRepository
from app.models.dbModels.LectureEntity import LectureStatusEnum
from app.services.emotion_classifier import EmotionClassifier
from app.services.attention_estimator import AttentionEstimator
from app.models.dtoModels.AnalysisDTO import (
    FaceMetrics,
    FaceEmotion,
    FrameMetrics,
    AnalysisSummary,
    AnalyzeVideoResponse,
    TimelineHighlight,
)


POSITIVE_EMOTIONS = {"happy", "surprise"}


class VideoAnalysisService:
    """
    Сервис полного цикла обработки видео-лекции с детекцией лиц, эмоций и внимания:
    - сохранение исходного видео
    - выбор кадров
    - детекция лиц и оценка внимания (head pose)
    - классификация эмоций через ONNX модель
    - агрегация метрик
    - сохранение AnalysisResult + обновление Lecture
    """

    def __init__(self, emotion_service=None) -> None:
        # Инициализируем классификатор эмоций
        model_path = Path(settings.EMOTION_MODEL_PATH)
        if not model_path.is_absolute():
            # Относительный путь от корня проекта
            base_dir = Path(__file__).resolve().parents[2]
            model_path = base_dir / model_path
        self._emotion_classifier = EmotionClassifier(str(model_path))
        
        # Инициализируем оценщик внимания
        self._attention_estimator = AttentionEstimator(
            yaw_ok=settings.ATTENTION_YAW_OK,
            pitch_ok=settings.ATTENTION_PITCH_OK,
        )
        
        # базовая папка для артефактов (напр. смонтированная volume)
        self._artifacts_dir = Path(getattr(core_settings, "ARTIFACTS_DIR", "artifacts")).absolute()
        self._videos_dir = self._artifacts_dir / "videos"
        self._metrics_dir = Path(settings.METRICS_DIR).absolute()

        self._videos_dir.mkdir(parents=True, exist_ok=True)
        self._metrics_dir.mkdir(parents=True, exist_ok=True)

    # ========== Публичные методы ==========

    async def create_lecture_and_run_analysis(
        self,
        *,
        session: AsyncSession,
        owner_id: UUID,
        title: str,
        subject: str | None,
        upload_file: UploadFile,
    ):
        """
        1) Сохраняем видео во временную папку
        2) Создаём Lecture
        3) Запускаем анализ
        """
        lecture_repo = LectureRepository(session)

        # 1. Сохраняем видео
        video_path = await self._save_uploaded_video(upload_file)

        # 2. Создаём лекцию в статусе pending
        lecture = await lecture_repo.create(
            owner_id=owner_id,
            title=title,
            subject=subject,
            video_tmp_path=str(video_path),
        )

        # 3. Обновляем статус -> processing
        await lecture_repo.update_status(
            lecture_id=lecture.id,
            status=LectureStatusEnum.processing,
            progress=0,
        )
        await session.commit()

        # 4. Запускаем анализ
        try:
            analysis_repo = AnalysisResultRepository(session)
            await self._run_full_analysis(
                session=session,
                lecture_id=lecture.id,
                video_path=video_path,
                lecture_repo=lecture_repo,
                analysis_repo=analysis_repo,
            )
        except Exception as e:
            # В случае ошибки — помечаем лекцию как error
            await lecture_repo.update_status(
                lecture_id=lecture.id,
                status=LectureStatusEnum.error,
                progress=0,
                error_message=str(e),
            )
            await session.commit()
            raise

        # заново получаем лекцию с обновлённым статусом
        return await lecture_repo.get_by_id(lecture.id)

    async def analyze_video(
        self,
        *,
        upload_tmp_path: str,
        lecture_id: UUID,
        sample_sec: float,
        session: AsyncSession,
        analysis_repo: AnalysisResultRepository,
    ) -> AnalyzeVideoResponse:
        """Новый метод для анализа видео с полным пайплайном"""
        # Run CPU-heavy work off the event loop
        (
            frames,
            avg_att,
            avg_eng,
            score,
            emotion_hist,
            top_peaks,
            top_dips,
            suggestions,
        ) = await asyncio.to_thread(self._analyze_sync, upload_tmp_path, sample_sec)

        summary = AnalysisSummary(
            lecture_id=lecture_id,
            frames_analyzed=len(frames),
            faces_total=sum(f.face_count for f in frames),
            avg_attention=avg_att,
            avg_engagement=avg_eng,
            score=score,
            emotion_hist=emotion_hist,
            top_peaks=top_peaks,
            top_dips=top_dips,
            suggestions=suggestions,
        )

        # Persist metrics JSON
        stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        out_name = f"{lecture_id}_{stamp}.json"
        out_path = str(self._metrics_dir / out_name)

        metrics_payload = {
            "lecture_id": str(lecture_id),
            "sample_sec": sample_sec,
            "frames": [f.model_dump() for f in frames],
            "highlights": {
                "peaks": [h.model_dump() for h in top_peaks],
                "dips": [h.model_dump() for h in top_dips],
            },
            "suggestions": suggestions,
            "summary": summary.model_dump(mode="json"),
        }

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(metrics_payload, f, ensure_ascii=False, indent=2)

        # Save to DB
        entity = await analysis_repo.create(
            lecture_id=lecture_id,
            avg_engagement=avg_eng,
            avg_attention=avg_att,
            score=score,
            metrics_path=out_path,
            summary_json=summary.model_dump_json(),
        )

        await session.commit()

        from app.models.dtoModels.AnalysisDTO import AnalysisResultOut
        db_record = AnalysisResultOut.model_validate(entity)

        return AnalyzeVideoResponse(
            summary=summary,
            metrics_path=out_path,
            db_record=db_record,
            frames=frames,
        )

    # ========== Внутренние методы ==========

    async def _save_uploaded_video(self, upload_file: UploadFile) -> Path:
        """Сохраняет загруженное видео в файловую систему."""
        suffix = Path(upload_file.filename or "video.mp4").suffix or ".mp4"
        fname = f"{uuid.uuid4()}{suffix}"
        out_path = self._videos_dir / fname

        # читаем всё содержимое файла
        data = await upload_file.read()
        with out_path.open("wb") as f:
            f.write(data)

        return out_path

    def _analyze_sync(
        self, video_path: str, sample_sec: float
    ) -> tuple[
        list[FrameMetrics],
        float,
        float,
        float,
        dict[str, float],
        list[TimelineHighlight],
        list[TimelineHighlight],
        list[str],
    ]:
        """
        Синхронный метод анализа видео (выполняется в отдельном потоке).
        Возвращает: (frames, avg_attention, avg_engagement, score, emotion_hist)
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Не удалось открыть видео: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        frame_step = max(int(fps * sample_sec), 1)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        frames: list[FrameMetrics] = []
        frame_idx = 0
        emotion_sum: dict[str, float] = {}

        while True:
            ret, frame_bgr = cap.read()
            if not ret:
                break

            if frame_idx % frame_step == 0:
                ts_sec = frame_idx / fps

                # 1. Детекция лиц и оценка внимания
                face_data = self._attention_estimator.estimate(frame_bgr)
                frame_faces: list[FaceMetrics] = []

                for fd in face_data:
                    bbox = fd["bbox"]
                    x, y, w, h = bbox

                    # Извлекаем лицо
                    face_roi = frame_bgr[y : y + h, x : x + w]
                    if face_roi.size == 0:
                        continue

                    # 2. Классификация эмоций
                    try:
                        top_emotion, top_prob, emotion_dist = self._emotion_classifier.predict(face_roi)
                        affect = self._emotion_classifier.affect_from_distribution(emotion_dist)
                    except Exception:
                        # Если не удалось классифицировать, используем нейтральные значения
                        top_emotion, top_prob = "neutral", 0.0
                        emotion_dist = {"neutral": 1.0}
                        affect = 0.5

                    # 3. Вычисляем engagement
                    attention = fd["attention"]
                    engagement = (
                        settings.WEIGHT_ATTENTION * attention + settings.WEIGHT_AFFECT * affect
                    )

                    # Собираем метрики лица
                    face_metrics = FaceMetrics(
                        bbox=bbox,
                        yaw_deg=fd["yaw"],
                        pitch_deg=fd["pitch"],
                        roll_deg=fd["roll"],
                        attention=attention,
                        affect=affect,
                        engagement=engagement,
                        top_emotion=FaceEmotion(label=top_emotion, prob=top_prob),
                        emotions=emotion_dist,
                        looking_target=fd["looking_target"],
                    )

                    frame_faces.append(face_metrics)

                    # Суммируем эмоции
                    for emo, prob in emotion_dist.items():
                        emotion_sum[emo] = emotion_sum.get(emo, 0.0) + prob

                face_count = len(frame_faces)
                positive_faces = sum(
                    1
                    for frm_face in frame_faces
                    if frm_face.top_emotion and frm_face.top_emotion.label in POSITIVE_EMOTIONS
                )
                attention_ratio = (
                    float(np.mean([frm_face.attention for frm_face in frame_faces])) if face_count else 0.0
                )
                engagement_ratio = float(positive_faces / face_count) if face_count else 0.0

                frames.append(
                    FrameMetrics(
                        ts_sec=ts_sec,
                        faces=frame_faces,
                        engagement_ratio=engagement_ratio,
                        attention_ratio=attention_ratio,
                        positive_faces=positive_faces,
                        face_count=face_count,
                    )
                )

            frame_idx += 1

        cap.release()

        if not frames:
            raise ValueError("Не удалось обработать ни одного кадра")

        # Агрегация
        meaningful_frames = [frame for frame in frames if frame.face_count > 0]

        if meaningful_frames:
            avg_att = float(np.mean([frame.attention_ratio for frame in meaningful_frames]))
            avg_eng = float(np.mean([frame.engagement_ratio for frame in meaningful_frames]))
        else:
            avg_att = 0.0
            avg_eng = 0.0

        total = sum(emotion_sum.values()) or 1.0
        emotion_hist = {k: float(v / total) for k, v in sorted(emotion_sum.items())}

        score = float(0.7 * avg_eng + 0.3 * avg_att)

        top_peaks, top_dips = self._build_highlights(frames, sample_sec)
        suggestions = self._generate_suggestions(avg_eng, avg_att, top_peaks, top_dips)

        return frames, avg_att, avg_eng, score, emotion_hist, top_peaks, top_dips, suggestions

    def _build_highlights(
        self,
        frames: list[FrameMetrics],
        sample_sec: float,
        limit: int = 3,
    ) -> tuple[list[TimelineHighlight], list[TimelineHighlight]]:
        """Find peak and dip moments for timeline summaries."""
        meaningful = [frame for frame in frames if frame.face_count > 0]
        if not meaningful:
            return [], []

        window = max(sample_sec * 3.0, 2.0)

        def pick(sorted_frames: list[FrameMetrics]) -> list[FrameMetrics]:
            selected: list[FrameMetrics] = []
            for frame in sorted_frames:
                if all(abs(frame.ts_sec - prev.ts_sec) >= window for prev in selected):
                    selected.append(frame)
                if len(selected) >= limit:
                    break
            return selected

        sorted_peaks = sorted(meaningful, key=lambda frame: frame.engagement_ratio, reverse=True)
        sorted_dips = sorted(meaningful, key=lambda frame: frame.engagement_ratio)

        peaks = [self._frame_to_highlight(frame, window, "Peak engagement") for frame in pick(sorted_peaks)]
        dips = [self._frame_to_highlight(frame, window, "Engagement dip") for frame in pick(sorted_dips)]
        return peaks, dips

    def _frame_to_highlight(
        self,
        frame: FrameMetrics,
        window: float,
        label_prefix: str,
    ) -> TimelineHighlight:
        half = window / 2
        return TimelineHighlight(
            ts_sec=frame.ts_sec,
            window_start_sec=max(frame.ts_sec - half, 0.0),
            window_end_sec=frame.ts_sec + half,
            engagement_ratio=frame.engagement_ratio,
            attention_ratio=frame.attention_ratio,
            label=f"{label_prefix} @ {self._format_timestamp(frame.ts_sec)}",
        )

    def _generate_suggestions(
        self,
        avg_engagement: float,
        avg_attention: float,
        peaks: list[TimelineHighlight],
        dips: list[TimelineHighlight],
    ) -> list[str]:
        suggestions: list[str] = []

        if peaks:
            top = peaks[0]
            suggestions.append(
                f"High engagement ({top.engagement_ratio:.0%}) near {self._format_timestamp(top.ts_sec)} - reuse the activity or storytelling there."
            )
        if dips:
            low = dips[0]
            suggestions.append(
                f"Engagement dipped to {low.engagement_ratio:.0%} near {self._format_timestamp(low.ts_sec)} - insert a poll, question, or visual aid."
            )
        if avg_attention < 0.5:
            suggestions.append(
                "Average attention stayed below 50% - slow the pace, make eye contact, or ask the audience to reflect."
            )
        if avg_engagement < 0.4:
            suggestions.append(
                "Overall engagement is low - interleave stories or interactive questions every few minutes."
            )
        if not suggestions:
            suggestions.append("Engagement stayed steady; keep the same pacing and interactive elements.")

        return suggestions

    @staticmethod
    def _format_timestamp(ts_sec: float) -> str:
        minutes = int(ts_sec // 60)
        seconds = int(ts_sec % 60)
        return f"{minutes}:{seconds:02d}"

    async def _run_full_analysis(
        self,
        *,
        session: AsyncSession,
        lecture_id: UUID,
        video_path: Path,
        lecture_repo: LectureRepository,
        analysis_repo: AnalysisResultRepository,
    ) -> None:
        """
        Полный пайплайн анализа видео (используется в create_lecture_and_run_analysis).
        """
        # Запускаем анализ в отдельном потоке
        (
            frames,
            avg_att,
            avg_eng,
            score,
            emotion_hist,
            top_peaks,
            top_dips,
            suggestions,
        ) = await asyncio.to_thread(self._analyze_sync, str(video_path), settings.FRAME_SAMPLE_SEC)

        total_frames = len(frames)

        # Обновляем прогресс
        for idx, _ in enumerate(frames):
            progress = int((idx + 1) / total_frames * 100)
            await lecture_repo.update_status(
                lecture_id=lecture_id,
                status=LectureStatusEnum.processing,
                progress=progress,
            )
            await session.commit()
        # ���?�:�?���?�?��? metrics.json
        stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        out_name = f"{lecture_id}_{stamp}.json"
        metrics_path = self._metrics_dir / out_name

        summary = AnalysisSummary(
            lecture_id=lecture_id,
            frames_analyzed=len(frames),
            faces_total=sum(f.face_count for f in frames),
            avg_attention=avg_att,
            avg_engagement=avg_eng,
            score=score,
            emotion_hist=emotion_hist,
            top_peaks=top_peaks,
            top_dips=top_dips,
            suggestions=suggestions,
        )

        metrics_payload = {
            "lecture_id": str(lecture_id),
            "sample_sec": settings.FRAME_SAMPLE_SEC,
            "frames": [f.model_dump() for f in frames],
            "highlights": {
                "peaks": [h.model_dump() for h in top_peaks],
                "dips": [h.model_dump() for h in top_dips],
            },
            "suggestions": suggestions,
            "summary": summary.model_dump(mode="json"),
        }

        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(metrics_payload, f, ensure_ascii=False, indent=2)


        # Сохраняем AnalysisResult
        await analysis_repo.create(
            lecture_id=lecture_id,
            avg_engagement=avg_eng,
            avg_attention=avg_att,
            score=score,
            metrics_path=str(metrics_path),
            summary_json=summary.model_dump_json(),
        )

        # Обновляем лекцию -> done
        await lecture_repo.update_status(
            lecture_id=lecture_id,
            status=LectureStatusEnum.done,
            progress=100,
            error_message=None,
        )

        await session.commit()

