import argparse, json, random
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, WeightedRandomSampler
import torchvision.transforms as T
from torchvision.datasets import ImageFolder
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
from tqdm import tqdm

# ---------- Utils ----------
def set_seed(s=42):
    random.seed(s); np.random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)

def device_auto():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

# ---------- Model ----------
class SeparableConv2d(nn.Module):
    def __init__(self, in_ch, out_ch, k=3, s=1, p=1):
        super().__init__()
        self.depthwise = nn.Conv2d(in_ch, in_ch, k, s, p, groups=in_ch, bias=False)
        self.pointwise = nn.Conv2d(in_ch, out_ch, 1, 1, 0, bias=False)
        self.bn = nn.BatchNorm2d(out_ch)
    def forward(self, x):
        x = self.depthwise(x); x = self.pointwise(x); x = self.bn(x)
        return F.relu(x, inplace=True)

class MiniXBlock(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.sep1 = SeparableConv2d(in_ch, out_ch)
        self.sep2 = SeparableConv2d(out_ch, out_ch)
        self.pool = nn.MaxPool2d(3, stride=2, padding=1)
        self.skip = nn.Conv2d(in_ch, out_ch, 1, stride=2, bias=False)
        self.bn = nn.BatchNorm2d(out_ch)
    def forward(self, x):
        y = self.sep1(x)
        y = self.sep2(y)
        y = self.pool(y)
        s = self.bn(self.skip(x))
        return F.relu(y + s, inplace=True)

class MiniXEmotion(nn.Module):
    def __init__(self, n_classes=7, in_ch=1):
        super().__init__()
        self.entry = nn.Sequential(
            nn.Conv2d(in_ch, 8, 3, padding=1, bias=False),
            nn.BatchNorm2d(8),
            nn.ReLU(inplace=True),
        )
        self.b1 = MiniXBlock(8, 16)
        self.b2 = MiniXBlock(16, 32)
        self.b3 = MiniXBlock(32, 64)
        self.b4 = MiniXBlock(64, 128)
        self.head = nn.Sequential(
            nn.Conv2d(128, 128, 3, padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
        )
        self.fc = nn.Linear(128, n_classes)
    def forward(self, x):
        x = self.entry(x)
        x = self.b1(x); x = self.b2(x); x = self.b3(x); x = self.b4(x)
        x = self.head(x)
        x = torch.flatten(x, 1)
        return self.fc(x)

# ---------- Data ----------
def make_transforms(img_size=96):
    mean, std = (0.5,), (0.5,)
    train_tf = T.Compose([
        T.Grayscale(num_output_channels=1),
        T.Resize((img_size, img_size)),
        T.RandomHorizontalFlip(),
        T.RandomRotation(10),
        T.ToTensor(),
        T.Normalize(mean, std),
    ])
    eval_tf = T.Compose([
        T.Grayscale(num_output_channels=1),
        T.Resize((img_size, img_size)),
        T.ToTensor(),
        T.Normalize(mean, std),
    ])
    return train_tf, eval_tf

def build_loaders(data_root, batch=128, num_workers=0):
    train_tf, eval_tf = make_transforms()
    train_ds = ImageFolder(Path(data_root)/"train", transform=train_tf)
    val_ds   = ImageFolder(Path(data_root)/"val",   transform=eval_tf)
    test_ds  = ImageFolder(Path(data_root)/"test",  transform=eval_tf)

    counts = np.bincount(train_ds.targets)
    class_weights = 1.0 / np.clip(counts, 1, None)
    sample_weights = [class_weights[t] for t in train_ds.targets]
    sampler = WeightedRandomSampler(sample_weights, num_samples=len(sample_weights), replacement=True)

    # pin_memory=False на CPU, чтобы не спамил варнингами
    train_loader = DataLoader(train_ds, batch_size=batch, sampler=sampler, num_workers=num_workers, pin_memory=False)
    val_loader   = DataLoader(val_ds, batch_size=batch, shuffle=False, num_workers=num_workers, pin_memory=False)
    test_loader  = DataLoader(test_ds, batch_size=batch, shuffle=False, num_workers=num_workers, pin_memory=False)
    return train_loader, val_loader, test_loader, train_ds.classes

# ---------- Train / Eval ----------
def accuracy(logits, y):
    pred = logits.argmax(1)
    return (pred == y).float().mean().item()

def train_one_epoch(model, loader, device, opt, crit, epoch, total_epochs):
    model.train()
    total_loss, total_acc, n = 0.0, 0.0, 0
    pbar = tqdm(loader, desc=f"train {epoch}/{total_epochs}", ncols=100)
    for x, y in pbar:
        x, y = x.to(device), y.to(device)
        opt.zero_grad()
        logits = model(x)
        loss = crit(logits, y)
        loss.backward()
        opt.step()

        bs = x.size(0)
        total_loss += loss.item() * bs
        total_acc  += accuracy(logits, y) * bs
        n += bs
        pbar.set_postfix(loss=f"{total_loss/n:.4f}", acc=f"{total_acc/n:.3f}")
    return total_loss/n, total_acc/n

@torch.no_grad()
def eval_epoch(model, loader, device, crit, phase, epoch, total_epochs):
    model.eval()
    total_loss, total_acc, n = 0.0, 0.0, 0
    all_y, all_p = [], []
    pbar = tqdm(loader, desc=f"{phase} {epoch}/{total_epochs}", ncols=100)
    for x, y in pbar:
        x, y = x.to(device), y.to(device)
        logits = model(x)
        loss = crit(logits, y)
        bs = x.size(0)
        total_loss += loss.item() * bs
        total_acc  += accuracy(logits, y) * bs
        n += bs
        pbar.set_postfix(loss=f"{total_loss/n:.4f}", acc=f"{total_acc/n:.3f}")
        all_y.append(y.cpu()); all_p.append(logits.argmax(1).cpu())
    y_true = torch.cat(all_y).numpy() if all_y else np.array([])
    y_pred = torch.cat(all_p).numpy() if all_p else np.array([])
    return total_loss/n, total_acc/n, y_true, y_pred

def plot_confusion(cm, classes, out_png):
    import seaborn as sns
    plt.figure(figsize=(6,5))
    try:
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=classes, yticklabels=classes)
    except Exception:
        plt.imshow(cm, cmap="Blues"); plt.colorbar()
        plt.xticks(range(len(classes)), classes, rotation=45); plt.yticks(range(len(classes)), classes)
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                plt.text(j, i, str(cm[i,j]), ha="center", va="center")
    plt.title("Confusion Matrix"); plt.xlabel("Pred"); plt.ylabel("True")
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout(); plt.savefig(out_png, dpi=150); plt.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data")
    ap.add_argument("--epochs", type=int, default=35)
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--img_size", type=int, default=96)
    ap.add_argument("--outdir", default="models")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    set_seed(args.seed)
    dev = device_auto()
    print("Device:", dev)

    train_loader, val_loader, test_loader, classes = build_loaders(args.data, batch=args.batch)
    n_classes = len(classes)
    print(f"Datasets | train: {len(train_loader.dataset)}  val: {len(val_loader.dataset)}  test: {len(test_loader.dataset)}")
    print(f"Steps/epoch | train: {len(train_loader)}  val: {len(val_loader)}")

    model = MiniXEmotion(n_classes=n_classes, in_ch=1).to(dev)
    crit = nn.CrossEntropyLoss(label_smoothing=0.05)
    opt  = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-2)
    sch  = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs)

    best_val = -1.0
    best_path = Path(args.outdir)/"emotion_minix.pt"
    metrics_path = Path("reports")/"val_metrics.json"
    cm_png = Path("reports")/"confusion_matrix_val.png"
    Path(args.outdir).mkdir(parents=True, exist_ok=True)

    patience, bad = 7, 0
    for ep in range(1, args.epochs+1):
        tl, ta = train_one_epoch(model, train_loader, dev, opt, crit, ep, args.epochs)
        vl, va, y_true, y_pred = eval_epoch(model, val_loader, dev, crit, "val", ep, args.epochs)
        sch.step()
        print(f"epoch {ep:02d} | train: loss {tl:.4f} acc {ta:.3f} | val: loss {vl:.4f} acc {va:.3f}")

        if va > best_val:
            best_val = va; bad = 0
            torch.save({"model": model.state_dict(), "classes": classes, "img_size": args.img_size}, best_path)
            print("  -> saved best:", best_path)
            if y_true.size and y_pred.size:
                cm = confusion_matrix(y_true, y_pred, labels=list(range(n_classes)))
                plot_confusion(cm, classes, cm_png)
                rep = classification_report(y_true, y_pred, target_names=classes, output_dict=True, zero_division=0)
                save_json(metrics_path, {"val_acc": va, "val_loss": vl, "report": rep})
        else:
            bad += 1
            if bad >= patience:
                print("Early stopping.")
                break

    # ONNX export
    ckpt = torch.load(best_path, map_location="cpu")
    model.load_state_dict(ckpt["model"])
    model.eval()
    dummy = torch.randn(1, 1, ckpt.get("img_size", 96), ckpt.get("img_size", 96))
    onnx_path = Path(args.outdir)/"emotion_minix.onnx"
    torch.onnx.export(model, dummy, onnx_path, input_names=["input"], output_names=["logits"], opset_version=12)
    print("Exported ONNX:", onnx_path)

    # Quick test
    _, test_acc, _, _ = eval_epoch(model, test_loader, dev, crit, "test", 0, 0)
    print(f"TEST acc: {test_acc:.3f}")

    meta = {
        "classes": classes,
        "input_size": [ckpt.get("img_size", 96), ckpt.get("img_size", 96)],
        "normalization": {"mean":[0.5], "std":[0.5]},
        "version": "1.0.0",
        "arch": "mini-xception",
    }
    save_json(Path(args.outdir)/"meta.json", meta)

if __name__ == "__main__":
    set_seed(42)
    main()
