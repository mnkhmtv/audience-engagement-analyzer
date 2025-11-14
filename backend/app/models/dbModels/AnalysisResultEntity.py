import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    Float,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.models.dbModels.Entity import EntityDB


class AnalysisResultEntity(EntityDB):
    __tablename__ = "analysis_results"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lecture_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("lectures.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    avg_engagement = Column(Float, nullable=False)
    avg_attention = Column(Float, nullable=False)
    score = Column(Float, nullable=False)

    metrics_path = Column(Text, nullable=False)
    summary_json = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    lecture = relationship("LectureEntity", back_populates="analysis_result")

    __table_args__ = (
        UniqueConstraint("lecture_id", name="uix_analysis_lecture_id"),
    )
