import os, random, shutil
from pathlib import Path

ROOT = Path("data")
TRAIN = ROOT / "train"
TEST  = ROOT / "test"
VAL   = ROOT / "val"

VAL_RATIO = 0.10  # 10%
EMOTIONS = ["angry","disgust","fear","happy","neutral","sad","surprise"]

def pick_images(p: Path):
    return [x for x in p.iterdir() if x.is_file() and x.suffix.lower() in (".jpg",".jpeg",".png")]

def main():
    assert TRAIN.exists(), f"train dir not found: {TRAIN}"
    assert TEST.exists(),  f"test dir not found: {TEST}"
    VAL.mkdir(exist_ok=True)

    random.seed(42)
    rows = []
    for emo in EMOTIONS:
        tr = TRAIN/emo; te = TEST/emo; va = VAL/emo
        if not tr.exists(): raise FileNotFoundError(tr)
        if not te.exists(): raise FileNotFoundError(te)
        va.mkdir(exist_ok=True)

        imgs = pick_images(tr)
        n_total = len(imgs)
        if n_total == 0:
            rows.append((emo, 0, 0))
            print(f"{emo:9s}  train_left={0:5d}  val={0:5d}  (no images)")
            continue

        n_val = max(int(n_total*VAL_RATIO), 1)
        random.shuffle(imgs)
        sel = imgs[:n_val]
        for src in sel:
            dst = va/src.name
            shutil.move(str(src), str(dst))
        rows.append((emo, n_total - n_val, n_val))
        print(f"{emo:9s}  train_left={n_total-n_val:5d}  val={n_val:5d}")

    print("\nSplit done.")
if __name__ == "__main__":
    main()
