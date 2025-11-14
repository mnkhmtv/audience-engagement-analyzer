# app/infrastructure/repositories/UserRepository.py

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.dbModels.UserEntity import UserEntity, UserRoleEnum


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_email(self, email: str) -> Optional[UserEntity]:
        stmt = select(UserEntity).where(UserEntity.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id(self, user_id: UUID) -> Optional[dict]:
        stmt = select(UserEntity).where(UserEntity.id == user_id)
        result = await self.session.execute(stmt)
        obj = result.scalar_one_or_none()
        return obj.to_dict() if obj else None

    async def find_all(self) -> List[dict]:
        stmt = select(UserEntity)
        result = await self.session.execute(stmt)
        return [u.to_dict() for u in result.scalars().all()]

    async def add_user(self, entity: UserEntity) -> dict:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity.to_dict()

    async def set_role(self, user_id: UUID, role: UserRoleEnum) -> Optional[dict]:
        stmt = select(UserEntity).where(UserEntity.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            return None
        user.role = role
        await self.session.commit()
        await self.session.refresh(user)
        return user.to_dict()
