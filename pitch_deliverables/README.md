# EcoSync Pitch Deck Deliverables
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
