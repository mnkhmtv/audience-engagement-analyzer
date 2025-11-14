from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.infrastructure.db.session import fastapi_get_db
from app.services.AuthorizationService import AuthService, get_current_user_service
from app.models.dtoModels.TokenDTO import TokenDTO
from app.models.dtoModels.RefreshTokenDTO import RefreshTokenDTO
from app.models.dtoModels.UserDTO import UserOutDTO

router = APIRouter()


@router.post("/get-token", response_model=TokenDTO)
async def login_for_access_token(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(fastapi_get_db),
    auth: AuthService = Depends(),
):
    return await auth.login_for_access_token(form_data, request, session)


@router.post("/refresh", response_model=TokenDTO)
async def refresh_access_token(
    request: Request,
    dto: RefreshTokenDTO,
    session: AsyncSession = Depends(fastapi_get_db),
    auth: AuthService = Depends(),
):
    return await auth.refresh_access_token(dto, request, session)


@router.get("/current-user", response_model=UserOutDTO)
async def read_users_me(
    current_user: Annotated[UserOutDTO, Depends(get_current_user_service)]
):
    return current_user