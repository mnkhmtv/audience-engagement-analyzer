from io import BytesIO
from enum import Enum
from typing import Dict, Tuple

from PIL import Image


class EmotionEnum(str, Enum):
    happy = "happy"
    neutral = "neutral"
    sad = "sad"


class EmotionService:
    async def analyze_image(self, data: bytes) -> Tuple[EmotionEnum, Dict[str, float]]:
        """
        Очень простая заглушка:
        - конвертируем в ч/б
        - считаем среднюю яркость
        - по порогам решаем, грубо: sad / neutral / happy
        """

        image = Image.open(BytesIO(data)).convert("L")  # grayscale
        pixels = list(image.getdata())
        avg = sum(pixels) / len(pixels)

        if avg > 170:
            emotion = EmotionEnum.happy
        elif avg < 80:
            emotion = EmotionEnum.sad
        else:
            emotion = EmotionEnum.neutral

        scores = {
            "happy": 1.0 if emotion == EmotionEnum.happy else 0.0,
            "sad": 1.0 if emotion == EmotionEnum.sad else 0.0,
            "neutral": 1.0 if emotion == EmotionEnum.neutral else 0.0,
        }

        return emotion, scores
