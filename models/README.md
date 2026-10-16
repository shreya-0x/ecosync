# EcoSync Computer Vision Checkpoints

This directory houses the pretrained object detection checkpoints utilized by the EcoSync Waste Scanner.

## Default Checkpoint: `yolo11n.pt`
- **Architecture**: Ultralytics YOLO11 Nano Detection Checkpoint
- **Weight Size**: 5.61 MB (Compact, high-speed, CPU-friendly)
- **Classes**: 80 standard COCO detection categories
- **Execution Device**: Automatically detects CUDA (GPU) if available, defaults gracefully to CPU.

## Material Identification Matrix
EcoSync distinguishes between **raw detected object geometry** and **inferred candidate material**:
- `bottle` → Plastic (PET / HDPE) or Silicate Glass
- `can` → Metal (Aluminum UBC / Tinplate)
- `cup` → Plastic / Paper Composite
- `box` → Corrugated Cardboard (OCC Kraft)
- `book` → Cellulose Paper
- `cell phone` / `laptop` → Electronic Waste (WEEE)

## Replacing or Fine-Tuning Models
To substitute this checkpoint with custom fine-tuned weights:
1. Place your `.pt` file in this directory (e.g., `models/custom_waste_yolo.pt`).
2. Update the environment variable in `.env`:
   ```bash
   ECOSYNC_YOLO_MODEL=custom_waste_yolo.pt
   ```
3. Restart the Flask application. EcoSync will automatically load your custom weights, extract its class dictionary, and expose it via `/api/model-status`.
