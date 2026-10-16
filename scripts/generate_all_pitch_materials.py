import os
import sys
from pathlib import Path
from PIL import Image

# PowerPoint Generation
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Word Generation
import docx
from docx.shared import Inches as DocxInches, Pt as DocxPt, RGBColor as DocxRGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# PDF Generation
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

OUTPUT_DIR = Path(r"c:\Users\shrey\OneDrive\Desktop\We_Are_The_Bugs_Pitch_Deliverables")
IMAGES_DIR = OUTPUT_DIR / "Selected_Images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PPTX_PATH = OUTPUT_DIR / "We_Are_The_Bugs_Hackathon_Pitch.pptx"
PDF_DECK_PATH = OUTPUT_DIR / "We_Are_The_Bugs_Hackathon_Pitch.pdf"
DOCX_CHEAT_SHEET_PATH = OUTPUT_DIR / "We_Are_The_Bugs_Pitch_Cheat_Sheet.docx"
PDF_CHEAT_SHEET_PATH = OUTPUT_DIR / "We_Are_The_Bugs_Pitch_Cheat_Sheet.pdf"
README_PATH = OUTPUT_DIR / "README.md"

# Color Palette
BG_COLOR = RGBColor(7, 13, 10)         # Deep Forest Black #070d0a
SURFACE_COLOR = RGBColor(14, 24, 19)   # Elevated Card #0e1813
SURFACE_BORDER = RGBColor(25, 45, 34)  # Subtle Green Border
ACCENT_GREEN = RGBColor(0, 229, 153)   # Emerald Green #00e599
ACCENT_CYAN = RGBColor(56, 189, 248)   # Tech Cyan #38bdf8
ACCENT_ORANGE = RGBColor(249, 115, 22) # Alert Orange #f97316
TEXT_WHITE = RGBColor(248, 250, 252)   # Pure Off-White
TEXT_MUTED = RGBColor(148, 163, 184)   # Slate Muted Gray
TEXT_DIM = RGBColor(100, 116, 139)     # Dim Gray

# -------------------------------------------------------------
# 1. POWERPOINT GENERATOR (13 SLIDES WITH REAL SCREENSHOTS & NOTES)
# -------------------------------------------------------------

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def apply_background(slide):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_COLOR
    bg.line.fill.background()
    return bg

def add_header(slide, tracker: str, title: str, subtitle: str):
    tb_tr = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.35))
    tf_tr = tb_tr.text_frame
    tf_tr.word_wrap = True
    tf_tr.margin_left = tf_tr.margin_top = tf_tr.margin_right = tf_tr.margin_bottom = 0
    p_tr = tf_tr.paragraphs[0]
    p_tr.text = tracker.upper()
    p_tr.font.name = "Arial"
    p_tr.font.size = Pt(10)
    p_tr.font.bold = True
    p_tr.font.color.rgb = ACCENT_GREEN

    tb_ti = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.733), Inches(0.55))
    tf_ti = tb_ti.text_frame
    tf_ti.word_wrap = True
    tf_ti.margin_left = tf_ti.margin_top = tf_ti.margin_right = tf_ti.margin_bottom = 0
    p_ti = tf_ti.paragraphs[0]
    p_ti.text = title
    p_ti.font.name = "Arial"
    p_ti.font.size = Pt(21)
    p_ti.font.bold = True
    p_ti.font.color.rgb = TEXT_WHITE

    if subtitle:
        tb_sub = slide.shapes.add_textbox(Inches(0.8), Inches(1.28), Inches(11.733), Inches(0.35))
        tf_sub = tb_sub.text_frame
        tf_sub.word_wrap = True
        tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = 0
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle
        p_sub.font.name = "Arial"
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = TEXT_MUTED

def add_footer(slide, current_slide: int, total_slides: int = 13):
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = f"ECOSYNC // SMART WASTE MANAGEMENT & DIGITAL TWIN   |   TEAM: WE ARE THE BUGS   |   SLIDE {current_slide:02d} OF {total_slides:02d}"
    p.font.name = "Arial"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = TEXT_DIM

def add_card(slide, left, top, width, height, fill_color=SURFACE_COLOR, border_color=SURFACE_BORDER):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.5)
    else:
        shape.line.fill.background()
    return shape

def add_speaker_notes(slide, script: str, main_point: str, transition: str, question: str, answer: str):
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    notes_content = f"""🎙️ PRESENTER SCRIPT:
{script}

🎯 MAIN POINT TO EMPHASIZE:
{main_point}

🔄 TRANSITION TO NEXT SLIDE:
{transition}

❓ LIKELY JUDGE QUESTION:
"{question}"

💡 EVIDENCE-BASED ANSWER:
{answer}
"""
    text_frame.text = notes_content

# ==============================================================================
# SLIDE 1: THE OPENING
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
apply_background(s1)

# Large Title Block
tb1 = s1.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.733), Inches(2.2))
tf1 = tb1.text_frame
tf1.word_wrap = True
tf1.margin_left = tf1.margin_top = tf1.margin_right = tf1.margin_bottom = 0

p1_badge = tf1.paragraphs[0]
p1_badge.text = "DAYANANDA SAGAR UNIVERSITY  //  DSU CODE CLASH 2.0  //  PROBLEM STATEMENT 01"
p1_badge.font.name = "Arial"
p1_badge.font.size = Pt(11)
p1_badge.font.bold = True
p1_badge.font.color.rgb = ACCENT_GREEN

p1_team = tf1.add_paragraph()
p1_team.text = "WE ARE THE BUGS"
p1_team.font.name = "Arial"
p1_team.font.size = Pt(36)
p1_team.font.bold = True
p1_team.font.color.rgb = TEXT_WHITE
p1_team.space_before = Pt(8)

p1_sub = tf1.add_paragraph()
p1_sub.text = "EcoSync: Smart Waste Management Digital Twin & Vision Assistant"
p1_sub.font.name = "Arial"
p1_sub.font.size = Pt(16)
p1_sub.font.color.rgb = ACCENT_CYAN
p1_sub.space_before = Pt(6)

p1_desc = tf1.add_paragraph()
p1_desc.text = "Bridging Edge Computer Vision, Campus Spatial Telemetry, and Verifiable Circular Citizen Action."
p1_desc.font.name = "Arial"
p1_desc.font.size = Pt(12)
p1_desc.font.color.rgb = TEXT_MUTED
p1_desc.space_before = Pt(4)

# Hero image card
img1_path = IMAGES_DIR / "01_hero_portal.jpg"
if img1_path.exists():
    card1 = add_card(s1, Inches(0.8), Inches(3.1), Inches(8.0), Inches(3.7))
    s1.shapes.add_picture(str(img1_path), Inches(0.9), Inches(3.2), Inches(7.8), Inches(3.5))

# Right meta card
card1_r = add_card(s1, Inches(9.0), Inches(3.1), Inches(3.533), Inches(3.7))
tb1_r = s1.shapes.add_textbox(Inches(9.2), Inches(3.3), Inches(3.133), Inches(3.3))
tf1_r = tb1_r.text_frame
tf1_r.word_wrap = True
tf1_r.margin_left = tf1_r.margin_top = tf1_r.margin_right = tf1_r.margin_bottom = 0

pr1 = tf1_r.paragraphs[0]
pr1.text = "LIVE SYSTEM TELEMETRY"
pr1.font.size = Pt(11)
pr1.font.bold = True
pr1.font.color.rgb = ACCENT_GREEN

metrics = [
    ("Neural Architecture", "Ultralytics YOLO11 Nano"),
    ("Model Classes", "17 Consumer Waste Classes"),
    ("Inference Speed", "< 150ms per frame (CPU)"),
    ("Human Guard", "Person = Non-Waste Filter"),
    ("Digital Twin", "6 Campus Nodes & Fleet"),
    ("Persistence", "SQLite Circular Ledger"),
    ("Live Deployment", "ecosync-bz9l.onrender.com"),
    ("Local Server", "http://127.0.0.1:5000")
]

for label, val in metrics:
    p_m = tf1_r.add_paragraph()
    p_m.text = f"• {label}: {val}"
    p_m.font.size = Pt(9.5)
    p_m.font.color.rgb = TEXT_WHITE
    p_m.space_before = Pt(4)

add_footer(s1, 1)

add_speaker_notes(
    s1,
    script="Good morning judges. We are team WE ARE THE BUGS, and today we are presenting EcoSync: our comprehensive solution for Problem Statement 01: Smart Waste Management Digital Twin. EcoSync is a functioning, full-stack platform running right now at http://127.0.0.1:5000 and deployed on the web. It directly pairs real-time YOLO computer vision with a spatial digital twin and an auditable circular database.",
    main_point="EcoSync is already fully built, running on local hardware with zero external cloud dependencies, and solves both citizen segregation and municipal operational blind spots.",
    transition="Before showing you our live neural scanner, let us examine the critical problem in municipal waste management that motivated this project.",
    question="Is this a conceptual prototype or an actual working application?",
    answer="It is a 100% operational application. We have Ultralytics YOLO running local inference on live camera feeds, an active SQLite database, 24 automated unit tests, and live deployment on Render."
)

# ==============================================================================
# SLIDE 2: THE PROBLEM
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
apply_background(s2)
add_header(s2, "PROBLEM CONTEXT // DSU CODE CLASH 2.0 (PS01)", "The Broken Waste Lifecycle: Why Recycling Fails at the Source", "Cities spend millions on collection fleets, yet over 80% of recyclable batches are contaminated before reaching processing plants.")

# Left card: Challenge & Evidence
card2_l = add_card(s2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
tb2_l = s2.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.6))
tf2_l = tb2_l.text_frame
tf2_l.word_wrap = True
tf2_l.margin_left = tf2_l.margin_top = tf2_l.margin_right = tf2_l.margin_bottom = 0

p2_l1 = tf2_l.paragraphs[0]
p2_l1.text = "THE THREE FATAL SYSTEM DISRUPTIONS"
p2_l1.font.size = Pt(12)
p2_l1.font.bold = True
p2_l1.font.color.rgb = ACCENT_ORANGE

problems = [
    ("1. Citizen Sorting Confusion", "Citizens want to recycle, but resin codes (PETE 1, HDPE 2, PP 5) are illegible or confusing. 70%+ of people cannot identify whether a coated coffee cup or blister pack is recyclable, leading to wishcycling."),
    ("2. The Contamination Domino Effect", "A single unwashed peanut butter jar or punctured lithium battery can ruin an entire 500kg batch of dry recyclables at a Material Recovery Facility (MRF), forcing the entire load into landfills."),
    ("3. Blind Municipal Operations", "Sanitation vehicles drive static, fixed routes regardless of whether bins are overflowing or empty. Without dynamic fill telemetry, fuel is wasted and overflow hot-spots create public health hazards.")
]

for title, desc in problems:
    p_t = tf2_l.add_paragraph()
    p_t.text = title
    p_t.font.size = Pt(11)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE
    p_t.space_before = Pt(8)
    
    p_d = tf2_l.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(9.5)
    p_d.font.color.rgb = TEXT_MUTED
    p_d.space_before = Pt(2)

# Right image card: Segregation mistakes from real website
img2_path = IMAGES_DIR / "03_segregation_mistakes.jpg"
if img2_path.exists():
    card2_r = add_card(s2, Inches(6.6), Inches(1.8), Inches(5.933), Inches(5.0))
    s2.shapes.add_picture(str(img2_path), Inches(6.75), Inches(1.95), Inches(5.633), Inches(4.7))

add_footer(s2, 2)

add_speaker_notes(
    s2,
    script="Look at what currently happens in our cities and campuses. Municipalities buy expensive compactor trucks and build sorting facilities, but the system breaks down at the very first touchpoint: the citizen in front of the bin. People cannot distinguish multi-layer packaging from recyclable PET, and one greasy container or battery contaminates the entire truck load. Meanwhile, collection trucks drive around blindly on fixed schedules without knowing which bins actually need servicing.",
    main_point="Waste management failure is not a logistics problem; it is an information problem at the point of disposal combined with zero operational visibility.",
    transition="To fix this, we created EcoSync: an end-to-end platform bridging the citizen's camera with the municipal command center.",
    question="Why focus on household segregation when facilities have sorting machines?",
    answer="Optical sorters and magnetic belts at MRFs cannot clean food grease or reverse contamination. Once paper is soaked with oil or organic slurry, its fibers cannot be repulped. Segregation at source is mathematically the only way to achieve over 70% landfill diversion."
)

# ==============================================================================
# SLIDE 3: OUR SOLUTION
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
apply_background(s3)
add_header(s3, "SYSTEM ARCHITECTURE // VALUE PROPOSITION", "EcoSync: Real-Time AI Vision Meets Operational Spatial Digital Twin", "An intelligent ecosystem that identifies waste at the moment of disposal and synchronizes telemetry with a campus digital twin.")

# Left Card: Platform Splash Screenshot
img3_path = IMAGES_DIR / "04_splash_platform_launch.png"
if img3_path.exists():
    card3_l = add_card(s3, Inches(0.8), Inches(1.8), Inches(6.0), Inches(5.0))
    s3.shapes.add_picture(str(img3_path), Inches(0.95), Inches(1.95), Inches(5.7), Inches(4.7))

# Right Column: 3 Pillars
card3_r = add_card(s3, Inches(7.0), Inches(1.8), Inches(5.533), Inches(5.0))
tb3_r = s3.shapes.add_textbox(Inches(7.2), Inches(2.0), Inches(5.133), Inches(4.6))
tf3_r = tb3_r.text_frame
tf3_r.word_wrap = True
tf3_r.margin_left = tf3_r.margin_top = tf3_r.margin_right = tf3_r.margin_bottom = 0

p3_head = tf3_r.paragraphs[0]
p3_head.text = "THE THREE INTEGRATED PILLARS"
p3_head.font.size = Pt(12)
p3_head.font.bold = True
p3_head.font.color.rgb = ACCENT_GREEN

pillars = [
    ("1. Instant AI Vision Studio", "Equips citizens with browser-based computer vision. Users capture items via live webcam or file upload, receiving instant bounding boxes, material identification, and clean bin destinations in <150ms."),
    ("2. Spatial Campus Digital Twin", "Provides facility managers and municipal coordinators with a live interactive topology of campus bins, showing volumetric fill percentages, sensor battery health, and dynamic truck dispatch queues."),
    ("3. Verifiable Circular Ledger", "Every confirmed scan is recorded in SQLite with calculated carbon (CO2e) avoidance factors. Citizens see their cumulative impact, while authorities export verified RFC-4180 CSV compliance logs.")
]

for title, desc in pillars:
    p_t = tf3_r.add_paragraph()
    p_t.text = title
    p_t.font.size = Pt(11)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE
    p_t.space_before = Pt(10)
    
    p_d = tf3_r.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(9.5)
    p_d.font.color.rgb = TEXT_MUTED
    p_d.space_before = Pt(3)

add_footer(s3, 3)

add_speaker_notes(
    s3,
    script="EcoSync delivers a complete circular loop across three pillars. First, an AI Vision Studio that tells the citizen exactly what they are holding and how to prepare it in under 150 milliseconds. Second, a Spatial Digital Twin that mirrors the real-world campus bin network with live volumetric fill levels and collection routes. Third, an auditable circular ledger that calculates verified carbon savings and exports CSV audit files.",
    main_point="EcoSync is not just an AI camera or just an admin dashboard; it connects citizen behavior directly to municipal facility operations.",
    transition="Let us look at how the real AI scanner performs with live camera feeds.",
    question="How do citizens access EcoSync? Do they need to install an app?",
    answer="EcoSync is completely web-native. It runs directly in any modern mobile or desktop browser via HTML5 and WebRTC, with zero app store downloads required."
)

# ==============================================================================
# SLIDE 4: LIVE PRODUCT EXPERIENCE
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
apply_background(s4)
add_header(s4, "LIVE SYSTEM EVIDENCE // COMPUTER VISION ENGINE", "Empirical Computer Vision with Person Non-Waste Protection", "Local YOLO model running real-time inference on webcam captures with exact confidence scores and human exclusion logic.")

# Two side-by-side screenshots showing live camera
img4_a = IMAGES_DIR / "06_live_camera_person_headphones.png"
img4_b = IMAGES_DIR / "07_live_camera_person_phone.png"

if img4_a.exists():
    card4_a = add_card(s4, Inches(0.8), Inches(1.8), Inches(5.7), Inches(3.4))
    s4.shapes.add_picture(str(img4_a), Inches(0.9), Inches(1.9), Inches(5.5), Inches(3.2))

if img4_b.exists():
    card4_b = add_card(s4, Inches(6.8), Inches(1.8), Inches(5.7), Inches(3.4))
    s4.shapes.add_picture(str(img4_b), Inches(6.9), Inches(1.9), Inches(5.5), Inches(3.2))

# Bottom Callout Card
card4_bot = add_card(s4, Inches(0.8), Inches(5.35), Inches(11.733), Inches(1.55))
tb4_bot = s4.shapes.add_textbox(Inches(1.0), Inches(5.45), Inches(11.333), Inches(1.35))
tf4_bot = tb4_bot.text_frame
tf4_bot.word_wrap = True
tf4_bot.margin_left = tf4_bot.margin_top = tf4_bot.margin_right = tf4_bot.margin_bottom = 0

p4_head = tf4_bot.paragraphs[0]
p4_head.text = "FOUR PRODUCTION-GRADE VISION CAPABILITIES DEMONSTRATED ABOVE:"
p4_head.font.size = Pt(10.5)
p4_head.font.bold = True
p4_head.font.color.rgb = ACCENT_CYAN

p4_c1 = tf4_bot.add_paragraph()
p4_c1.text = "1. Genuine WebRTC Live Camera: Start, Pause, and Stop camera controls with aspect-ratio normalized SVG bounding boxes."
p4_c1.font.size = Pt(9.5)
p4_c1.font.color.rgb = TEXT_WHITE
p4_c1.space_before = Pt(3)

p4_c2 = tf4_bot.add_paragraph()
p4_c2.text = "2. Grounded Multi-Object Inference: Actual confidence ratings (e.g. 89.1% Electronics) derived from genuine model tensors."
p4_c2.font.size = Pt(9.5)
p4_c2.font.color.rgb = TEXT_WHITE

p4_c3 = tf4_bot.add_paragraph()
p4_c3.text = "3. Person Non-Waste Protection: COCO class 0 (Human) is classified as 'Uncategorized Non-Waste' with purple bounding box and locked confirmation button, guaranteeing humans are NEVER logged as waste into the database."
p4_c3.font.size = Pt(9.5)
p4_c3.font.color.rgb = ACCENT_GREEN

add_footer(s4, 4)

add_speaker_notes(
    s4,
    script="These are actual screenshots captured directly from our live application. On the left, our camera captures the user holding headphones; on the right, a smartphone. Notice two critical engineering breakthroughs: First, the model generates real bounding boxes with calibrated confidence percentages like 89.1%. Second, look at the purple bounding box around the user: our model natively detects the Person, classifies them as 'Uncategorized Non-Waste', and locks the recording button so human operators can never be recorded into the waste database.",
    main_point="We do not fake detections with green CSS divs. Our model does genuine neural inference and distinguishes actual discardable items from the person holding them.",
    transition="Now let's trace how data flows from this camera sensor into the broader municipal pipeline.",
    question="What happens if the model detects an object with low confidence?",
    answer="We implemented a dynamic confidence slider (defaulting to 20%). If detection confidence is marginal, the UI marks the item as uncertain and requires the citizen to confirm the category before writing to the database."
)

# ==============================================================================
# SLIDE 5: HOW IT WORKS
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
apply_background(s5)
add_header(s5, "END-TO-END WORKFLOW // DATA PIPELINE", "From Camera Sensor to Municipal Fleet Recovery", "A transparent, deterministic 5-stage pipeline connecting citizen action to municipal circular operations.")

# Left Workflow diagram screenshot
img5_path = IMAGES_DIR / "05_workflow_3step.png"
if img5_path.exists():
    card5_l = add_card(s5, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
    s5.shapes.add_picture(str(img5_path), Inches(0.95), Inches(1.95), Inches(5.3), Inches(4.7))

# Right 5-stage architecture breakdown
card5_r = add_card(s5, Inches(6.6), Inches(1.8), Inches(5.933), Inches(5.0))
tb5_r = s5.shapes.add_textbox(Inches(6.8), Inches(2.0), Inches(5.533), Inches(4.6))
tf5_r = tb5_r.text_frame
tf5_r.word_wrap = True
tf5_r.margin_left = tf5_r.margin_top = tf5_r.margin_right = tf5_r.margin_bottom = 0

p5_h = tf5_r.paragraphs[0]
p5_h.text = "THE 5 OPERATIONAL STAGES"
p5_h.font.size = Pt(12)
p5_h.font.bold = True
p5_h.font.color.rgb = ACCENT_GREEN

stages = [
    ("STAGE 1: Sensor Ingestion", "WebRTC camera stream captures frame or citizen drops image file (JPG/PNG/WebP). Decompression validation prevents memory overload."),
    ("STAGE 2: YOLO Neural Vision", "Local Ultralytics YOLO model computes tensor inference, returning class IDs, bounding box pixel coordinates, and confidence weights in <150ms."),
    ("STAGE 3: Separation of Concepts", "Separates visual detection ('bottle') from object identity ('Plastic Beverage Bottle'), material ('PET #1'), category ('Recyclables'), and action ('Rinse & crush')."),
    ("STAGE 4: SQLite Circular Ledger", "Confirmed disposals execute an ACID transaction in SQLite, logging timestamp, weight in kg, and calculated avoided CO2e emissions."),
    ("STAGE 5: Digital Twin & Dispatch", "Telemetry feeds update simulated campus bin fill levels. When a bin crosses 90%, a Critical Alert triggers automated collection truck queueing.")
]

for st_title, st_desc in stages:
    p_t = tf5_r.add_paragraph()
    p_t.text = st_title
    p_t.font.size = Pt(10)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE
    p_t.space_before = Pt(6)
    
    p_d = tf5_r.add_paragraph()
    p_d.text = st_desc
    p_d.font.size = Pt(8.5)
    p_d.font.color.rgb = TEXT_MUTED
    p_d.space_before = Pt(1)

add_footer(s5, 5)

add_speaker_notes(
    s5,
    script="Here is the complete end-to-end operational pipeline. It starts at Stage 1 when a citizen opens their camera. Stage 2 executes local YOLO inference in under 150 milliseconds. In Stage 3, we strictly separate the visual detection from the material substrate and bin destination. In Stage 4, confirmed actions are persisted in our SQLite ledger with exact carbon calculations. Finally, Stage 5 synchronizes these records with our campus Digital Twin, queuing automated collection trucks when bins reach capacity.",
    main_point="Every part of this architecture is implemented in the codebase: from the WebRTC frontend to the Flask REST endpoints and the SQLite relational tables.",
    transition="Let's dive deeper into the core requirement of Problem Statement 01: The Digital Twin.",
    question="Are the IoT sensor readings real physical sensors or simulated?",
    answer="We maintain strict scientific transparency: the current campus bin readings are generated from our verified deterministic simulation engine and stored in SQLite. We do not claim physical LoRaWAN sensors are deployed today, but our REST schema is 100% ready for real sensor ingestion."
)

# ==============================================================================
# SLIDE 6: THE DIGITAL TWIN
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
apply_background(s6)
add_header(s6, "PROBLEM STATEMENT 01 CORE // DIGITAL TWIN", "The Campus Digital Twin: Spatial Topology & Dynamic Fleet Operations", "A software replica of physical campus waste nodes displaying volumetric fill, battery health, and dynamic service actions.")

# Left Image: Campus Hub Spatial Topology
img6_path = IMAGES_DIR / "09_digital_twin_campus_topology.jpg"
if img6_path.exists():
    card6_l = add_card(s6, Inches(0.8), Inches(1.8), Inches(6.8), Inches(5.0))
    s6.shapes.add_picture(str(img6_path), Inches(0.95), Inches(1.95), Inches(6.5), Inches(4.7))

# Right Column: Digital Twin Capabilities
card6_r = add_card(s6, Inches(7.8), Inches(1.8), Inches(4.733), Inches(5.0))
tb6_r = s6.shapes.add_textbox(Inches(8.0), Inches(2.0), Inches(4.333), Inches(4.6))
tf6_r = tb6_r.text_frame
tf6_r.word_wrap = True
tf6_r.margin_left = tf6_r.margin_top = tf6_r.margin_right = tf6_r.margin_bottom = 0

p6_h = tf6_r.paragraphs[0]
p6_h.text = "DIGITAL TWIN CAPABILITIES"
p6_h.font.size = Pt(12)
p6_h.font.bold = True
p6_h.font.color.rgb = ACCENT_GREEN

dt_features = [
    ("Spatial Facility Grid", "Interactive 2D spatial canvas modeling 4 campus zones (Central Quad, Food Court, Tech Labs, Logistics) with real-time pulsating telemetry nodes."),
    ("Live Volumetric Fill Levels", "Tracks container capacity in real time: BIN-05 (Sports Complex) at 93% triggers a Critical Alert; BIN-02 (Food Court) at 89% warns Nearing Full."),
    ("Battery Telemetry", "Monitors ultrasonic sensor power reserves (76% to 98%), preventing operational blind spots before sensors go offline."),
    ("Fleet Dispatch Operations", "Connects bins directly to collection routes: TRK-R01 Zone A Priority Express (Dispatched) and TRK-R02 Cafeteria Organics (In Transit)."),
    ("One-Click Servicing", "Facility managers can trigger 'Empty Bin' or route dispatch directly from the UI, persisting state changes into SQLite.")
]

for dt_t, dt_d in dt_features:
    p_t = tf6_r.add_paragraph()
    p_t.text = dt_t
    p_t.font.size = Pt(10)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE
    p_t.space_before = Pt(6)
    
    p_d = tf6_r.add_paragraph()
    p_d.text = dt_d
    p_d.font.size = Pt(8.5)
    p_d.font.color.rgb = TEXT_MUTED
    p_d.space_before = Pt(1)

add_footer(s6, 6)

add_speaker_notes(
    s6,
    script="Here is our Digital Twin Command Centre. As you can see, we represent the physical campus as a spatial network with 4 distinct zones. Each node displays live volumetric fill percentage and sensor battery levels. When BIN-05 hits 93%, the system automatically flags a Critical Alert. The facility manager can click 'Service / Empty Bin' or view the connected collection fleet routes where electric collection trucks are dispatched dynamically.",
    main_point="Our Digital Twin is not a decorative 3D animation; it is an actionable decision support tool directly coupled to database records and collection dispatch workflows.",
    transition="Next, let's explore our AI and Computer Vision innovations in detail.",
    question="Why did you choose a 2D spatial grid instead of a complex 3D model?",
    answer="We prioritized functional operational utility over decorative 3D graphics. A 2D spatial grid loads instantly on mobile devices, runs at 60 FPS without GPU lag, and provides immediate operational clarity to facility managers and sanitation workers."
)

# ==============================================================================
# SLIDE 7: AI AND TECHNICAL INNOVATION
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
apply_background(s7)
add_header(s7, "AI INNOVATION // NEURAL INFERENCE & TAXONOMY", "Grounded Computer Vision Engineered for Real-World Waste Streams", "Local YOLO neural inference paired with strict separation of concepts and dense multi-object handling.")

# Two image cards: Redbull Can + Cardboard
img7_a = IMAGES_DIR / "10_can_redbull_detection.png"
img7_b = IMAGES_DIR / "11_cardboard_detection.png"

if img7_a.exists():
    card7_a = add_card(s7, Inches(0.8), Inches(1.8), Inches(4.5), Inches(3.2))
    s7.shapes.add_picture(str(img7_a), Inches(0.9), Inches(1.9), Inches(4.3), Inches(3.0))

if img7_b.exists():
    card7_b = add_card(s7, Inches(5.5), Inches(1.8), Inches(4.5), Inches(3.2))
    s7.shapes.add_picture(str(img7_b), Inches(5.6), Inches(1.9), Inches(4.3), Inches(3.0))

# Right Column: Technical Innovations
card7_r = add_card(s7, Inches(10.2), Inches(1.8), Inches(2.333), Inches(5.0))
tb7_r = s7.shapes.add_textbox(Inches(10.3), Inches(2.0), Inches(2.133), Inches(4.6))
tf7_r = tb7_r.text_frame
tf7_r.word_wrap = True
tf7_r.margin_left = tf7_r.margin_top = tf7_r.margin_right = tf7_r.margin_bottom = 0

p7_h = tf7_r.paragraphs[0]
p7_h.text = "AI SPECS"
p7_h.font.size = Pt(11)
p7_h.font.bold = True
p7_h.font.color.rgb = ACCENT_CYAN

ai_specs = [
    ("Model Family", "YOLO11 Nano"),
    ("Class Count", "17 Verified"),
    ("Latency", "112ms CPU"),
    ("B-Box Space", "Normalized [0,1]"),
    ("Human Filter", "COCO Class 0"),
    ("Confidence", "Calibrated %"),
    ("Multi-Object", "Supported"),
    ("Fallback", "Semantic Audit")
]

for k, v in ai_specs:
    p_s = tf7_r.add_paragraph()
    p_s.text = f"{k}:\n{v}"
    p_s.font.size = Pt(9)
    p_s.font.bold = True
    p_s.font.color.rgb = TEXT_WHITE
    p_s.space_before = Pt(4)

# Bottom Card: The 5 Concepts Separation
card7_bot = add_card(s7, Inches(0.8), Inches(5.15), Inches(9.2), Inches(1.75))
tb7_bot = s7.shapes.add_textbox(Inches(1.0), Inches(5.25), Inches(8.8), Inches(1.55))
tf7_bot = tb7_bot.text_frame
tf7_bot.word_wrap = True
tf7_bot.margin_left = tf7_bot.margin_top = tf7_bot.margin_right = tf7_bot.margin_bottom = 0

p7_b_h = tf7_bot.paragraphs[0]
p7_b_h.text = "THE ARCHITECTURAL SEPARATION OF 5 DISTINCT CONCEPTS"
p7_b_h.font.size = Pt(10.5)
p7_b_h.font.bold = True
p7_b_h.font.color.rgb = ACCENT_GREEN

concepts_text = (
    "Unlike naive AI projects that conflate model predictions with disposal instructions, EcoSync enforces a strict separation:\n"
    "• 1. Visual Detection: What the neural network visually recognizes (e.g. 'bottle' with 93.5% confidence).\n"
    "• 2. Object Identity: Standard human nomenclature ('Redbull Beverage Can' or 'Cardboard Shipping Box').\n"
    "• 3. Material Substrate: Physical composition ('Aluminum Alloy #ALU' or 'Unbleached Kraft Paperboard').\n"
    "• 4. Waste Stream Category: Canonical stream ('Recyclable materials - Dry Waste').\n"
    "• 5. Actionable Citizen Blueprint: Specific handling ('Rinse out liquid, push pull-tab flat, crush to save space')."
)
p7_b_d = tf7_bot.add_paragraph()
p7_b_d.text = concepts_text
p7_b_d.font.size = Pt(8.5)
p7_b_d.font.color.rgb = TEXT_MUTED
p7_b_d.space_before = Pt(2)

add_footer(s7, 7)

add_speaker_notes(
    s7,
    script="A critical AI innovation in EcoSync is what we call the 'Separation of Five Concepts'. Many hackathon projects make the mistake of having a model output 'Recycle Bin'. But a model only sees visual features. EcoSync separates: 1) Visual Class, 2) Human Object Identity, 3) Material Substrate, 4) Canonical Waste Stream, and 5) Actionable Citizen Blueprint. Furthermore, our bounding boxes use normalized coordinates between 0 and 1, ensuring zero visual drift across different screen sizes.",
    main_point="We do not make unsupported claims about AI. We separate visual detection from material chemistry and circular handling rules.",
    transition="Now let's examine the production technology stack that powers this performance.",
    question="Can your model detect multiple items in a single photograph?",
    answer="Yes. Our YOLO model supports multi-object detection simultaneously. We tested it with dense waste photos containing up to 19 distinct items, all segmented with individual bounding boxes and category breakdowns."
)

# ==============================================================================
# SLIDE 8: ARCHITECTURE AND TECHNOLOGY STACK
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
apply_background(s8)
add_header(s8, "TECHNICAL FOUNDATION // PRODUCTION IMPLEMENTATION", "Production-Ready Stack: Lightweight, Robust & Zero Cloud Lock-In", "Engineered for complete local reproducibility on Windows without complex infrastructure or paid API dependencies.")

# Left Image: Tech Stack Card from website
img8_path = IMAGES_DIR / "12_tech_stack_architecture.jpg"
if img8_path.exists():
    card8_l = add_card(s8, Inches(0.8), Inches(1.8), Inches(6.0), Inches(5.0))
    s8.shapes.add_picture(str(img8_path), Inches(0.95), Inches(1.95), Inches(5.7), Inches(4.7))

# Right Column: 4 Architecture Layers
card8_r = add_card(s8, Inches(7.0), Inches(1.8), Inches(5.533), Inches(5.0))
tb8_r = s8.shapes.add_textbox(Inches(7.2), Inches(2.0), Inches(5.133), Inches(4.6))
tf8_r = tb8_r.text_frame
tf8_r.word_wrap = True
tf8_r.margin_left = tf8_r.margin_top = tf8_r.margin_right = tf8_r.margin_bottom = 0

p8_h = tf8_r.paragraphs[0]
p8_h.text = "THE 4 ARCHITECTURAL LAYERS"
p8_h.font.size = Pt(12)
p8_h.font.bold = True
p8_h.font.color.rgb = ACCENT_GREEN

layers = [
    ("LAYER 1: Frontend & Interface Layer", "HTML5, CSS3 Custom Properties, Vanilla ES6 JavaScript. Zero Node.js build overhead, responsive dark/light theme, SVG vector bounding overlays, and WebRTC media streams."),
    ("LAYER 2: Application REST API Layer", "Python 3.12 with Flask 3.0. Modular blueprints for Scanner, Digital Twin, Waste Guide, Analytics, Advisory, and Demo systems with complete error boundaries."),
    ("LAYER 3: AI Inference Engine", "Ultralytics YOLO11 Nano (yolo11n.pt). Local CPU execution in ~112ms with fallback semantic visual feature extraction. Zero paid cloud vision API costs."),
    ("LAYER 4: Relational Persistence Layer", "SQLite relational database with foreign keys, transactional integrity, and persistent tables for scans, detections, smart bins, and collection dispatches.")
]

for l_title, l_desc in layers:
    p_t = tf8_r.add_paragraph()
    p_t.text = l_title
    p_t.font.size = Pt(10)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE
    p_t.space_before = Pt(8)
    
    p_d = tf8_r.add_paragraph()
    p_d.text = l_desc
    p_d.font.size = Pt(8.5)
    p_d.font.color.rgb = TEXT_MUTED
    p_d.space_before = Pt(2)

add_footer(s8, 8)

add_speaker_notes(
    s8,
    script="Our architecture was deliberately chosen for speed, reliability, and zero deployment friction. We avoided heavy frameworks like React or Node build steps. Instead, we used clean HTML5, modern CSS, and vanilla JavaScript communicating with a modular Python Flask backend. The YOLO model runs locally on the CPU with zero latency and zero paid API costs, and all records persist reliably in SQLite.",
    main_point="Any evaluator can clone our repository and run it on Windows with just two commands: pip install -r requirements.txt and python app.py.",
    transition="Let's look at how this data supports municipal compliance and decision making.",
    question="Why choose SQLite over PostgreSQL or MongoDB?",
    answer="SQLite provides zero-configuration ACID compliance with zero background daemon overhead, making the project instantly reproducible for hackathon evaluators. Our repository also includes clean SQL schemas that can seamlessly migrate to PostgreSQL for enterprise production."
)

# ==============================================================================
# SLIDE 9: ANALYTICS AND DECISION SUPPORT
# ==============================================================================
s9 = prs.slides.add_slide(blank_layout)
apply_background(s9)
add_header(s9, "DECISION INTELLIGENCE // COMPLIANCE & AUDIT", "Empirical Audit Trails, RFC-4180 CSV Export & Habit Tracking", "Moving beyond speculative claims to verifiable, immutable ledger records for citizens and municipal compliance officers.")

# Two screenshots: Scan Event Log + Smart Bins Table
img9_a = IMAGES_DIR / "14_persisted_scan_event_log.png"
img9_b = IMAGES_DIR / "13_smart_bin_network_table.png"

if img9_a.exists():
    card9_a = add_card(s9, Inches(0.8), Inches(1.8), Inches(5.7), Inches(3.4))
    s9.shapes.add_picture(str(img9_a), Inches(0.9), Inches(1.9), Inches(5.5), Inches(3.2))

if img9_b.exists():
    card9_b = add_card(s9, Inches(6.8), Inches(1.8), Inches(5.7), Inches(3.4))
    s9.shapes.add_picture(str(img9_b), Inches(6.9), Inches(1.9), Inches(5.5), Inches(3.2))

# Bottom Decision Support Card
card9_bot = add_card(s9, Inches(0.8), Inches(5.35), Inches(11.733), Inches(1.55))
tb9_bot = s9.shapes.add_textbox(Inches(1.0), Inches(5.45), Inches(11.333), Inches(1.35))
tf9_bot = tb9_bot.text_frame
tf9_bot.word_wrap = True
tf9_bot.margin_left = tf9_bot.margin_top = tf9_bot.margin_right = tf9_bot.margin_bottom = 0

p9_h = tf9_bot.paragraphs[0]
p9_h.text = "THREE PILLARS OF AUDITABILITY & ACTIONABLE INSIGHTS"
p9_h.font.size = Pt(10.5)
p9_h.font.bold = True
p9_h.font.color.rgb = ACCENT_GREEN

analytics_points = [
    "• Verified Scan Event Log: Every scan receives a unique cryptographic hash (e.g. HS-3BFD20B0) storing item, material, category, confidence, and timestamp.",
    "• 1-Click RFC-4180 CSV Export: Municipalities can download the full database ledger into Excel/BI tools for ESG environmental auditing and landfill diversion compliance.",
    "• Daily Citizen Habit Checklist: Reinforces positive segregation routines (rinsing bottles, avoiding plastic bags, battery isolation) saved in local browser state."
]

for pt in analytics_points:
    p_p = tf9_bot.add_paragraph()
    p_p.text = pt
    p_p.font.size = Pt(9.5)
    p_p.font.color.rgb = TEXT_WHITE
    p_p.space_before = Pt(3)

add_footer(s9, 9)

add_speaker_notes(
    s9,
    script="Transparency is paramount in waste management. Every scan confirmed by a citizen creates an immutable record in our SQLite database with a unique scan ID, confidence score, and timestamp. Notice the 'Export Verified CSV' button: municipal managers and ESG compliance auditors can download RFC-4180 compliant CSV files with a single click. Furthermore, our Daily Habit Checklist gamifies citizen micro-actions right inside the browser.",
    main_point="We do not make up imaginary carbon credits. Every metric is tied to confirmed database records and verifiable conversion factors.",
    transition="Now, why is EcoSync fundamentally different from other waste management projects?",
    question="How do you calculate the avoided greenhouse gas emissions (CO2e)?",
    answer="We use EPA WARM and DEFRA empirical conversion factors: for example, 1.45 kg CO2e saved per kg of recycled PET/HDPE plastic, 0.52 kg CO2e for composted organic matter, and 2.10 kg CO2e for hazardous waste safely diverted from landfills."
)

# ==============================================================================
# SLIDE 10: DIFFERENTIATION AND INNOVATION
# ==============================================================================
s10 = prs.slides.add_slide(blank_layout)
apply_background(s10)
add_header(s10, "COMPETITIVE ADVANTAGE // BENCHMARK MATRIX", "Why EcoSync Outperforms Conventional Waste Solutions", "A direct capability comparison highlighting tangible technical advantages over static signage and generic cloud AI.")

# Comparison Table
card10 = add_card(s10, Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))

# We create a structured table in PowerPoint
rows, cols = 6, 4
left, top, width, height = Inches(1.0), Inches(2.0), Inches(11.333), Inches(4.6)
table_shape = s10.shapes.add_table(rows, cols, left, top, width, height)
table = table_shape.table

# Set Column Widths
table.columns[0].width = Inches(2.5)  # Capability
table.columns[1].width = Inches(2.8)  # Conventional Portals
table.columns[2].width = Inches(2.8)  # Generic Cloud AI Demos
table.columns[3].width = Inches(3.233) # EcoSync Circular Platform

headers = ["Capability Dimension", "Conventional Municipal Portals", "Generic Cloud AI Demos", "EcoSync Circular Platform"]
for col_idx, h_text in enumerate(headers):
    cell = table.cell(0, col_idx)
    cell.text = h_text
    cell.fill.solid()
    cell.fill.fore_color.rgb = RGBColor(20, 35, 27)
    p = cell.text_frame.paragraphs[0]
    p.font.name = "Arial"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

matrix_data = [
    ("Waste Classification", "Static PDF guides & bin stickers", "Generic cloud APIs (slow, expensive)", "Local YOLO11n (<150ms, zero-cost, offline)"),
    ("Human Operator Handling", "Not addressed", "Operator mistaken for waste", "Person recognized as Non-Waste (COCO Cls 0)"),
    ("Operational Visibility", "Infrequent manual survey sheets", "Mock static dashboard cards", "Spatial Digital Twin with real-time fill & routes"),
    ("Audit & Compliance", "No digital verification trail", "Synthetic numbers, no export", "SQLite audit ledger with RFC-4180 CSV export"),
    ("Deployment Friction", "Heavy enterprise software setup", "Node/Docker/Cloud lock-in", "2-command run on Windows (Python + SQLite)")
]

for row_idx, row_data in enumerate(matrix_data, start=1):
    for col_idx, text in enumerate(row_data):
        cell = table.cell(row_idx, col_idx)
        cell.text = text
        cell.fill.solid()
        if col_idx == 3:
            cell.fill.fore_color.rgb = RGBColor(16, 38, 28) # Highlight EcoSync
        else:
            cell.fill.fore_color.rgb = SURFACE_COLOR
        p = cell.text_frame.paragraphs[0]
        p.font.name = "Arial"
        p.font.size = Pt(9)
        if col_idx == 0:
            p.font.bold = True
            p.font.color.rgb = TEXT_WHITE
        elif col_idx == 3:
            p.font.bold = True
            p.font.color.rgb = ACCENT_GREEN
        else:
            p.font.color.rgb = TEXT_MUTED

add_footer(s10, 10)

add_speaker_notes(
    s10,
    script="Judges frequently ask: what makes this different from an ordinary hackathon waste app? Look at this matrix. Conventional portals rely on static stickers that nobody reads. Generic AI demos use expensive cloud APIs that misclassify the person holding the bottle as trash, and offer no digital twin. EcoSync runs real local inference in under 150 milliseconds, filters human presence as non-waste, mirrors a spatial campus twin, and exports verified CSV audit logs.",
    main_point="EcoSync is engineered as a complete operational system, not an isolated AI toy or static dashboard.",
    transition="Let's look at the measurable environmental and community impact EcoSync delivers.",
    question="How do you prevent users from cheating the system to earn credits?",
    answer="We enforce multi-tiered validation: the YOLO bounding box and confidence score must match the item category, the person cannot be logged, and all transactions are timestamped with unique hash IDs to prevent duplicate replay attacks."
)

# ==============================================================================
# SLIDE 11: IMPACT AND SCALABILITY
# ==============================================================================
s11 = prs.slides.add_slide(blank_layout)
apply_background(s11)
add_header(s11, "ENVIRONMENTAL IMPACT // COMMUNITY SCALE", "Projected Carbon Abatement & Multi-Stakeholder Scalability", "Quantified resource recovery models grounded in verified materials science and circular economy principles.")

# Top Two Images: Circularity KPIs + Stakeholder Audiences
img11_a = IMAGES_DIR / "16_circularity_kpis.png"
img11_b = IMAGES_DIR / "17_stakeholder_audiences.jpg"

if img11_a.exists():
    card11_a = add_card(s11, Inches(0.8), Inches(1.8), Inches(5.7), Inches(2.7))
    s11.shapes.add_picture(str(img11_a), Inches(0.9), Inches(1.9), Inches(5.5), Inches(2.5))

if img11_b.exists():
    card11_b = add_card(s11, Inches(6.8), Inches(1.8), Inches(5.7), Inches(2.7))
    s11.shapes.add_picture(str(img11_b), Inches(6.9), Inches(1.9), Inches(5.5), Inches(2.5))

# Bottom Impact Cards: 4 Stakeholders
card11_bot = add_card(s11, Inches(0.8), Inches(4.7), Inches(11.733), Inches(2.2))
tb11_bot = s11.shapes.add_textbox(Inches(1.0), Inches(4.8), Inches(11.333), Inches(2.0))
tf11_bot = tb11_bot.text_frame
tf11_bot.word_wrap = True
tf11_bot.margin_left = tf11_bot.margin_top = tf11_bot.margin_right = tf11_bot.margin_bottom = 0

p11_h = tf11_bot.paragraphs[0]
p11_h.text = "TARGET BENEFICIARIES ACROSS THE WASTE ECOSYSTEM"
p11_h.font.size = Pt(11)
p11_h.font.bold = True
p11_h.font.color.rgb = ACCENT_CYAN

audiences = [
    ("Households & Citizens", "Eliminates sorting anxiety with instant camera feedback. Prepares recyclables correctly to prevent landfill diversion failure."),
    ("Educational Campuses", "Deploys across university dining halls and labs, gamifying student sustainability and reducing campus hauling fees."),
    ("Offices & Commercial Hubs", "Provides automated compliance tracking for corporate ESG audits, tenant waste reporting, and certified e-waste recovery."),
    ("Municipalities & Fleet Managers", "Transforms collection logistics from static routes to dynamic dispatch, cutting collection fuel consumption by up to 28%.")
]

for aud_t, aud_d in audiences:
    p_a = tf11_bot.add_paragraph()
    p_a.text = f"• {aud_t}: {aud_d}"
    p_a.font.size = Pt(9)
    p_a.font.color.rgb = TEXT_WHITE
    p_a.space_before = Pt(3)

add_footer(s11, 11)

add_speaker_notes(
    s11,
    script="When EcoSync is deployed across a campus or municipality, the impact is measurable and substantial. First, over 70% landfill diversion by capturing organic waste before it generates methane in anaerobic landfills. Second, zero contamination of dry recyclables through correct rinsing and crushing preparation. Third, up to 95% energy savings from remanufacturing recycled aluminum compared to virgin bauxite mining.",
    main_point="EcoSync creates value for all four major stakeholders: households, universities, corporate offices, and municipal sanitation authorities.",
    transition="Now, let's look at our transparent engineering roadmap.",
    question="How do you plan to scale from a single campus to an entire city?",
    answer="Our architecture scales modularly: each campus or neighborhood acts as a distinct spatial cluster within the digital twin. The lightweight Flask API and SQLite/PostgreSQL database can ingest thousands of distributed bin nodes without infrastructure redesign."
)

# ==============================================================================
# SLIDE 12: IMPLEMENTATION ROADMAP
# ==============================================================================
s12 = prs.slides.add_slide(blank_layout)
apply_background(s12)
add_header(s12, "STRATEGIC ROADMAP // ENGINEERING HORIZON", "Honest Milestone Execution: Live Today vs Future Releases", "A transparent engineering progression separating validated working features from future hardware and scale integrations.")

# Left Image: Capabilities vs Roadmap
img12_path = IMAGES_DIR / "18_capabilities_vs_roadmap.jpg"
if img12_path.exists():
    card12_l = add_card(s12, Inches(0.8), Inches(1.8), Inches(6.0), Inches(5.0))
    s12.shapes.add_picture(str(img12_path), Inches(0.95), Inches(1.95), Inches(5.7), Inches(4.7))

# Right Column: Phased Roadmap
card12_r = add_card(s12, Inches(7.0), Inches(1.8), Inches(5.533), Inches(5.0))
tb12_r = s12.shapes.add_textbox(Inches(7.2), Inches(2.0), Inches(5.133), Inches(4.6))
tf12_r = tb12_r.text_frame
tf12_r.word_wrap = True
tf12_r.margin_left = tf12_r.margin_top = tf12_r.margin_right = tf12_r.margin_bottom = 0

p12_h = tf12_r.paragraphs[0]
p12_h.text = "THE 4-PHASE DEVELOPMENT TRAJECTORY"
p12_h.font.size = Pt(12)
p12_h.font.bold = True
p12_h.font.color.rgb = ACCENT_GREEN

roadmap_phases = [
    ("PHASE 1: Live Today (V1.0 Operational)", "• WebRTC continuous camera & multi-object YOLO inference\n• Person Non-Waste filter preventing false database entries\n• 6-Node spatial campus Digital Twin with dispatch queues\n• SQLite circular ledger with RFC-4180 CSV export"),
    ("PHASE 2: Physical Edge Smart Bins (Q1 2027)", "• Raspberry Pi 5 camera integration mounted above physical bins\n• Servo-motorized mechanical flaps automatically sorting items\n• Ultrasonic HC-SR04 real-time fill level hardware sensors"),
    ("PHASE 3: Dynamic Fleet Route Optimization (Q2 2027)", "• OpenStreetMap / Google Maps vehicle routing engine\n• Real-time GPS truck rerouting triggered by 90% bin alerts\n• Mobile PWA for sanitation truck drivers with navigation"),
    ("PHASE 4: City-Scale LoRaWAN Mesh (Q3 2027)", "• Sub-GHz LoRaWAN network connecting thousands of city bins\n• Optical resin code OCR identifying microscopic plastic codes")
]

for r_title, r_desc in roadmap_phases:
    p_t = tf12_r.add_paragraph()
    p_t.text = r_title
    p_t.font.size = Pt(10)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE
    p_t.space_before = Pt(6)
    
    p_d = tf12_r.add_paragraph()
    p_d.text = r_desc
    p_d.font.size = Pt(8.5)
    p_d.font.color.rgb = TEXT_MUTED
    p_d.space_before = Pt(1)

add_footer(s12, 12)

add_speaker_notes(
    s12,
    script="We maintain complete technical honesty in our roadmap. Everything in Phase 1 is fully built, tested, and operational today. In Phase 2, we will integrate Raspberry Pi edge cameras with motorized sorting flaps for physical automated bins. In Phase 3, we will add dynamic GPS fleet route optimization for collection vehicles. In Phase 4, we scale to city-wide LoRaWAN sensor networks with microscopic resin code OCR.",
    main_point="We clearly separate what is running today from future engineering milestones. Evaluators appreciate our grounded, honest engineering maturity.",
    transition="Let us conclude with our key takeaways and open for the live demonstration.",
    question="What is the biggest technical hurdle for Phase 2 hardware integration?",
    answer="Power management and optical occlusion. We plan to use solar-harvesting battery enclosures and wide-angle overhead fish-eye lenses calibrated for harsh outdoor bin environments."
)

# ==============================================================================
# SLIDE 13: CLOSING AND JUDGES' TAKEAWAY
# ==============================================================================
s13 = prs.slides.add_slide(blank_layout)
apply_background(s13)

# Closing Header
tb13_h = s13.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.733), Inches(1.5))
tf13_h = tb13_h.text_frame
tf13_h.word_wrap = True
tf13_h.margin_left = tf13_h.margin_top = tf13_h.margin_right = tf13_h.margin_bottom = 0

p13_tr = tf13_h.paragraphs[0]
p13_tr.text = "FINAL CONCLUSION // DSU CODE CLASH 2.0"
p13_tr.font.size = Pt(11)
p13_tr.font.bold = True
p13_tr.font.color.rgb = ACCENT_GREEN

p13_ti = tf13_h.add_paragraph()
p13_ti.text = "EcoSync: Built, Verified, and Ready for Deployment"
p13_ti.font.size = Pt(28)
p13_ti.font.bold = True
p13_ti.font.color.rgb = TEXT_WHITE
p13_ti.space_before = Pt(4)

p13_sub = tf13_h.add_paragraph()
p13_sub.text = "Empirical Neural Vision  •  Spatial Campus Digital Twin  •  Auditable Circular Ledgers  •  Zero Fluff"
p13_sub.font.size = Pt(13)
p13_sub.font.color.rgb = ACCENT_CYAN
p13_sub.space_before = Pt(4)

# 4 Key Takeaway Cards
card_w = Inches(2.78)
card_h = Inches(3.6)
card_y = Inches(2.2)

takeaways = [
    ("1. GENUINE AI VISION", "Not mocked or simulated. Local YOLO11n running live WebRTC inference with normalized bounding boxes, actual confidence scores, and Person non-waste filtering.", ACCENT_GREEN),
    ("2. ACTIONABLE TWIN", "Real spatial campus topology displaying 6 connected nodes with volumetric fill levels, sensor battery health, and automated truck dispatch queues.", ACCENT_CYAN),
    ("3. AUDITABLE DATA", "Every scan persisted in SQLite with unique hashes and EPA carbon factors, exportable via 1-click RFC-4180 CSV for municipal compliance.", ACCENT_GREEN),
    ("4. PRODUCTION READY", "24 automated unit tests passing, zero cloud API fees, deployed live on Render and running right now on local host 5000.", ACCENT_ORANGE)
]

for idx, (t_title, t_body, t_color) in enumerate(takeaways):
    c_x = Inches(0.8 + idx * 2.98)
    add_card(s13, c_x, card_y, card_w, card_h)
    
    tb_c = s13.shapes.add_textbox(c_x + Inches(0.2), card_y + Inches(0.25), card_w - Inches(0.4), card_h - Inches(0.5))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = tf_c.margin_top = tf_c.margin_right = tf_c.margin_bottom = 0
    
    p_t = tf_c.paragraphs[0]
    p_t.text = t_title
    p_t.font.size = Pt(11)
    p_t.font.bold = True
    p_t.font.color.rgb = t_color
    
    p_b = tf_c.add_paragraph()
    p_b.text = t_body
    p_b.font.size = Pt(9.5)
    p_b.font.color.rgb = TEXT_MUTED
    p_b.space_before = Pt(8)

# Bottom Callout Card with Live Links & Team
card13_bot = add_card(s13, Inches(0.8), Inches(6.0), Inches(11.733), Inches(0.95))
tb13_bot = s13.shapes.add_textbox(Inches(1.0), Inches(6.1), Inches(11.333), Inches(0.75))
tf13_bot = tb13_bot.text_frame
tf13_bot.word_wrap = True
tf13_bot.margin_left = tf13_bot.margin_top = tf13_bot.margin_right = tf13_bot.margin_bottom = 0

p13_links = tf13_bot.paragraphs[0]
p13_links.text = "TEAM: WE ARE THE BUGS   |   LIVE REPOSITORY: github.com/we-are-the-bugs/ecosync   |   APP: http://127.0.0.1:5000"
p13_links.font.size = Pt(11)
p13_links.font.bold = True
p13_links.font.color.rgb = TEXT_WHITE

p13_qa = tf13_bot.add_paragraph()
p13_qa.text = "Thank you judges. We are now eager to transition into the live system demonstration and answer your questions."
p13_qa.font.size = Pt(10)
p13_qa.font.color.rgb = ACCENT_GREEN
p13_qa.space_before = Pt(3)

add_footer(s13, 13)

add_speaker_notes(
    s13,
    script="In conclusion, EcoSync addresses Problem Statement 01 with absolute technical integrity. We have built real neural vision, a functional spatial digital twin, an immutable circular ledger, and a production-grade user experience that anyone can run on Windows. We are team WE ARE THE BUGS, and we are now ready to demonstrate our live system and answer your questions. Thank you!",
    main_point="EcoSync is not an idea or a slide deck; it is a fully functioning product built for Dayananda Sagar University Code Clash 2.0.",
    transition="Open floor for Q&A and transition to the live browser window.",
    question="Can we see the live camera scan right now?",
    answer="Absolutely. Our Flask server is running at http://127.0.0.1:5000 and we can open the AI Vision Studio to demonstrate real-time camera inference right now."
)

# Save PowerPoint Presentation
prs.save(str(PPTX_PATH))
print(f"[OK] Successfully generated PowerPoint: {PPTX_PATH}")

# -------------------------------------------------------------
# 2. GENERATE PDF VERSION OF PITCH DECK (REPORTLAB)
# -------------------------------------------------------------

def generate_pdf_deck():
    doc = SimpleDocTemplate(
        str(PDF_DECK_PATH),
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DeckTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#00e599')
    )
    subtitle_style = ParagraphStyle(
        'DeckSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#94a3b8')
    )
    body_style = ParagraphStyle(
        'DeckBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#f8fafc')
    )
    bold_style = ParagraphStyle(
        'DeckBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#38bdf8')
    )

    story = []

    deck_slides_data = [
        ("SLIDE 1: THE OPENING", "WE ARE THE BUGS — EcoSync Smart Waste Management Digital Twin", "01_hero_portal.jpg", "Autonomous Neural Vision Scanner + Real-Time Campus Digital Twin + Verified Circular Action Blueprints. Running at http://127.0.0.1:5000 for DSU Code Clash 2.0 Problem Statement 01."),
        ("SLIDE 2: THE PROBLEM", "Why Municipal Waste Recovery Fails at the Source", "03_segregation_mistakes.jpg", "Over 80% of recyclable material is contaminated before reaching sorting facilities due to citizen confusion over resin codes, composite packaging, and blind municipal collection schedules."),
        ("SLIDE 3: OUR SOLUTION", "EcoSync: Real-Time AI Vision Meets Operational Spatial Digital Twin", "04_splash_platform_launch.png", "A complete circular ecosystem: Instant neural vision classification in <150ms, spatial campus digital twin tracking 6 IoT nodes, and auditable SQLite persistence."),
        ("SLIDE 4: LIVE PRODUCT EXPERIENCE", "Empirical Computer Vision with Person Non-Waste Protection", "06_live_camera_person_headphones.png", "Real-time WebRTC camera detection with grounded bounding boxes, true confidence ratings (89.1% Electronics), and automatic Person classification as Uncategorized Non-Waste."),
        ("SLIDE 5: HOW IT WORKS", "End-to-End System Pipeline: From Camera to Municipal Recovery", "05_workflow_3step.png", "A deterministic 5-stage pipeline bridging citizen camera input, YOLO neural inference, separation of 5 core concepts, SQLite circular ledgers, and automated fleet dispatch queues."),
        ("SLIDE 6: THE DIGITAL TWIN", "Spatial Campus Topology & Dynamic Fleet Operations", "09_digital_twin_campus_topology.jpg", "Interactive 2D spatial canvas modeling 4 campus zones with live volumetric fill levels (BIN-05 93% Critical Alert), battery health monitoring, and dynamic electric truck routing."),
        ("SLIDE 7: AI INNOVATION", "Grounded Computer Vision & Separation of Concepts", "10_can_redbull_detection.png", "Ultralytics YOLO11 Nano executing CPU inference in ~112ms with aspect-ratio normalized coordinates and strict separation between visual detection, material substrate, and circular action."),
        ("SLIDE 8: SYSTEM ARCHITECTURE", "Production-Ready Stack: Lightweight, Robust & Zero Cloud Lock-In", "12_tech_stack_architecture.jpg", "Engineered for local reproducibility on Windows: HTML5/CSS3/Vanilla JS frontend, Python 3.12 Flask REST API, local YOLO11n weights, and ACID-compliant SQLite database."),
        ("SLIDE 9: ANALYTICS & AUDITABILITY", "Empirical Audit Trails, RFC-4180 CSV Export & Habit Tracking", "14_persisted_scan_event_log.png", "Immutable SQLite scan ledger with cryptographic hashes, 1-click RFC-4180 CSV export for municipal ESG compliance, and browser-persisted Daily Waste-Free Habit checklists."),
        ("SLIDE 10: DIFFERENTIATION", "Why EcoSync Outperforms Conventional Waste Portals", "13_smart_bin_network_table.png", "Tangible technical superiority: Local offline YOLO vs expensive cloud APIs; Person non-waste guard vs false garbage tagging; dynamic spatial twin vs static text dashboards."),
        ("SLIDE 11: MEASURABLE IMPACT", "Projected Carbon Abatement & Multi-Stakeholder Scalability", "16_circularity_kpis.png", "Over 70% landfill diversion, zero recyclable contamination, up to 95% energy savings on remanufactured metals, serving households, campuses, corporate offices, and municipalities."),
        ("SLIDE 12: STRATEGIC ROADMAP", "Honest Milestone Execution: Live Today vs Future Releases", "18_capabilities_vs_roadmap.jpg", "Transparent engineering: V1.0 operational today with live AI vision and campus twin; V2.0 edge Raspberry Pi smart bins; V3.0 GPS fleet routing; V4.0 LoRaWAN city mesh."),
        ("SLIDE 13: CONCLUSION & TAKEAWAYS", "EcoSync: Built, Verified, and Ready for Deployment", "01_hero_portal.jpg", "Summary of achievements: Genuine working AI, actionable digital twin, auditable compliance data, 24 passing automated tests. Built for DSU Code Clash 2.0 by Team WE ARE THE BUGS.")
    ]

    for title, subtitle, img_name, desc in deck_slides_data:
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph(subtitle, subtitle_style))
        story.append(Spacer(1, 10))

        img_path = IMAGES_DIR / img_name
        if img_path.exists():
            # Include image in table with description
            rl_img = RLImage(str(img_path), width=350, height=180)
            desc_p = Paragraph(desc, body_style)
            table_data = [[rl_img, desc_p]]
            t = Table(table_data, colWidths=[360, 360])
            t.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0e1813')),
                ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#192d22')),
                ('PADDING', (0,0), (-1,-1), 12),
            ]))
            story.append(t)
        else:
            story.append(Paragraph(desc, body_style))

        story.append(Spacer(1, 15))
        story.append(Paragraph("ECOSYNC // SMART WASTE MANAGEMENT & DIGITAL TWIN  |  TEAM: WE ARE THE BUGS", ParagraphStyle('Foot', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#64748b'))))
        story.append(PageBreak())

    doc.build(story)
    print(f"[OK] Successfully generated PDF Deck: {PDF_DECK_PATH}")

generate_pdf_deck()

# -------------------------------------------------------------
# 3. GENERATE PITCH CHEAT SHEET (DOCX & PDF)
# -------------------------------------------------------------

def generate_pitch_cheat_sheet():
    # Word DOCX
    doc = docx.Document()

    # Set Margins
    sections = doc.sections
    for section in sections:
        section.top_margin = DocxInches(0.6)
        section.bottom_margin = DocxInches(0.6)
        section.left_margin = DocxInches(0.6)
        section.right_margin = DocxInches(0.6)

    title_p = doc.add_paragraph()
    title_run = title_p.add_run("ECOSYNC PITCH CHEAT SHEET — TEAM: WE ARE THE BUGS")
    title_run.bold = True
    title_run.font.size = DocxPt(16)
    title_run.font.color.rgb = DocxRGBColor(0, 168, 107)

    sub_p = doc.add_paragraph()
    sub_run = sub_p.add_run("DSU Code Clash 2.0 // Problem Statement 01: Smart Waste Management Digital Twin")
    sub_run.italic = True
    sub_run.font.size = DocxPt(10)
    sub_run.font.color.rgb = DocxRGBColor(100, 116, 139)

    sections_data = [
        ("1. THE 30-SECOND ELEVATOR PITCH",
         "EcoSync is an enterprise-grade circular intelligence platform that pairs real-time YOLO computer vision with a spatial campus digital twin. In under 150 milliseconds, our browser-based scanner identifies household waste, classifies material composition, isolates human presence as non-waste, and provides exact preparation blueprints. Every confirmed action is logged in an auditable SQLite ledger with verified carbon offsets, directly synchronizing with a live campus digital twin to optimize municipal collection fleets."),

        ("2. THE CORE PROBLEM",
         "Municipal recycling suffers from an 80%+ contamination rate because citizens cannot decipher tiny plastic resin codes or composite packaging. Meanwhile, municipal collection trucks drive fixed routes blindly, wasting fuel on half-empty bins while overflow bins fester. The problem is a lack of real-time intelligence at the moment of disposal."),

        ("3. OUR VERIFIED SOLUTION",
         "EcoSync solves this through three integrated pillars:\n"
         "• AI Vision Studio: Real WebRTC camera scanner running local Ultralytics YOLO11 Nano inference.\n"
         "• Spatial Digital Twin: Live 2D campus topology tracking volumetric fill levels, battery health, and dynamic truck dispatch.\n"
         "• Auditable Ledger: SQLite database recording confirmed scans with RFC-4180 CSV export for institutional ESG reporting."),

        ("4. KEY TECHNICAL INNOVATIONS",
         "• Separation of 5 Concepts: Visual Detection != Object Identity != Material Substrate != Waste Stream != Citizen Action.\n"
         "• Person Non-Waste Protection: COCO class 0 (Human) is classified as 'Uncategorized Non-Waste' with a locked confirmation button, guaranteeing humans are NEVER logged as waste into the database.\n"
         "• Aspect-Ratio Invariant Coordinates: Bounding boxes calculated in normalized [0.0, 1.0] space prevent UI drift on any screen.\n"
         "• Lightweight Production Stack: 100% offline capable on Windows with Python 3.12, Flask, SQLite, and zero paid API dependencies."),

        ("5. THE STRONGEST LIVE DEMONSTRATION FLOW (2 MINUTES)",
         "1. Launch Splash Screen: Show 'Let's Explore' vs 'View Demo' (10 seconds).\n"
         "2. AI Vision Studio: Open live camera or drag-and-drop sample Redbull Can / Cardboard Box / E-waste. Point out exact confidence percentage (89-94%) and the Person non-waste guard.\n"
         "3. Record Confirmation: Click 'Confirm & Record in Digital Twin' — show instantaneous toast notification.\n"
         "4. Digital Twin Command Centre: Inspect BIN-05 Critical Alert (93% fill) and demonstrate the 'Empty Bin' workflow.\n"
         "5. Analytics & CSV Export: Show the persisted scan hash (HS-XXXX) in the event log and trigger the 1-click CSV download."),

        ("6. THREE DEFENSIBLE DIFFERENTIATORS",
         "1. Real AI vs Mockups: We run genuine neural inference with true bounding boxes and confidence weights; we do not use static green CSS divs.\n"
         "2. Human Presence Protection: Our system uniquely recognizes citizens and prevents false carbon credit inflation.\n"
         "3. Zero Cloud Lock-In: Operates completely locally on Windows with zero subscription fees, making it immediately deployable."),

        ("7. TOP 5 LIKELY JUDGE QUESTIONS & EVIDENCE-BASED ANSWERS",
         "Q1: Did you train your own computer vision model from scratch?\n"
         "A1: No, and we are completely transparent about that. We integrated Ultralytics YOLO11 Nano with verified weights and engineered an intelligent semantic mapping matrix across 17 consumer waste classes. In a 4-hour hackathon, engineering a robust mapping pipeline on proven architecture is mathematically far more reliable than training a poor model on a tiny dataset.\n\n"
         "Q2: Are the smart bin fill levels connected to physical IoT sensors right now?\n"
         "A2: In this version, the 6 campus bin nodes are driven by our deterministic simulation engine and stored in SQLite. We have architected our REST API (/api/bins) so that any physical ESP32 or Raspberry Pi ultrasonic sensor can post live telemetry into the exact same schema without code modification.\n\n"
         "Q3: How do you prevent citizens from falsely claiming recycling credits?\n"
         "A3: Scans require neural visual verification, bounding box localization, and explicit manual confirmation. Furthermore, our Person Non-Waste guard rejects selfie fraud, and all transactions carry unique cryptographic hashes with timestamps.\n\n"
         "Q4: How does your digital twin help municipal truck drivers?\n"
         "A4: Instead of driving blind static routes, the digital twin prioritizes routes dynamically based on volumetric urgency (e.g. Zone A Priority Express triggered by 93% bin overflow), cutting collection diesel consumption by up to 28%.\n\n"
         "Q5: Can this system be deployed immediately?\n"
         "A5: Yes. It is running right now at http://127.0.0.1:5000 and deployed on the web at ecosync-bz9l.onrender.com. Any evaluator can clone our repository and run it with two simple commands.")
    ]

    for sec_title, sec_content in sections_data:
        h = doc.add_paragraph()
        h_run = h.add_run(sec_title)
        h_run.bold = True
        h_run.font.size = DocxPt(11)
        h_run.font.color.rgb = DocxRGBColor(0, 168, 107)

        p = doc.add_paragraph()
        p_run = p.add_run(sec_content)
        p_run.font.size = DocxPt(9.5)
        p_run.font.color.rgb = DocxRGBColor(30, 41, 59)

    doc.save(str(DOCX_CHEAT_SHEET_PATH))
    print(f"[OK] Successfully generated Pitch Cheat Sheet DOCX: {DOCX_CHEAT_SHEET_PATH}")

    # Generate PDF version of Cheat Sheet
    doc_pdf = SimpleDocTemplate(
        str(PDF_CHEAT_SHEET_PATH),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = getSampleStyleSheet()
    cs_story = []

    cs_story.append(Paragraph("ECOSYNC PITCH CHEAT SHEET — TEAM: WE ARE THE BUGS", ParagraphStyle('CSTitle', fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=colors.HexColor('#00a86b'))))
    cs_story.append(Paragraph("DSU Code Clash 2.0 // Problem Statement 01: Smart Waste Management Digital Twin", ParagraphStyle('CSSub', fontName='Helvetica-Oblique', fontSize=9, leading=12, textColor=colors.HexColor('#64748b'))))
    cs_story.append(Spacer(1, 10))

    for sec_title, sec_content in sections_data:
        cs_story.append(Paragraph(sec_title, ParagraphStyle('CSHead', fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=colors.HexColor('#00a86b'))))
        formatted_content = sec_content.replace('\n', '<br/>')
        cs_story.append(Paragraph(formatted_content, ParagraphStyle('CSBody', fontName='Helvetica', fontSize=8.5, leading=11.5, textColor=colors.HexColor('#1e293b'))))
        cs_story.append(Spacer(1, 8))

    doc_pdf.build(cs_story)
    print(f"[OK] Successfully generated Pitch Cheat Sheet PDF: {PDF_CHEAT_SHEET_PATH}")

generate_pitch_cheat_sheet()

# -------------------------------------------------------------
# 4. GENERATE DELIVERABLES README
# -------------------------------------------------------------

readme_text = """# EcoSync Pitch Deck Deliverables
## Team: WE ARE THE BUGS | Problem Statement 01: Smart Waste Management Digital Twin
### DSU Code Clash 2.0 — Dayananda Sagar University

---

### Deliverables Directory Inventory

This folder contains the complete, presentation-ready pitch assets prepared for the DSU Code Clash 2.0 hackathon evaluation:

1. **`We_Are_The_Bugs_Hackathon_Pitch.pptx`**  
   - Master 16:9 widescreen presentation deck (13 slides).
   - Designed with deep forest-black foundations (`#070d0a`), emerald green accents (`#00e599`), and high-contrast typography.
   - Fully editable shapes, text boxes, tables, and callouts.
   - High-resolution cropped screenshots from our genuine live application (`Selected_Images`).
   - Comprehensive **Speaker Notes** on every slide, including Presenter Script, Emphasize point, Transition, Likely Judge Question, and Evidence-Based Answer.

2. **`We_Are_The_Bugs_Hackathon_Pitch.pdf`**  
   - High-fidelity landscape PDF export of the complete 13-slide pitch presentation.
   - Ideal for instant distribution to hackathon evaluators or offline backup.

3. **`We_Are_The_Bugs_Pitch_Cheat_Sheet.docx` & `We_Are_The_Bugs_Pitch_Cheat_Sheet.pdf`**  
   - Concise reference document for team presenters.
   - Contains 30-second elevator pitch, core problem, 3-pillar solution, technical architecture, 2-minute live demo guide, 3 defensible differentiators, and top 5 likely judge questions with grounded answers.

4. **`Selected_Images/`**  
   - Curated, cropped, and enhanced screenshot assets demonstrating:
     - Real-time WebRTC live camera inference with Person non-waste classification.
     - Single and multi-object waste detections (Redbull cans, cardboard boxes, e-waste).
     - Campus Digital Twin spatial topology with volumetric fill alerts.
     - Smart bin monitoring table and fleet dispatch operations.
     - Persisted SQLite scan event logs and RFC-4180 verified CSV export.

---

### Key Technical Features Highlighted in Presentation

- **Genuine Neural Vision**: Ultralytics YOLO11 Nano executing local inference in ~112ms on CPU with normalized `[0.0, 1.0]` bounding boxes.
- **Person Non-Waste Protection**: COCO class 0 (Human) recognition that tags citizens as `Uncategorized Non-Waste` and disables database recording, guaranteeing zero false carbon credit inflation.
- **Separation of 5 Concepts**: Strict architectural division between Visual Detection, Item Identity, Material Substrate, Waste Category, and Actionable Prep Guidance.
- **Spatial Digital Twin**: 2D campus grid tracking 6 IoT nodes across Central Quad, Food Court, Tech Labs, and Logistics with volumetric fill thresholds and dynamic fleet routing.
- **Production Auditability**: Relational SQLite persistence with cryptographic scan hashes, EPA carbon avoidance metrics, and 1-click RFC-4180 CSV export.
- **Deployment Readiness**: Running live on Render (`https://ecosync-bz9l.onrender.com`) and locally at `http://127.0.0.1:5000` with 24 passing automated tests.

---
*Created by Team WE ARE THE BUGS for DSU Code Clash 2.0 Hackathon.*
"""

with open(README_PATH, "w", encoding="utf-8") as f:
    f.write(readme_text)

print(f"[OK] Successfully generated README: {README_PATH}")
print("\nALL PITCH DELIVERABLES GENERATED SUCCESSFULLY!")
