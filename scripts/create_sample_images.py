import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import Config

def create_sample_images():
    samples_dir = Config.BASE_DIR / "static" / "images" / "samples"
    samples_dir.mkdir(parents=True, exist_ok=True)

    # 1. Mixed Stream Sample (Bottles, Can, Box)
    img_mixed = Image.new("RGB", (800, 600), color=(240, 238, 230))
    draw = ImageDraw.Draw(img_mixed)
    
    # Background texture lines (conveyor belt)
    draw.rectangle([0, 480, 800, 600], fill=(45, 50, 48))
    for x in range(0, 800, 40):
        draw.line([x, 480, x + 20, 600], fill=(55, 62, 60), width=3)

    # Plastic Bottle 1 (Blue clear PET)
    draw.rounded_rectangle([120, 180, 220, 480], radius=18, fill=(180, 220, 245), outline=(120, 180, 220), width=4)
    draw.rectangle([145, 120, 195, 180], fill=(160, 205, 235), outline=(120, 180, 220), width=3)
    draw.rectangle([140, 100, 200, 120], fill=(30, 100, 200)) # Cap
    draw.rectangle([120, 260, 220, 360], fill=(255, 255, 255)) # Label
    draw.text((135, 300), "PET 1", fill=(0, 0, 0))

    # Plastic Bottle 2 (Green PET)
    draw.rounded_rectangle([260, 220, 350, 490], radius=15, fill=(160, 230, 180), outline=(100, 190, 130), width=4)
    draw.rectangle([285, 160, 325, 220], fill=(150, 215, 170), outline=(100, 190, 130), width=3)
    draw.rectangle([280, 140, 330, 160], fill=(40, 160, 80)) # Cap
    draw.text((285, 310), "ECO", fill=(20, 80, 40))

    # Aluminum Can (Red metallic beverage can)
    draw.rounded_rectangle([390, 250, 490, 490], radius=20, fill=(225, 60, 60), outline=(180, 40, 40), width=4)
    draw.ellipse([390, 240, 490, 270], fill=(210, 215, 220), outline=(160, 165, 170), width=3)
    draw.text((415, 350), "ALUM", fill=(255, 255, 255))

    # Cardboard Box
    draw.rectangle([530, 230, 730, 490], fill=(200, 160, 110), outline=(150, 110, 60), width=4)
    draw.line([530, 230, 730, 490], fill=(170, 130, 80), width=2)
    draw.rectangle([580, 310, 680, 360], fill=(235, 225, 210))
    draw.text((600, 325), "KRAFT", fill=(50, 40, 30))

    path_mixed = samples_dir / "sample_mixed_stream.jpg"
    img_mixed.save(path_mixed, quality=95)
    print("Created:", path_mixed)

    # 2. Pure Beverage Bottles (Plastic PET)
    img_bottles = Image.new("RGB", (700, 500), color=(235, 238, 235))
    draw_b = ImageDraw.Draw(img_bottles)
    draw_b.rounded_rectangle([100, 100, 200, 420], radius=18, fill=(190, 225, 245), outline=(100, 160, 200), width=4)
    draw_b.rectangle([125, 60, 175, 100], fill=(160, 205, 235), outline=(100, 160, 200), width=3)
    draw_b.rounded_rectangle([250, 120, 350, 430], radius=18, fill=(170, 230, 200), outline=(90, 180, 140), width=4)
    draw_b.rectangle([275, 80, 325, 120], fill=(150, 210, 180), outline=(90, 180, 140), width=3)
    draw_b.rounded_rectangle([400, 110, 500, 420], radius=18, fill=(245, 210, 180), outline=(200, 150, 110), width=4)
    draw_b.rectangle([425, 70, 475, 110], fill=(230, 190, 160), outline=(200, 150, 110), width=3)
    draw_b.rounded_rectangle([550, 140, 640, 430], radius=16, fill=(200, 220, 245), outline=(120, 160, 210), width=4)
    
    path_bottles = samples_dir / "sample_bottles.jpg"
    img_bottles.save(path_bottles, quality=95)
    print("Created:", path_bottles)

    # 3. Cardboard Packages (Corrugated Kraft)
    img_boxes = Image.new("RGB", (650, 500), color=(230, 228, 222))
    draw_bx = ImageDraw.Draw(img_boxes)
    draw_bx.rectangle([60, 120, 280, 420], fill=(195, 155, 105), outline=(140, 100, 50), width=4)
    draw_bx.rectangle([320, 100, 580, 440], fill=(210, 170, 120), outline=(150, 110, 60), width=4)
    draw_bx.line([320, 260, 580, 260], fill=(160, 120, 70), width=3)
    
    path_boxes = samples_dir / "sample_boxes.jpg"
    img_boxes.save(path_boxes, quality=95)
    print("Created:", path_boxes)

if __name__ == "__main__":
    create_sample_images()
