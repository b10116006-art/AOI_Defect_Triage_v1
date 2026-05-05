# AOI Defect Triage v1

AI-driven defect classification and detection system for semiconductor manufacturing.

This repo is the **Vision Layer** of a larger manufacturing AI architecture:

> image → defect classification → structured JSON → MES process context → LLM reasoning → engineering decision

## Key Results

### Track A: Wafer Map Classification (WM-811K)

| Metric | Value |
|--------|-------|
| Dataset | [WM-811K](https://www.kaggle.com/datasets/qingyi/wm811k-wafer-map) (810K+ raw records) |
| Usable samples | **172,950** (recovered from raw data) |
| CNN Test Accuracy | **89.28%** |
| CNN Val Accuracy | **96.40%** |
| Classes | 9 (Center, Donut, Edge-Loc, Edge-Ring, Loc, Near-full, Random, Scratch, none) |

### Track B: AOI Camera Defect Detection (Roboflow Wafer Defect)

| Metric | Value |
|--------|-------|
| Dataset | [Roboflow Wafer Defect](https://universe.roboflow.com/wafer-irhuv/wafer-defect-rv1vx) (4,532 images) |
| Model | YOLOv8 |
| mAP50 | **0.715** |
| Classes | 7 (Particle, Scratch, Coating Bad, Block Etch, SEZ Burnt, PIQ Particle, PO Contamination) |

### Why Two Tracks?

Track A and B operate on **different physical layers** of a real fab:

- **Track A** consumes wafer-level binary maps (die pass/fail patterns)
- **Track B** consumes camera images of physical surfaces (real defect localization)

They share a JSON contract boundary, never shared pixels or models.

## Architecture

```
[Track A: Wafer Map]             [Track B: AOI Camera]
WM-811K 810K records             Roboflow 4,532 images
        |                                |
  preprocessing                    YOLO training
  172,950 samples                  7-class detection
        |                                |
  CNN classifier                   YOLOv8 model
  9-class, 89.28%                  mAP50=0.715
        |                                |
        +---------- JSON contract -------+
                         |
                   FastAPI Service
                   POST /predict
                         |
              Structured JSON Output
              (for downstream MES integration)
```

## Project Structure

```
src/
  prepare_data.py       # WM-811K preprocessing + label recovery
  train.py              # CNN training pipeline
  evaluate.py           # Test evaluation + confusion matrix
  infer.py              # Single-image inference (CLI)
  api.py                # FastAPI inference service (POST /predict)
  b_yolo/               # Track B: YOLO detection pipeline
    api.py              # Track B FastAPI inference service
    train.py            # YOLO training on Roboflow dataset
    predict.py          # YOLO prediction
    eval_smoke.py       # Evaluation smoke test
    prepare_roboflow_wafer.py
docs/
  core/                 # Roadmap, project state, integration blueprint
results/                # Evaluation reports + baseline metrics
tools/                  # Smoke test scripts
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run inference API
uvicorn src.api:app --host 0.0.0.0 --port 8000

# Test prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "<base64-encoded-png>"}'
```

## API Response Format

```json
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
  "model_version": "2026_03_29",
  "request_id": "uuid-string",
  "processing_time_ms": 8.47,
  "schema_version": "2.0"
}
```

## Development Status

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | CNN baseline + data pipeline (WM-811K) | Complete |
| Phase 2 | FastAPI inference service | Complete |
| Phase 3 | Detection feasibility on WM-811K | Validated: not feasible, moved to Track B |
| B-track | YOLO detection on Roboflow Wafer Defect | mAP50=0.715 achieved |
| B8.2 | Service hardening + weights config | Complete |
| B8.3 | Evaluation smoke loop + gold dataset | In progress (20-image baseline committed) |
| Phase 4 | Batch inference + production-style IO | Planned |
| Phase 5 | AOI → MES integration via JSON contract | Planned |

## Tech Stack

Python | PyTorch | FastAPI | YOLOv8 | scikit-learn | NumPy | Pandas

## Related Projects

- [mes-rag-assistant](https://github.com/b10116006-art/mes-rag-assistant) — RAG/LLM decision core for semiconductor manufacturing

## License

MIT
