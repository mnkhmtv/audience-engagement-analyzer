# app/api/main.py
from fastapi import APIRouter

from app.api.routes import TokenRout
from app.api.routes import EmotionRout
from app.api.routes import HealthRouter
from app.api.routes import AuthRouter
from app.api.routes import LectureRout
from app.api.routes import AnalysisRouter


api_router = APIRouter()

# /api/health
api_router.include_router(HealthRouter.router, tags=["health"])

# /api/token/...
api_router.include_router(TokenRout.router, prefix="/token", tags=["token"])

# /api/auth/register
api_router.include_router(AuthRouter.router, prefix="/auth", tags=["auth"])

api_router.include_router(
    EmotionRout.router,
    tags=["Emotion"],
)

api_router.include_router(LectureRout.router)

# /api/analysis/...
api_router.include_router(AnalysisRouter.router)

