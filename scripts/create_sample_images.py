import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import Config

def generate_samples():
    samples_dir = Config.BASE_DIR / "static" / "images" / "samples"
    samples_dir.mkdir(parents=True, exist_ok=True)

    # Helper to create smooth shaded backgrounds
    def create_canvas(w=800, h=600, bg_top=(25, 35, 30), bg_bottom=(12, 18, 15)):
        img = Image.new("RGB", (w, h))
        draw = ImageDraw.Draw(img)
        for y in range(h):
            ratio = y / float(h)
            r = int(bg_top[0] * (1 - ratio) + bg_bottom[0] * ratio)
            g = int(bg_top[1] * (1 - ratio) + bg_bottom[1] * ratio)
            b = int(bg_top[2] * (1 - ratio) + bg_bottom[2] * ratio)
            draw.line([(0, y), (w, y)], fill=(r, g, b))
        return img

    # 1. Redbull Can (Dry Waste / Recyclable Metal)
    img1 = create_canvas()
    d1 = ImageDraw.Draw(img1)
    # Surface shadow
    d1.ellipse([270, 480, 530, 540], fill=(5, 8, 7))
    # Can body (Silver & Blue/Silver quad)
    d1.rounded_rectangle([320, 150, 480, 500], radius=24, fill=(18, 55, 130), outline=(220, 225, 235), width=3)
    # Metallic top rim
    d1.ellipse([320, 135, 480, 175], fill=(210, 215, 225), outline=(240, 245, 255), width=2)
    d1.ellipse([375, 145, 425, 165], fill=(160, 165, 175))
    # Silver checker pattern
    d1.polygon([(320, 150), (480, 320), (480, 500), (320, 330)], fill=(200, 205, 215))
    # Redbull sun / text accent
    d1.ellipse([370, 280, 430, 340], fill=(240, 190, 10))
    d1.polygon([(345, 305), (385, 300), (400, 325)], fill=(220, 20, 40))
    d1.polygon([(455, 305), (415, 300), (400, 325)], fill=(220, 20, 40))
    d1.text((360, 370), "Red Bull", fill=(15, 30, 90))
    d1.text((350, 420), "ENERGY DRINK", fill=(220, 20, 40))
    img1.save(samples_dir / "sample_redbull.jpg", quality=95)

    # 2. Plastic Bottle (Dry Recyclable)
    img2 = create_canvas()
    d2 = ImageDraw.Draw(img2)
    d2.ellipse([270, 490, 530, 550], fill=(5, 8, 7))
    # Clear Blue PET body
    d2.rounded_rectangle([330, 200, 470, 510], radius=20, fill=(160, 215, 240), outline=(100, 180, 220), width=3)
    # Neck & Cap
    d2.rectangle([375, 120, 425, 200], fill=(150, 205, 230), outline=(100, 180, 220), width=2)
    d2.rounded_rectangle([370, 95, 430, 125], radius=6, fill=(20, 120, 230), outline=(255, 255, 255), width=2)
    # Label
    d2.rectangle([330, 290, 470, 390], fill=(245, 250, 255))
    d2.rectangle([330, 300, 470, 320], fill=(0, 150, 220))
    d2.text((365, 335), "PURE WATER", fill=(20, 60, 110))
    d2.text((375, 360), "100% RECYCLED", fill=(40, 140, 70))
    img2.save(samples_dir / "sample_bottle.jpg", quality=95)

    # 3. Apple (Wet Waste / Organic)
    img3 = create_canvas()
    d3 = ImageDraw.Draw(img3)
    d3.ellipse([270, 470, 530, 530], fill=(5, 8, 7))
    # Apple Body
    d3.ellipse([300, 210, 470, 480], fill=(210, 35, 35), outline=(160, 20, 20), width=3)
    d3.ellipse([330, 210, 500, 480], fill=(225, 45, 40), outline=(160, 20, 20), width=3)
    # Highlight
    d3.ellipse([330, 240, 380, 320], fill=(245, 100, 90))
    # Stem & Leaf
    d3.line([(400, 220), (410, 140)], fill=(90, 55, 25), width=6)
    d3.ellipse([410, 145, 470, 175], fill=(50, 160, 60), outline=(30, 110, 40), width=2)
    img3.save(samples_dir / "sample_apple.jpg", quality=95)

    # 4. Banana Peel (Wet Waste / Organic)
    img4 = create_canvas()
    d4 = ImageDraw.Draw(img4)
    d4.ellipse([250, 460, 550, 530], fill=(5, 8, 7))
    # Curved Banana Body
    points = [(260, 250), (320, 380), (450, 470), (550, 430), (500, 470), (340, 430), (280, 320)]
    d4.polygon(points, fill=(245, 210, 30), outline=(180, 150, 15))
    # Peel open flaps
    d4.polygon([(260, 250), (220, 180), (250, 280)], fill=(230, 195, 25))
    d4.polygon([(260, 250), (310, 190), (300, 270)], fill=(220, 185, 20))
    # Brown spots
    d4.ellipse([360, 410, 380, 425], fill=(90, 60, 20))
    d4.ellipse([420, 440, 440, 455], fill=(90, 60, 20))
    d4.ellipse([240, 210, 255, 225], fill=(80, 50, 15))
    img4.save(samples_dir / "sample_banana.jpg", quality=95)

    # 5. Doritos Bag (Dry Waste / Multi-layer wrapper)
    img5 = create_canvas()
    d5 = ImageDraw.Draw(img5)
    d5.ellipse([260, 480, 540, 540], fill=(5, 8, 7))
    # Bag pouch
    d5.polygon([(290, 160), (510, 160), (530, 490), (270, 490)], fill=(215, 25, 25), outline=(240, 60, 40), width=3)
    # Crimped edges
    for x in range(290, 510, 10):
        d5.line([(x, 155), (x + 5, 165)], fill=(150, 15, 15), width=2)
        d5.line([(x - 15, 485), (x - 10, 495)], fill=(150, 15, 15), width=2)
    # Doritos Logo / Triangle
    d5.polygon([(400, 250), (340, 350), (460, 350)], fill=(245, 140, 20), outline=(255, 255, 255), width=3)
    d5.text((350, 295), "Doritos", fill=(255, 255, 255))
    d5.text((345, 380), "NACHO CHEESE", fill=(255, 220, 50))
    img5.save(samples_dir / "sample_doritos.jpg", quality=95)

    # 6. Dairy Milk Chocolate (Dry/Wet Multi-material)
    img6 = create_canvas()
    d6 = ImageDraw.Draw(img6)
    d6.ellipse([260, 470, 540, 530], fill=(5, 8, 7))
    # Purple Wrapper Body
    d6.rounded_rectangle([290, 200, 510, 480], radius=12, fill=(75, 20, 130), outline=(120, 50, 180), width=3)
    # Gold milk splashes
    d6.ellipse([340, 280, 460, 340], fill=(255, 255, 255))
    d6.text((330, 305), "Dairy Milk", fill=(60, 15, 110))
    d6.text((340, 360), "SILK CHOCOLATE", fill=(245, 190, 70))
    # Unwrapped silver foil corner showing brown chocolate
    d6.polygon([(440, 200), (510, 200), (510, 270)], fill=(200, 205, 215))
    d6.polygon([(460, 200), (510, 200), (510, 250)], fill=(90, 45, 25))
    img6.save(samples_dir / "sample_dairymilk.jpg", quality=95)

    # 7. Cardboard Packaging Box (Dry Recyclable)
    img7 = create_canvas()
    d7 = ImageDraw.Draw(img7)
    d7.ellipse([220, 470, 580, 540], fill=(5, 8, 7))
    # 3D isometric Kraft Box
    d7.polygon([(260, 280), (400, 200), (540, 280), (400, 360)], fill=(215, 175, 125), outline=(160, 120, 75), width=3)
    d7.polygon([(260, 280), (400, 360), (400, 490), (260, 410)], fill=(185, 145, 95), outline=(140, 100, 60), width=3)
    d7.polygon([(400, 360), (540, 280), (540, 410), (400, 490)], fill=(160, 120, 75), outline=(120, 85, 45), width=3)
    # Sealing tape
    d7.polygon([(385, 208), (415, 192), (415, 368), (385, 352)], fill=(230, 200, 150))
    # Barcode & Recyclable Symbol
    d7.rectangle([(300, 350), (350, 380)], fill=(255, 255, 255))
    for bx in range(305, 345, 4):
        d7.line([(bx, 355), (bx, 375)], fill=(0, 0, 0), width=2)
    img7.save(samples_dir / "sample_cardboard.jpg", quality=95)

    # 8. AA Batteries & Tech Cords (Hazardous / E-Waste)
    img8 = create_canvas()
    d8 = ImageDraw.Draw(img8)
    d8.ellipse([240, 460, 560, 530], fill=(5, 8, 7))
    # USB Cord coiled
    for r in range(120, 160, 10):
        d8.arc([230, 340, 570, 480], start=0, end=180, fill=(35, 40, 45), width=6)
    # Battery 1 (Cylindrical Gold/Black)
    d8.rounded_rectangle([330, 220, 400, 460], radius=8, fill=(30, 30, 30), outline=(210, 160, 30), width=2)
    d8.rectangle([330, 220, 400, 310], fill=(225, 165, 25)) # Copper top
    d8.rectangle([355, 205, 375, 220], fill=(180, 185, 190)) # Terminal nib
    d8.text((345, 350), "AA 1.5V", fill=(255, 255, 255))
    d8.text((342, 260), "DURACELL", fill=(0, 0, 0))
    # Battery 2 (Lying down)
    d8.rounded_rectangle([420, 290, 485, 470], radius=8, fill=(30, 30, 30), outline=(210, 160, 30), width=2)
    d8.rectangle([420, 290, 485, 360], fill=(225, 165, 25))
    d8.rectangle([445, 275, 465, 290], fill=(180, 185, 190))
    d8.text((435, 400), "LITHIUM", fill=(255, 255, 255))
    img8.save(samples_dir / "sample_battery.jpg", quality=95)

    print("Created 8 high-fidelity sample images in static/images/samples/")

if __name__ == "__main__":
    generate_samples()
