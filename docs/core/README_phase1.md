# AOI Defect Triage — Phase 1: CNN Classification Baseline

This phase trains a simple CNN to classify wafer map images from the WM-811K dataset
into 9 defect categories. No API, no database, no UI — just model training and evaluation.

---

## Defect classes

| Class | Meaning |
|---|---|
| Center | Defects clustered at wafer center |
| Donut | Ring-shaped defect band |
| Edge-Loc | Localized defects at wafer edge |
| Edge-Ring | Continuous defect ring at edge |
| Loc | Localized cluster not at edge or center |
| Near-full | Nearly entire wafer covered |
| Random | Random scattered defects |
| Scratch | Linear scratch pattern |
| none | Clean wafer, no defect |

---

## Folder structure

```
AOI_Defect_Triage_v1/
├── data/
│   ├── raw/                   ← Place LSWMD.pkl here (do not edit it)
│   └── processed/             ← Created by prepare_data.py
│       ├── train/
│       ├── val/
│       └── test/
├── src/
│   ├── prepare_data.py
│   ├── train.py
│   ├── evaluate.py
│   └── infer.py
├── models/                    ← Saved model weights go here
├── results/                   ← Evaluation report goes here
└── requirements.txt
```

---

## Step-by-step instructions

### Step 0 — Install Python packages

Run this once in your terminal from the project root:

```
pip install -r requirements.txt
```

Requires Python 3.9 or later. A GPU (CUDA) will speed up training but is not required.

---

### Step 1 — Place the dataset

Download `LSWMD.pkl` from Kaggle (search: "WM-811K wafer map").
Place it at:

```
data/raw/LSWMD.pkl
```

Do not rename or modify the file.

---

### Step 2 — Prepare the data

```
py -3.11 src/prepare_data.py
```

What this does:
- Reads LSWMD.pkl
- Filters to labeled wafer maps only (~172,000 of 811,000 total)
- Resizes each wafer map to a 64x64 PNG image
- Sorts images into class subfolders under data/processed/train/, val/, and test/
- Prints class counts so you can verify the distribution

Expected output: class counts table, then "Data preparation complete."
This step is slow (a few minutes). Run it only once.

---

### Step 3 — Train the model

```
py -3.11 src/train.py
```

What this does:
- Loads images from data/processed/train/ and val/
- Trains a small CNN for 20 epochs
- Uses class weights so rare defects are not ignored
- Saves the best checkpoint to models/cnn_baseline_v1.pth

Expected output: a table showing train loss / accuracy and val accuracy per epoch.
Training time: ~10-30 minutes on CPU, ~2-5 minutes on GPU.

---

### Step 4 — Evaluate the model

```
py -3.11 src/evaluate.py
```

What this does:
- Loads models/cnn_baseline_v1.pth
- Runs the model on the test set
- Prints overall accuracy, per-class accuracy, and confusion matrix
- Saves the report to results/eval_report.txt

Target: overall accuracy > 80%, no class at 0% recall.

---

### Step 5 — Run inference on a single image

```
py -3.11 src/infer.py --image data/processed/test/Scratch/test_000123.png
```

What this does:
- Loads the trained model
- Classifies the single image
- Prints a JSON result in the locked AOI contract format

Example output:
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

Note: `bbox` is the full image in Phase 1. The original Phase 3 plan to
derive real bboxes from WM-811K was later validated as not feasible
(WM-811K is pattern-classification data, not object-detection data).
See AOI_MASTER_ROADMAP.md §Phase 3 and AOI_DEBUG_EVOLUTION.md for the
revised architecture.
Note: `ng_flag` is `true` for any defect class other than `none`.

Optional metadata flags:
```
py -3.11 src/infer.py --image path/to/image.png --image-id img_0042 --machine-id AOI_02 --lot-id LOT456 --layer M1
```

---

## Phase 1 validation checklist

Before moving to Phase 2, confirm all of the following:

- [x] `data/processed/` contains all 9 class subfolders under train/, val/, and test/
- [x] Class counts printed by prepare_data.py show no empty classes
- [x] train.py runs end-to-end without errors
- [x] Training loss decreases across epochs
- [x] Val accuracy is logged per epoch
- [x] Final test accuracy is above 80%
- [x] No class shows 0% recall in the evaluation report
- [x] `models/cnn_baseline_v1.pth` exists
- [x] `results/eval_report.txt` exists and is readable
- [x] infer.py runs on one test image and produces valid JSON

---

## Phase 1 observed results

These are the actual results from the completed Phase 1 run.

### Data
- Total rows in LSWMD.pkl: 811,457
- Labeled samples recovered: **172,950**
- Skipped (unlabeled): 638,507
- Split: train 44,762 / val 9,593 / test 118,595

### Training
- Model: cnn_baseline_v1
- Best val accuracy: **96.40%**
- No training instability observed

### Evaluation
- Overall test accuracy: **89.28%**
- Val → test gap (~7 pp): likely class imbalance and dataset bias, not a broken model

### Per-class test accuracy
| Class | Accuracy | Note |
|---|---|---|
| none | 91.52% | Majority class, high recall expected |
| Near-full | 90.53% | Visually distinctive, strong |
| Center | 59.38% | Weak — visually similar to others |
| Donut | 61.64% | Weak |
| Edge-Loc | 66.74% | Weak |
| Edge-Ring | 66.07% | Confused with Edge-Loc |
| Loc | 45.31% | Weak — sparse, similar to noise |
| Scratch | 31.89% | Weakest — linear features hard for simple CNN |

### Key weakness
Model is biased toward the `none` (clean wafer) class.
Real defect classes are harder: visually similar, low sample count, and a simple CNN lacks the spatial reasoning needed.
This is expected for a baseline and is the direct motivation for Phases 2–5.

### Inference
Single-image inference confirmed working. Example output (Scratch image):
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

Note: `bbox` is `[0, 0, 64, 64]` (full image) in Phase 1. The original
Phase 3 plan to derive real bboxes from WM-811K was later validated as
not feasible — see AOI_MASTER_ROADMAP.md §Phase 3 and
AOI_DEBUG_EVOLUTION.md for the revised layered architecture.

---

## What is NOT in Phase 1

- No API server
- No database
- No UI or dashboard
- No Docker
- No LLM explanations
- No MES Copilot integration

These are planned for Phases 2–5.

---

## Phase 2 — FastAPI Inference Service

Phase 2 wraps the Phase 1 inference logic into a callable HTTP service.

This phase does **not** retrain the model and does **not** redesign the JSON contract.
It keeps the original AOI response fields and appends three API-level metadata fields at the end:

- `request_id`
- `processing_time_ms`
- `schema_version`

### Install / verify dependencies

```bash
pip install -r requirements.txt
```

### Start the service

From the project root:

```bash
py -3.11 -m uvicorn src.api:app --reload
```

Expected result:
- local service starts on `http://127.0.0.1:8000`
- `/predict` becomes available

### Manual PowerShell request example

```powershell
$img = "C:\Users\user\Desktop\TSMC\AOI_Defect_Triage_v1\data\processed\test\Scratch\test_000561.png"
$bytes = [System.IO.File]::ReadAllBytes($img)
$b64 = [System.Convert]::ToBase64String($bytes)

$body = @{
    image_base64 = $b64
    image_id     = "img_0001"
    machine_id   = "AOI_01"
    lot_id       = "LOT_UNKNOWN"
    layer        = "UNKNOWN"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

### Bad request behavior
If invalid base64 is sent, the API should return:
- HTTP 400

This behavior was validated during smoke testing.

## Phase 2 — Smoke Test Tooling

### API smoke test
Expected file:
- `tools/test_predict_smoke.ps1`

Purpose:
- validate happy path request
- validate bad request behavior
- verify all 14 response fields are present

Observed result:
- PASS: 2
- FAIL: 0

### One-command launcher
Expected file:
- `tools/run_phase2_api_and_smoke.ps1`

Purpose:
- start the FastAPI service
- wait for readiness
- run the smoke test automatically
- stop the API process

### One-command run

```powershell
.\tools\run_phase2_api_and_smoke.ps1
```

Expected summary:

```text
PASS: 2
FAIL: 0
ALL TESTS PASSED — Phase 2 API is healthy.
```

## Phase 2 — What this proves
By the end of Phase 2, this AOI project can now demonstrate:

- model training pipeline
- evaluation and confusion analysis
- single-image inference
- stable JSON contract
- callable HTTP inference API
- automated smoke validation

This is the point where the AOI project becomes a reusable Vision Layer service, while still staying independent from AI MES runtime.
