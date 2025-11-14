from app.models.dbModels.Entity import EntityDB
from sqlalchemy import Column, String, UUID, Text, Boolean, DateTime
from datetime import datetime, timezone
import uuid

class RefreshTokensEntity(EntityDB):
    __tablename__ = 'refresh_tokens'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid.uuid4,
    )
    user_id = Column(UUID(as_uuid=True),
        primary_key=True,
        nullable=False,)
    token = Column(Text, nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    user_agent = Column(String, nullable=True)
    ip = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "token": self.token,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_revoked": self.is_revoked,
            "user_agent": self.user_agent,
            "ip": self.ip,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
