from __future__ import annotations

from pathlib import Path
import os
from pydantic import BaseModel


DEFAULT_EMOTION_MODEL_PATH = "app/ml_models/emotion_minix.pt"


class Settings(BaseModel):
    # Path to emotion Torch checkpoint. You can override via ENV.
    EMOTION_MODEL_PATH: str = DEFAULT_EMOTION_MODEL_PATH

    # Frame sampling period in seconds (N seconds between processed frames)
    FRAME_SAMPLE_SEC: float = 1.0

    # Attention thresholds (degrees)
    ATTENTION_YAW_OK: float = 30.0  # |yaw| <= this -> attentive
    ATTENTION_PITCH_OK: float = 20.0  # |pitch| <= this -> attentive

    # Weights for engagement score
    WEIGHT_ATTENTION: float = 0.6
    WEIGHT_AFFECT: float = 0.4

    # Where to save metrics JSON files
    METRICS_DIR: str = "data/metrics"

    pass


def _load() -> Settings:
    return Settings(
        EMOTION_MODEL_PATH=os.getenv("APP_EMOTION_MODEL_PATH", DEFAULT_EMOTION_MODEL_PATH),
        FRAME_SAMPLE_SEC=float(os.getenv("APP_FRAME_SAMPLE_SEC", 1.0)),
        ATTENTION_YAW_OK=float(os.getenv("APP_ATTENTION_YAW_OK", 30.0)),
        ATTENTION_PITCH_OK=float(os.getenv("APP_ATTENTION_PITCH_OK", 20.0)),
        WEIGHT_ATTENTION=float(os.getenv("APP_WEIGHT_ATTENTION", 0.6)),
        WEIGHT_AFFECT=float(os.getenv("APP_WEIGHT_AFFECT", 0.4)),
        METRICS_DIR=os.getenv("APP_METRICS_DIR", "data/metrics"),
    )


settings = _load()

# ensure metrics dir exists at import time
Path(settings.METRICS_DIR).mkdir(parents=True, exist_ok=True)
