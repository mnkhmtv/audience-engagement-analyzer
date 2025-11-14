# app/infrastructure/repositories/RefreshTokenRepository.py

from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update

from app.models.dbModels.RefreshTokenRepository import RefreshTokensEntity


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_token(
        self,
        token: str,
        user_id: UUID,
        expires_in_minutes: int,
        user_agent: Optional[str] = None,
        ip: Optional[str] = None
    ) -> dict:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        entity = RefreshTokensEntity(
            id=uuid4(),
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            user_agent=user_agent,
            ip=ip,
        )
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity.to_dict()

    async def get_token(self, token: str) -> Optional[RefreshTokensEntity]:
        stmt = select(RefreshTokensEntity).where(RefreshTokensEntity.token == token)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_token(self, token_id: UUID) -> None:
        stmt = (
            update(RefreshTokensEntity)
            .where(RefreshTokensEntity.id == token_id)
            .values(is_revoked=True)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_token(
        self,
        token_id: UUID,
        new_token: str,
        expires_in_minutes: int,
        user_agent: Optional[str] = None,
        ip: Optional[str] = None,
    ) -> dict:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        stmt = (
            update(RefreshTokensEntity)
            .where(RefreshTokensEntity.id == token_id)
            .values(
                token=new_token,
                expires_at=expires_at,
                is_revoked=False,
                user_agent=user_agent,
                ip=ip,
            )
            .returning(RefreshTokensEntity)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        updated = result.fetchone()[0]
        await self.session.refresh(updated)
        return updated.to_dict()

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        stmt = (
            update(RefreshTokensEntity)
            .where(RefreshTokensEntity.user_id == user_id)
            .values(is_revoked=True)
        )
        await self.session.execute(stmt)
        await self.session.commit()
