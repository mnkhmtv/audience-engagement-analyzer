# app/models/dtoModels/UserDTO.py
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from pydantic import ConfigDict
from enum import Enum


class UserRoleEnum(str, Enum):
    PROFESSOR = "professor"
    ADMIN = "admin"


class UserCreateDTO(BaseModel):
    """
    Request body for user registration
    """
    first_name: str = Field(..., max_length=50, example="Alice")
    last_name: str = Field(..., max_length=50, example="Smith")
    email: EmailStr = Field(..., example="alice@example.com")
    password: str = Field(..., min_length=6, example="hunter2")
    role: UserRoleEnum = Field(default=UserRoleEnum.PROFESSOR, example="professor")


class UserOutDTO(BaseModel):
    """
    Response model for user data
    """
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    role: UserRoleEnum
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
