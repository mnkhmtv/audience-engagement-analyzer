import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    ForeignKey,
    DateTime,
    Enum,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.models.dbModels.Entity import EntityDB


class LectureStatusEnum(str):
    pending = "pending"
    processing = "processing"
    done = "done"
    error = "error"


class LectureEntity(EntityDB):
    __tablename__ = "lectures"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(200), nullable=False)
    subject = Column(String(100), nullable=True)

    status = Column(
        Enum(
            LectureStatusEnum.pending,
            LectureStatusEnum.processing,
            LectureStatusEnum.done,
            LectureStatusEnum.error,
            name="lecture_status_enum",
        ),
        nullable=False,
        default=LectureStatusEnum.pending,
    )

    progress = Column(Integer, nullable=False, default=0)

    video_tmp_path = Column(Text, nullable=True)
    thumbnail_path = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # связь 1:1 с результатом анализа
    analysis_result = relationship(
        "AnalysisResultEntity",
        uselist=False,
        back_populates="lecture",
        cascade="all, delete-orphan",
    )
