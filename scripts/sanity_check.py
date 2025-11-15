import glob, cv2
paths = glob.glob("data/train/*/*.jpg") + glob.glob("data/val/*/*.jpg") + glob.glob("data/test/*/*.jpg")
print("total images:", len(paths))
if paths:
    img = cv2.imread(paths[0], cv2.IMREAD_GRAYSCALE)
    print("sample shape:", None if img is None else img.shape)
