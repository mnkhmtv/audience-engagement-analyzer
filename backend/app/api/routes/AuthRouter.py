# app/api/routes/AuthRouter.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import fastapi_get_db
from app.models.dtoModels.UserDTO import UserCreateDTO, UserOutDTO
from app.services.UserService import add_user

router = APIRouter()

@router.post("/register", response_model=UserOutDTO, status_code=status.HTTP_201_CREATED)
async def register(dto: UserCreateDTO, session: AsyncSession = Depends(fastapi_get_db)):
    return await add_user(dto, session)
