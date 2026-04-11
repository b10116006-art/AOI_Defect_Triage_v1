# AOI Defect Triage v1 — Project Debug & Evolution Log

## Project Overview
Goal: Build an AI-powered wafer defect classification + triage system for semiconductor inspection.

Pipeline:
RAW (LSWMD.pkl)
→ parsing / cleaning
→ image dataset (PNG)
→ CNN baseline training
→ evaluation (confusion matrix)
→ single-image inference
→ FastAPI inference contract layer
→ later detection / explanation / MES integration

---

# Phase 1 — Data Engineering & Debug

## Issue 1 — All samples skipped (CRITICAL)

### Symptom
- labeled = 0
- skipped = 811,457

### Root cause
Dataset schema mismatch:
- `failureType` = `numpy.ndarray` (NOT string)
- `trianTestLabel` typo inside dataset

### Fix
- handle ndarray via `.flat[0]`
- fix column name
- handle empty arrays

### Result
- labeled recovered: 172,950 samples

---

# Phase 1 — Training Result

Model: `cnn_baseline_v1`  
Best Val Accuracy: **96.40%**

Interpretation:
- model converges correctly
- no training instability
- baseline is VALID

---

# Phase 1 — Evaluation Result (CRITICAL INSIGHT)

## Overall Test Accuracy
**89.28%**

⚠️ Gap vs Val (96.4 → 89.3)
→ slight overfitting OR dataset bias

## Per-Class Accuracy (KEY STORY)

GOOD:
- none → 91.52%
- Near-full → 90.53%

WEAK (critical defects):
- Center → 59.38%
- Donut → 61.64%
- Edge-Loc → 66.74%
- Edge-Ring → 66.07%
- Loc → 45.31%
- Scratch → 31.89%

## Core Insight
👉 Model is biased toward majority class (`none`)

👉 Real defect classes are HARDER:
- visually similar
- imbalanced dataset
- model confusion high

## Confusion Pattern
Typical mistakes:
- defect → predicted as `none`
- Edge-related defects confuse each other
- Scratch extremely hard

---

# Engineering Interpretation

This is NOT failure — this is REAL AI behavior:

1. Dataset imbalance problem
2. Feature similarity between defect types
3. Baseline CNN limitation

---

# Phase 1 Conclusion

✅ Data pipeline built  
✅ Parsing bug solved  
✅ CNN baseline trained  
✅ Evaluation done  
⚠️ Class imbalance & confusion identified

---

# Phase 1 — Inference Result

## Command confirmed working
```bash
py -3.11 src/infer.py --image "data\processed\test\Scratch\test_000561.png"
```

## JSON output (confirmed against locked contract)
```json
{
  "image_id": "img_0001",
  "machine_id": "AOI_01",
  "lot_id": "LOT_UNKNOWN",
  "layer": "UNKNOWN",
  "timestamp": "2026-04-09T15:36:46.880505+00:00",
  "defect_class": "none",
  "confidence": 0.9598,
  "bbox": [0, 0, 64, 64],
  "ng_flag": false,
  "model_name": "cnn_baseline",
  "model_version": "cnn_baseline_v1"
}
```

All locked contract fields present and populated correctly.  
`bbox` is full-image `[0, 0, 64, 64]` — Phase 1 placeholder. Real detection comes in Phase 3.

---

# Key Engineering Insights — Phase 1

## 1. Data engineering is the first failure point
The pipeline failed before a single training step because of schema assumptions.

## 2. High overall accuracy can hide per-class failure
89.28% test accuracy sounds acceptable, but minority defect classes remain weak.

## 3. Class imbalance requires structural solutions
Weighted loss helped, but did not fully solve minority-class confusion.

## 4. Baseline CNN is the right first step, not the final answer
The baseline proves the full pipeline works, and its weaknesses point directly to the next phase.

## 5. The JSON contract decouples model quality from system integration
Downstream systems can consume the AOI signal even while the model continues to improve.

---

# Phase 2 — Inference Contract Layer / API Service

## What Phase 2 means
Phase 2 does **not** mean MES integration.
It means turning the validated Phase 1 inference result into a callable HTTP service.

Interpretation:
- Phase 1 = model works
- Phase 2 = model can be consumed by another system

That is why Phase 2 is best understood as the AOI **Inference Contract Layer**.

## Phase 2 implementation
Implemented:
- minimal helper extraction from `src/infer.py`
- `src/api.py` created
- `POST /predict` endpoint added
- request accepts image payload + optional metadata
- response preserves locked AOI fields first
- three metadata fields appended:
  - `request_id`
  - `processing_time_ms`
  - `schema_version`

Explicitly NOT changed:
- no training code rewrite
- no dataset change
- no architecture redesign
- no MES runtime merge
- no LLM logic
- no Docker requirement

## Phase 2 validation result

### Service start
Confirmed working:
```bash
py -3.11 -m uvicorn src.api:app --reload
```

### Valid request test
Observed successful valid `/predict` response with:
- all original AOI contract fields
- correct field population
- appended Phase 2 metadata fields

### Bad request test
Invalid base64 request correctly returned:
- HTTP 400

This proves the API works on both happy path and controlled failure path.

---

# Smoke test result
PowerShell smoke testing completed with both cases:

### Test 1 — Happy Path
- valid Scratch image sent to `/predict`
- all 14 expected fields present
- PASS

### Test 2 — Bad Request
- invalid base64 sent intentionally
- API returned HTTP 400
- PASS

### Summary
- PASS: 2
- FAIL: 0

Conclusion:
👉 **Phase 2 API is healthy**

---

# Architectural meaning of Phase 2
Before Phase 2:
- the model could only be run manually or from CLI

After Phase 2:
- any downstream system can call AOI through HTTP
- AI MES can later consume it
- LLM / decision layer can later consume its structured output
- but the AOI repo still remains independently demoable

This separation is valuable:
- easier demo
- easier debugging
- easier interview explanation
- safer future integration

---

# Phase 3 — next
Phase 3 should now focus on:
- real detection / localization
- YOLO or detection baseline
- replacing placeholder bbox semantics with real detection outputs later

Key rule:
👉 do **not** collapse Phase 3 into immediate MES integration
