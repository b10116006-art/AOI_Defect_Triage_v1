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

Note: `bbox` is the full image in Phase 1. Real bounding boxes come in Phase 3 (YOLO).
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

Note: `bbox` is `[0, 0, 64, 64]` (full image) in Phase 1. Real bounding boxes are planned for Phase 3 (YOLO).

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

### Install new dependencies

```
pip install -r requirements.txt
```

### Start the service

Run from the project root:

```
uvicorn src.api:app --reload
```

The service starts on `http://localhost:8000`.

### Send a prediction request

The endpoint accepts a JSON body with a base64-encoded image and optional metadata.

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d "{
    \"image_base64\": \"$(base64 -w 0 data/processed/test/Scratch/test_000123.png)\",
    \"image_id\": \"img_0042\",
    \"machine_id\": \"AOI_02\",
    \"lot_id\": \"LOT456\",
    \"layer\": \"M1\"
  }"
```

### Example successful response

```json
{
  "image_id": "img_0042",
  "machine_id": "AOI_02",
  "lot_id": "LOT456",
  "layer": "M1",
  "timestamp": "2026-04-06T08:00:00+00:00",
  "defect_class": "Scratch",
  "confidence": 0.9712,
  "bbox": [0, 0, 64, 64],
  "ng_flag": true,
  "model_name": "cnn_baseline",
  "model_version": "cnn_baseline_v1",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "processing_time_ms": 12.5,
  "schema_version": "v1"
}
```

### MES integration note

The response is the locked AOI JSON contract with three appended fields.
A downstream MES service can consume `POST /predict` directly and use the
JSON payload as the Vision Layer signal in the broader decision pipeline.

---

## Phase 2 — Smoke Test

A one-click PowerShell script that validates the running API against two scenarios.

### Prerequisites

1. The API must be running before you execute the script:

```
uvicorn src.api:app --reload
```

2. The test dataset must exist (`data/processed/test/Scratch/test_000561.png`).
   If it is missing, run `prepare_data.py` first (see Phase 1 steps above).

### Run the smoke test

From the **project root** in PowerShell:

```
.\tools\test_predict_smoke.ps1
```

### Test 1 — Happy path (valid image)

The script reads `data/processed/test/Scratch/test_000561.png`, encodes it as
base64, and calls `POST /predict`.

Expected successful output:

```
--------------------------------------------------------------
  Test 1: Happy Path  (valid Scratch image -> /predict)
--------------------------------------------------------------

  Full response:
  {
    "image_id": "smoke_test_001",
    "machine_id": "AOI_SMOKE",
    ...
    "schema_version": "v1"
  }

  Checking required fields:
    OK  image_id          = smoke_test_001
    OK  machine_id        = AOI_SMOKE
    OK  lot_id            = LOT_SMOKE
    OK  layer             = ILD
    OK  timestamp         = 2026-04-10T...
    OK  defect_class      = Scratch   (or none / other class)
    OK  confidence        = 0.xxxx
    OK  bbox              = [0, 0, 64, 64]
    OK  ng_flag           = True / False
    OK  model_name        = cnn_baseline
    OK  model_version     = cnn_baseline_v1
    OK  request_id        = <uuid>
    OK  processing_time_ms = xx.xx
    OK  schema_version    = v1

  [PASS] All 14 contract fields present
```

### Test 2 — Bad request (invalid base64)

The script sends a deliberately malformed `image_base64` string.
The API is expected to reject it with HTTP 400.

Expected output:

```
--------------------------------------------------------------
  Test 2: Bad Request  (invalid base64 -> expect HTTP 400)
--------------------------------------------------------------

  HTTP status: 400
  Error body:  {"error":"Invalid image: could not decode base64 or open image file."}

  [PASS] API correctly returned HTTP 400 for invalid base64
```

### Final summary line

When both tests pass:

```
--------------------------------------------------------------
  Smoke Test Summary
--------------------------------------------------------------
  PASS: 2
  FAIL: 0

  ALL TESTS PASSED — Phase 2 API is healthy.
```

If a test fails, the script prints `[FAIL]` in red with a diagnostic message
and a reminder to check whether the API is running.
