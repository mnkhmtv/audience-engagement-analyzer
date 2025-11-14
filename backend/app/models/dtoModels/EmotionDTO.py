from typing import Dict
from pydantic import BaseModel


class EmotionResponseDTO(BaseModel):
    emotion: str
    scores: Dict[str, float]
