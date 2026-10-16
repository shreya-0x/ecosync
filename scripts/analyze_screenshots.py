import os
from pathlib import Path
from PIL import Image

folder = Path(r"c:\Users\shrey\OneDrive\Desktop\screenshottts")
images = list(folder.glob("*.png")) + list(folder.glob("*.jpg")) + list(folder.glob("*.jpeg"))
print(f"Total images found: {len(images)}")

for img_p in sorted(images, key=lambda x: x.stat().st_mtime):
    try:
        with Image.open(img_p) as im:
            w, h = im.size
            size_kb = img_p.stat().st_size / 1024
            mtime = img_p.stat().st_mtime
            print(f"{img_p.name} | {w}x{h} | {size_kb:.1f} KB")
    except Exception as e:
        print(f"Error reading {img_p.name}: {e}")
