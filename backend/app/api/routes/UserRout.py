"""
from fastapi import APIRouter, Depends
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import fastapi_get_db as get_session
from app.services.UserService import UserService
from app.services.AuthorizationService import get_current_user
from app.models.dtoModels.UserDTO import UserOutDTO
from app.models.dbModels.entities.UserEntity import InterestEnum

router = APIRouter()


@router.get("/interests", response_model=list[InterestEnum])
async def get_interests(
    session: AsyncSession = Depends(get_session),
    current_user: UserOutDTO = Depends(get_current_user),
    user_service: UserService = Depends(UserService),
):
    return await user_service.get_user_interests(session, current_user.id)
"""