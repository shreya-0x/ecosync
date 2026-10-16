import os
import shutil
from pathlib import Path
from PIL import Image

src_folder = Path(r"c:\Users\shrey\OneDrive\Desktop\screenshottts")
out_folder = Path(r"c:\Users\shrey\OneDrive\Desktop\We_Are_The_Bugs_Pitch_Deliverables\Selected_Images")
out_folder.mkdir(parents=True, exist_ok=True)

# Map key files and optionally crop browser top bars (e.g. Chrome tab bar ~80px)
selections = [
    ("01_hero_portal.jpg", "WhatsApp Image 2026-10-16 at 11.03.24 AM.jpeg", False),
    ("02_hackathon_problem_ps01.png", "Screenshot (111).png", True),
    ("03_segregation_mistakes.jpg", "WhatsApp Image 2026-10-16 at 11.03.36 AM (1).jpeg", False),
    ("04_splash_platform_launch.png", "Screenshot (106).png", True),
    ("05_workflow_3step.png", "Screenshot (120).png", True),
    ("06_live_camera_person_headphones.png", "Screenshot (112).png", True),
    ("07_live_camera_person_phone.png", "Screenshot (114).png", True),
    ("08_dense_multi_object_scan.png", "Screenshot (104).png", True),
    ("09_digital_twin_campus_topology.jpg", "WhatsApp Image 2026-10-16 at 11.03.29 AM.jpeg", False),
    ("10_can_redbull_detection.png", "Screenshot (116).png", True),
    ("11_cardboard_detection.png", "Screenshot (115).png", True),
    ("12_tech_stack_architecture.jpg", "WhatsApp Image 2026-10-16 at 11.03.37 AM (2).jpeg", False),
    ("13_smart_bin_network_table.png", "Screenshot (117).png", True),
    ("14_persisted_scan_event_log.png", "Screenshot (118).png", True),
    ("15_daily_habit_checklist.png", "Screenshot (119).png", True),
    ("16_circularity_kpis.png", "Screenshot (121).png", True),
    ("17_stakeholder_audiences.jpg", "WhatsApp Image 2026-10-16 at 11.03.37 AM (3).jpeg", False),
    ("18_capabilities_vs_roadmap.jpg", "WhatsApp Image 2026-10-16 at 11.03.37 AM (7).jpeg", False),
    ("19_collection_operations.jpg", "WhatsApp Image 2026-10-16 at 11.03.32 AM.jpeg", False)
]

for out_name, src_name, crop_browser in selections:
    src_p = src_folder / src_name
    dest_p = out_folder / out_name
    if not src_p.exists():
        print(f"Warning: {src_name} not found!")
        continue
    
    with Image.open(src_p) as img:
        w, h = img.size
        # If crop_browser is True and it's a desktop screenshot (height 768), crop out top browser bar (y=80 to y=768-48)
        if crop_browser and h == 768:
            # Crop top browser tab bar (~80px) and bottom Windows taskbar (~48px)
            cropped = img.crop((0, 80, w, h - 48))
            cropped.save(dest_p, quality=95)
            print(f"Cropped and saved {out_name} ({w}x{h} -> {cropped.size})")
        else:
            img.save(dest_p, quality=95)
            print(f"Saved {out_name} ({w}x{h})")

print(f"\nAll {len(selections)} curated images saved in {out_folder}")
