from __future__ import annotations

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Tuple


class SeparableConv2d(nn.Module):
    def __init__(self, in_ch: int, out_ch: int, k: int = 3, s: int = 1, p: int = 1) -> None:
        super().__init__()
        self.depthwise = nn.Conv2d(in_ch, in_ch, k, s, p, groups=in_ch, bias=False)
        self.pointwise = nn.Conv2d(in_ch, out_ch, 1, 1, 0, bias=False)
        self.bn = nn.BatchNorm2d(out_ch)

    def forward(self, x: torch.Tensor) -> torch.Tensor:  # pragma: no cover - trivial
        x = self.depthwise(x)
        x = self.pointwise(x)
        x = self.bn(x)
        return F.relu(x, inplace=True)


class MiniXBlock(nn.Module):
    def __init__(self, in_ch: int, out_ch: int) -> None:
        super().__init__()
        self.sep1 = SeparableConv2d(in_ch, out_ch)
        self.sep2 = SeparableConv2d(out_ch, out_ch)
        self.pool = nn.MaxPool2d(3, stride=2, padding=1)
        self.skip = nn.Conv2d(in_ch, out_ch, 1, stride=2, bias=False)
        self.bn = nn.BatchNorm2d(out_ch)

    def forward(self, x: torch.Tensor) -> torch.Tensor:  # pragma: no cover - trivial
        y = self.sep1(x)
        y = self.sep2(y)
        y = self.pool(y)
        s = self.bn(self.skip(x))
        return F.relu(y + s, inplace=True)


class MiniXEmotion(nn.Module):
    def __init__(self, n_classes: int, in_ch: int = 1) -> None:
        super().__init__()
        self.entry = nn.Sequential(
            nn.Conv2d(in_ch, 8, 3, padding=1, bias=False),
            nn.BatchNorm2d(8),
            nn.ReLU(inplace=True),
        )
        self.blocks = nn.Sequential(
            MiniXBlock(8, 16),
            MiniXBlock(16, 32),
            MiniXBlock(32, 64),
            MiniXBlock(64, 128),
        )
        self.head = nn.Sequential(
            nn.Conv2d(128, 128, 3, padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
        )
        self.fc = nn.Linear(128, n_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:  # pragma: no cover - trivial
        x = self.entry(x)
        x = self.blocks(x)
        x = self.head(x)
        x = torch.flatten(x, 1)
        return self.fc(x)


class EmotionClassifier:
    """Torch-based classifier used for emotion estimation."""

    def __init__(self, model_path: str) -> None:
        ckpt_path = Path(model_path)
        checkpoint = torch.load(ckpt_path, map_location="cpu")
        self.class_names = checkpoint.get("classes") or ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
        self.img_size = int(checkpoint.get("img_size", 96))
        state_dict = checkpoint.get("model") or checkpoint
        state_dict = self._remap_legacy_keys(state_dict)

        self.model = MiniXEmotion(n_classes=len(self.class_names), in_ch=1)
        self.model.load_state_dict(state_dict)
        self.model.eval()
        self.device = torch.device("cpu")
        self.model.to(self.device)

    def _preprocess(self, face_bgr: np.ndarray) -> torch.Tensor:
        gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (self.img_size, self.img_size), interpolation=cv2.INTER_AREA)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        normalized = clahe.apply(resized)
        tensor = torch.from_numpy(normalized).float().unsqueeze(0).unsqueeze(0) / 255.0
        tensor = (tensor - 0.5) / 0.5
        return tensor.to(self.device)

    @torch.inference_mode()
    def predict(self, face_bgr: np.ndarray) -> Tuple[str, float, Dict[str, float]]:
        inp = self._preprocess(face_bgr)
        logits = self.model(inp)
        probs = torch.softmax(logits, dim=1).cpu().numpy().flatten()
        top_idx = int(probs.argmax())
        distributions = {label: float(probs[i]) for i, label in enumerate(self.class_names)}
        return self.class_names[top_idx], float(probs[top_idx]), distributions

    @staticmethod
    def affect_from_distribution(dist: Dict[str, float]) -> float:
        pos = dist.get("happy", 0.0) + 0.5 * dist.get("surprise", 0.0)
        neg = dist.get("angry", 0.0) + dist.get("disgust", 0.0) + dist.get("fear", 0.0) + dist.get("sad", 0.0)
        neu = dist.get("neutral", 0.0) * 0.5
        score = pos * 0.8 + (1 - min(1.0, neg + neu)) * 0.2
        return max(0.0, min(1.0, score))

    @staticmethod
    def _remap_legacy_keys(state_dict: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        """Adapt checkpoints trained before refactor (b1.* -> blocks.* naming)."""
        if not any(key.startswith("b1.") for key in state_dict.keys()):
            return state_dict

        remapped: "OrderedDict[str, torch.Tensor]" = OrderedDict()
        for key, value in state_dict.items():
            if len(key) > 2 and key[0] == "b" and key[1].isdigit() and key[2] == ".":
                block_idx = int(key[1]) - 1
                suffix = key[3:]
                new_key = f"blocks.{block_idx}.{suffix}"
                remapped[new_key] = value
            else:
                remapped[key] = value
        return remapped
