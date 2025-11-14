# scripts/export_emotion_minix_onnx.py
import torch
from pathlib import Path
from train_emotion_minix import MiniXEmotion  # или откуда у тебя класс модели

def main():
    ckpt_path = Path("models") / "emotion_minix.pt"
    ckpt = torch.load(ckpt_path, map_location="cpu")
    classes = ckpt["classes"]
    img_size = ckpt.get("img_size", 96)

    model = MiniXEmotion(n_classes=len(classes), in_ch=1)
    model.load_state_dict(ckpt["model"])
    model.eval()

    dummy = torch.randn(1, 1, img_size, img_size)
    onnx_path = Path("models") / "emotion_minix.onnx"
    torch.onnx.export(
        model, dummy, onnx_path,
        input_names=["input"],
        output_names=["logits"],
        opset_version=12,
    )
    print("Exported ONNX:", onnx_path)

if __name__ == "__main__":
    main()
