# app/services/UserService.py
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.UserRepository import UserRepository
from app.models.dbModels.UserEntity import UserEntity, UserRoleEnum
from app.models.dtoModels.UserDTO import UserCreateDTO, UserOutDTO
from app.services.AuthorizationService import AuthService


async def add_user(dto: UserCreateDTO, session: AsyncSession) -> UserOutDTO:
    """
    Регистрация нового пользователя (препода/админа).
    """
    repo = UserRepository(session)

    # Проверяем, нет ли уже пользователя с таким email
    if await repo.find_by_email(str(dto.email)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with given email already exists",
        )

    hashed_pw = AuthService().get_password_hash(dto.password)

    # Создаём сущность пользователя
    entity = UserEntity(
        id=uuid4(),
        first_name=dto.first_name,
        last_name=dto.last_name,
        email=str(dto.email),
        hashed_password=hashed_pw,
        role=dto.role or UserRoleEnum.PROFESSOR,
    )

    saved = await repo.add_user(entity)
    # repo.add_user возвращает entity.to_dict(); Pydantic спокойно это переварит
    return UserOutDTO(**saved)
