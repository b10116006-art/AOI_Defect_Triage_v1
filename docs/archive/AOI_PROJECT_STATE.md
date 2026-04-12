# PROJECT_STATE.md — AOI_Defect_Triage_v1

_Last updated: 2026-04-06_

## 1. Project role
Independent Vision Layer subproject for AOI defect triage.
Standalone demo first, later optional integration with MES Copilot.

## 2. Current phase
Phase 1 — CNN classification baseline → **complete**
Phase 2 — FastAPI inference service → **complete**
Phase 3 — Detection feasibility validation → **validated; detection path on WM-811K deferred**
(See AOI_MASTER_ROADMAP.md §Phase 3 and §4.1 for the revised layered architecture.)

### Phase 1 completed items
- [x] Preprocessing complete — 172,950 labeled samples recovered from 811,457 total rows
- [x] Training complete — best val accuracy: **96.40%**
- [x] Evaluation complete — test accuracy: **89.28%**; confusion matrix and per-class report saved
- [x] Single-image inference complete — JSON output confirmed against locked contract format

## 3. Locked contract
The JSON contract between Vision Layer and MES Layer is fixed and must not be changed without explicit approval.

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
  "model_version": "2026_03_29"
}
```

## 4. Must preserve
- independence from MES runtime
- phase-by-phase demoability
- simple explainability for non-software-engineer operator
- minimal-diff development style
- WM-811K-based Phase 1 baseline scope

## 5. Must avoid
- touching MES API routes
- mixing AOI code into MES repo too early
- skipping phases
- over-designing Phase 1 infrastructure
- changing the locked JSON contract casually
- deciding Phase 2–5 details during Phase 1

## 6. Phase order
- Phase 1: CNN classification baseline
- Phase 2: FastAPI inference API
- Phase 3: YOLO / detection baseline  *(re-scoped: validated as not feasible on wafer maps; real detection belongs to AOI-camera layer)*
- Phase 4: LLM defect explanation
- Phase 5: Integration with MES Copilot

## 7. Approved planning direction for Phase 1
Dataset:
- WM-811K / LSWMD raw `.pkl` file
- keep raw file untouched under `data/raw/`

Planned outputs:
- processed image folders under `data/processed/`
- simple CNN baseline
- train / evaluate / single-image inference scripts
- saved model weights and result report

## 8. Immediate next step
Implement the minimal Phase 1 baseline files only:
- folder structure
- prepare_data.py
- train.py
- evaluate.py
- requirements.txt
- README_phase1.md

## 9. Validation rule
Phase 1 is not complete until:
- processed dataset exists
- training runs end-to-end
- validation/test metrics are recorded
- confusion matrix is saved
- model weights are saved
- README allows rerun by another person

## 10. Deferred on purpose
Do not decide yet:
- API design
- detection architecture choice
- LLM explanation design
- MES integration mechanics
- database schema
- deployment / containerization
- automation schedule
