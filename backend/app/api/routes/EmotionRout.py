from fastapi import APIRouter, UploadFile, File, Depends
from app.services.EmotionService import EmotionService
from app.models.dtoModels.EmotionDTO import EmotionResponseDTO


router = APIRouter(
    prefix="/emotion",
    tags=["emotion"],
)


def get_emotion_service() -> EmotionService:
    return EmotionService()


@router.post("/detect-image", response_model=EmotionResponseDTO)
async def detect_emotion_from_image(
    file: UploadFile = File(..., description="Image file"),
    emotion_service: EmotionService = Depends(get_emotion_service),
):
    """
    Analyze a single image for emotion using a simple heuristic.
    """
    data = await file.read()
    emotion, scores = await emotion_service.analyze_image(data)
    return EmotionResponseDTO(emotion=emotion, scores=scores)

