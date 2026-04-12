# AOI Defect Triage v1 — Project Debug & Evolution Log

## Project Overview
Goal: Build an AI-powered wafer defect classification + triage system.

Pipeline:
RAW (LSWMD.pkl)
→ parsing / cleaning
→ image dataset (PNG)
→ CNN baseline training
→ evaluation (confusion matrix)
→ inference API (next)

---

# Phase 1 — Data Engineering & Debug

## Issue 1 — All samples skipped (CRITICAL)

### Symptom
- labeled = 0
- skipped = 811,457

### Root cause
Dataset schema mismatch:
- failureType = numpy.ndarray (NOT string)
- trianTestLabel (typo in dataset)

### Fix
- handle ndarray via `.flat[0]`
- fix column name
- handle empty arrays

### Result
- labeled recovered: 172,950 samples

---

# Phase 1 — Training Result

Model: cnn_baseline_v1  
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

---

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

---

## Core Insight (VERY IMPORTANT FOR INTERVIEW)

👉 Model is biased toward majority class (`none`)

👉 Real defect classes are HARDER:
- visually similar
- imbalanced dataset
- model confusion high

---

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

👉 This is EXACTLY what interviewers want to see

---

# Phase 1 Conclusion

✅ Data pipeline built  
✅ Parsing bug solved  
✅ CNN baseline trained  
✅ Evaluation done  
⚠️ Class imbalance & confusion identified  

---

# Phase 2 Plan (Next Steps)

## Step 1 — Inference ✅ Complete
Run:
py -3.11 src/infer.py --image data/processed/test/Scratch/test_000123.png

Goal:
- input image
- output JSON
- simulate AOI system

---

## Step 2 — Improvement Ideas

Future upgrades:
- data augmentation
- focal loss / reweight
- ResNet backbone
- feature engineering

---

# Demo Story (IMPORTANT)

This project demonstrates:

1. Real-world dataset debugging
2. Data → Model pipeline building
3. Handling imbalance problems
4. Model evaluation beyond accuracy
5. Engineering thinking (not just training)

---

# Final Positioning

This is NOT:
❌ toy CNN project

This IS:
✅ AI + Semiconductor Manufacturing system prototype

---

# Phase 1 — Inference Result

## Command confirmed working
```
py -3.11 src/infer.py --image data/processed/test/Scratch/test_000123.png
```

## JSON output (confirmed against locked contract)
```json
{
  "image_id": "img_0001",
  "machine_id": "AOI_01",
  "lot_id": "LOT_UNKNOWN",
  "layer": "UNKNOWN",
  "timestamp": "2026-04-01T08:00:00+00:00",
  "defect_class": "Scratch",
  "confidence": 0.9712,
  "bbox": [0, 0, 64, 64],
  "ng_flag": true,
  "model_name": "cnn_baseline",
  "model_version": "cnn_baseline_v1"
}
```

All locked contract fields present and populated correctly.  
`bbox` is full-image `[0, 0, 64, 64]` — Phase 1 placeholder. Real detection in Phase 3.  
`ng_flag` correctly set to `true` for non-`none` defect class.

---

# Key Engineering Insights — Phase 1

## 1. Data engineering is the first failure point
The pipeline failed before a single training step because of schema assumptions.
`failureType` was assumed to be a string — it was a numpy ndarray.
`trianTestLabel` was assumed to be spelled correctly — it had a typo built into the dataset.
Lesson: always inspect raw values before writing parsing logic.

## 2. High overall accuracy can hide per-class failure
89.28% test accuracy sounds acceptable.
But Scratch recall was 31.89% and Loc was 45.31%.
In a real fab, missing a Scratch would be a yield loss event.
Lesson: never report a single accuracy number for a multi-class defect system.

## 3. Class imbalance requires structural solutions, not just weighted loss
Class weights were applied during training and helped the model converge.
They did not fully solve the minority-class confusion problem.
The val-to-test accuracy gap (~7 pp) reflects dataset distribution shift between splits.
Lesson: weighted loss is necessary but not sufficient — future phases need augmentation and/or focal loss.

## 4. Baseline CNN is the right first step, not the final answer
The baseline proves the pipeline works end-to-end.
Its weaknesses (on Scratch, Loc, Center) are a diagnostic, not a failure.
Each weakness points to a concrete next step:
- Scratch → needs more spatial resolution or deeper feature extraction
- Loc / Center → needs better class separation (ResNet or attention)
- Edge confusion → needs geometric augmentation

## 5. The JSON contract decouples model quality from system integration
Phase 2 (FastAPI) can be built and tested even before the model improves.
The locked contract ensures downstream consumers are not affected by model version changes.
This is the correct architecture for a production-facing AI system.

---

# Phase 3 — Detection Feasibility Validation

## Goal
Test whether a YOLO-style detector can be trained on WM-811K by deriving
bboxes from failing-die pixels.

## Dry-run result (FAILURE)
`src/convert_to_yolo.py` produced bbox annotations, but inspection
showed:
- bboxes covered scattered failing dies, not defect "objects"
- multiple semantically-different patterns (Scratch vs Loc) yielded
  visually identical bbox layouts
- no consistent object boundary existed for the model to learn

## Root cause
WM-811K is a **pattern-classification dataset**, not an object-detection
dataset. `pixel == 255` marks a failing die, not a defect region.
Any bbox derived from connected-component logic on these pixels is
semantically invalid — it encodes die-level failure, not a localizable
defect object.

## Decision pivot
- Detection on wafer maps is **abandoned** for this repo.
- Real defect detection is moved to a **separate AOI-camera dataset**
  in a future layer, not WM-811K.
- The system is re-framed as a layered pipeline:
  **pattern diagnosis → visual localization → automated action**
  where wafer-map classification (Phase 1) and AOI-camera detection
  (future) are distinct stages with distinct data sources.

## Lesson
Always validate the **semantic meaning of pixels** before assuming a
dataset supports a task. A dataset that visually "looks like" detection
data may still be classification-only at the label level.
