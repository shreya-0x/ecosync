import os
from pathlib import Path
from PIL import Image

folder = Path(r"c:\Users\shrey\OneDrive\Desktop\screenshottts")
files = sorted(folder.glob("*.*"), key=lambda x: x.name)

print("Inventory of all images:")
for f in files:
    if f.suffix.lower() in [".png", ".jpg", ".jpeg"]:
        size_kb = f.stat().st_size / 1024
        print(f"{f.name:45} | {size_kb:6.1f} KB")
