# PROJECT_STATE.md — AOI_Defect_Triage_v1

_Last updated: 2026-04-11_

## 1. Project role
Independent Vision Layer subproject for AOI defect triage.

This repo is intentionally built as a standalone AOI / Vision Layer first:
- independently demoable
- independently testable
- easier to explain in interview / review
- safer to integrate later with AI MES Copilot and LLM / RAG layers

Future integration direction:
- AOI Vision Layer → AI MES Copilot → LLM / RAG decision layer
- but runtime-level coupling is intentionally deferred until later phases

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

### Phase 2 completed items
- [x] `src/api.py` created as minimal FastAPI inference service
- [x] `POST /predict` implemented
- [x] Phase 1 CLI inference behavior preserved
- [x] Locked AOI JSON contract preserved in original order
- [x] Only three API metadata fields appended at the end:
  - `request_id`
  - `processing_time_ms`
  - `schema_version`
- [x] invalid base64 / unreadable image request returns HTTP 400
- [x] PowerShell smoke test completed successfully
- [x] one-command API launcher created:
  - `tools/run_phase2_api_and_smoke.ps1`

## 3. Locked contract
The JSON contract between Vision Layer and downstream systems is fixed and must not be changed casually.

### Base contract
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

### Phase 2 response rule
Phase 2 keeps the base contract unchanged and only appends:
```json
{
  "request_id": "uuid-string",
  "processing_time_ms": 8.47,
  "schema_version": "v1"
}
```

## 4. Must preserve
- independence from MES runtime
- phase-by-phase demoability
- simple explainability for non-software-engineer operator
- minimal-diff development style
- WM-811K / LSWMD baseline scope
- locked JSON contract stability
- clear separation of implemented / validated / planned

## 5. Must avoid
- touching MES API routes from this repo
- mixing AOI code into MES repo too early
- skipping phases
- over-designing infrastructure too early
- changing the locked JSON contract casually
- rewriting Phase 1 training pipeline while building downstream interfaces
- treating Phase 2 as if it already equals full MES integration

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

Outputs:
- processed image folders under `data/processed/`
- simple CNN baseline
- train / evaluate / single-image inference scripts
- saved model weights and result report

## 8. Immediate next step
> **Update (post Phase 3 validation):** the original "YOLO / detection
> baseline" plan below was validated as not feasible on WM-811K (pixel=255
> = failing die, not defect region). The next real step is to define the
> separate **AOI-camera detection** dataset/layer per the layered
> architecture in AOI_MASTER_ROADMAP.md §4.1. The original plan is kept
> below for history.

**Phase 3 — YOLO / detection baseline** *(historical plan, re-scoped)*

Target:
- move from class-only prediction to real localization
- replace full-image placeholder bbox logic in future response mode
- keep Phase 2 API stable while building detection capability

Important sequencing note:
- If the Phase 2 PR is still OPEN on GitHub, merge that PR first
- Then refresh local `main`
- Then branch Phase 3 from the merged main
- Do not continue long-term development on a Phase 3 branch that is missing merged Phase 2 work

## 9. Validation rule
### Phase 1 validation
- processed dataset exists
- training runs end-to-end
- validation/test metrics are recorded
- confusion matrix is saved
- model weights are saved
- README allows rerun by another person

### Phase 2 validation
- API starts successfully
- `/predict` returns JSON successfully on valid request
- bad request returns HTTP 400
- smoke test covers both happy path and failure path
- contract fields remain stable and ordered

## 10. Deferred on purpose
Do not decide yet:
- final MES merge mechanics
- production database schema
- container / CI deployment strategy
- full LLM explanation design
- RAG knowledge design
- multi-service orchestration

## 11. Phase 2 observed validation evidence
Observed working behaviors:
- `py -3.11 -m uvicorn src.api:app --reload` starts successfully
- valid request returns all base contract fields plus:
  - `request_id`
  - `processing_time_ms`
  - `schema_version`
- invalid base64 request returns HTTP 400
- smoke test summary:
  - PASS: 2
  - FAIL: 0

## 12. Integration position
This repo is still an **independent AOI project**.

It is **not yet merged into AI MES runtime**.

Correct interpretation:
- AOI repo = Vision Layer prototype
- AI MES repo = process / equipment / decision runtime
- future integration should happen by contract consumption, not by prematurely mixing codebases
