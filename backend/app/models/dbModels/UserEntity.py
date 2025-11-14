# app/models/dbModels/UserEntity.py
from uuid import uuid4
from sqlalchemy import Column, String, Enum as SAEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from datetime import datetime, timezone
from enum import Enum

from app.models.dbModels.Entity import EntityDB


class UserRoleEnum(str, Enum):
    PROFESSOR = "professor"
    ADMIN = "admin"


class UserEntity(EntityDB):
    __tablename__ = "users"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String(200), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)

    role = Column(
        SAEnum(
            UserRoleEnum,
            name="user_role_enum",
            values_callable=lambda e: [v.value for v in e],
        ),
        nullable=False,
        default=UserRoleEnum.PROFESSOR.value,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role.value if isinstance(self.role, UserRoleEnum) else self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
