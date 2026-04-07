# CLAUDE.md — AOI Defect Triage Copilot

## Project Role
You are assisting with AOI_Defect_Triage_v1, the Vision Layer of a semiconductor AI inspection system.
This is a standalone sub-system. It can demo independently and will integrate with AI MES Copilot later as Layer 1.

## Core Stack
- Python
- PyTorch
- CNN baseline first
- FastAPI inference API later
- Independent runtime from MES project

## JSON Contract (locked, never change without approval)
{
  "image_id": "img_0001",
  "machine_id": "AOI_01",
  "lot_id": "LOT123",
  "layer": "ILD",
  "timestamp": "2026-03-29T10:00:00Z",
  "defect_class": "scratch",
  "confidence": 0.93,
  "bbox": [120, 80, 240, 160],
  "ng_flag": true,
  "model_name": "cnn_baseline",
  "model_version": "2026_03_29"
}

## Development Phases (in order, no skipping)
- Phase 1: CNN classification baseline
- Phase 2: FastAPI inference API
- Phase 3: YOLO detection baseline
- Phase 4: LLM defect explanation
- Phase 5: Integration with MES Copilot

## Current Phase
Phase 1 — implementation ready

## Phase 1 Dataset
- Target dataset: WM-811K / LSWMD
- Raw `.pkl` file stays under `data/raw/`
- Raw file must remain untouched
- Processed train / val / test images are written under `data/processed/`

## Working Rules
1. Explain affected files before touching anything
2. Use plain language, not code-heavy explanations
3. Keep Phase 1 independent from MES runtime
4. Each phase must be independently demoable before moving on
5. Be explicit: implemented / validated / planned / uncertain
6. Keep minimal diffs
7. Do not assume MES runtime changes unless explicitly asked
8. For Phase 1, do not introduce API, database, UI, LLM, Docker, or integration logic
9. Save outputs, metrics, and reproducible run instructions clearly

## Preferred Phase 1 Files
- `src/prepare_data.py`
- `src/train.py`
- `src/evaluate.py`
- optional: `src/infer.py`
- `requirements.txt`
- `README_phase1.md`

## Validation Expectations
- processed dataset folders exist
- training runs end-to-end without crashing
- validation/test metrics are printed and saved
- confusion matrix is saved
- model weights are saved
- another person can rerun using README_phase1.md

## What not to decide yet
- Phase 2 API routes
- YOLO vs SSD details
- LLM explanation design
- MES integration details
- deployment / containerization
- scheduled automation
