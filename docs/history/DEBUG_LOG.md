# AOI Defect Triage v1 — Debug Log

## Scope
This log records real issues encountered during Phase 1 of the AOI Defect Triage Vision subproject.

Project:
- AOI_Defect_Triage_v1
- Phase 1: CNN classification baseline
- Dataset: WM-811K / LSWMD

---

## 2026-04-01 — Data parsing bug in `LSWMD.pkl`

### Symptom
The first run of `prepare_data.py` could read the raw file, but parsed:

- Total rows: 811,457
- Labeled samples: 0
- Unlabeled / skipped: 811,457

That caused the split step to fail with:

```text
ValueError: With n_samples=0, test_size=0.15 and train_size=None, the resulting train set will be empty.
```

### Initial wrong assumption
The original parsing logic assumed the dataset stored labels as simple Python strings or lists.

Examples of the wrong assumption:
- `failureType` would look like `"Center"`
- `trianTestLabel` would look like `"Training"`

### Actual dataset structure
After inspecting the raw pickle file, the real columns were:

- `waferMap`
- `dieSize`
- `lotName`
- `waferIndex`
- `trianTestLabel`
- `failureType`

Important findings:

1. `failureType` is stored as a numpy ndarray, not a plain string
2. `trianTestLabel` is also stored as a numpy ndarray
3. The split column name is actually:
   - `trianTestLabel`
   - not `trainTestLabel`

### Root cause
There were three real causes:

1. The script checked the wrong data type for labels  
   It expected Python `list`, but the dataset stored values as `numpy.ndarray`

2. The script did not correctly handle empty ndarrays  
   Unlabeled rows used empty arrays, which needed special handling

3. The script checked the wrong split column name  
   The dataset uses `trianTestLabel` (missing the second `n`)

### Fix applied
Only `src/prepare_data.py` was changed.

#### Change 1 — label extraction
`extract_label()` was updated to:
- detect `numpy.ndarray`
- return `None` if the array is empty
- use `.flat[0]` to extract the actual label string

#### Change 2 — split extraction
`extract_split()` was updated to:
- support ndarray-based values
- extract `"Training"` or `"Test"` using `.flat[0]`

#### Change 3 — split column name
The code was updated to read:
- `trianTestLabel`

instead of:
- `trainTestLabel`

### Result after fix
The parser successfully recovered labeled data:
- Total rows: 811,457
- Labeled samples: 172,950
- Skipped unlabeled rows: 638,507

Class distribution became readable and valid.

### Why this matters
This is a strong real-world AI engineering example:
- the dataset was not broken
- the bug was in schema assumptions
- successful debugging required inspecting real raw values, not relying on documentation or guesswork

### Engineering lesson
Real-world ML projects often fail before training because of:
- schema mismatch
- nested label storage
- inconsistent or typo-based column names
- silent assumptions in preprocessing code

This issue was resolved before model training.

---

## 2026-04-01 — Processed dataset generation completed

After fixing parsing logic, `prepare_data.py` successfully generated image datasets under:

- `data/processed/train/`
- `data/processed/val/`
- `data/processed/test/`

Each split contains class folders:

- Center
- Donut
- Edge-Loc
- Edge-Ring
- Loc
- Near-full
- Random
- Scratch
- none

### Split summary
Using the built-in split from the dataset:
- train+val: 54,355
- test: 118,595

Final split:
- train: 44,762
- val: 9,593
- test: 118,595

### Note
The dataset's built-in split is unusual because the test side is larger than the training side.
This was kept for the baseline run to avoid changing too many things at once.

---

## 2026-04-01 — CNN baseline training started successfully

After preprocessing completed, `train.py` started successfully.

### Confirmed training setup
- device: CPU
- train samples: 44,762
- val samples: 9,593
- 9 classes loaded successfully
- class weights were computed automatically to address class imbalance

### Early training results
Observed early epochs:
- Epoch 1
  - Train Loss: 1.2150
  - Train Acc: 59.24%
  - Val Loss: 0.8830
  - Val Acc: 78.66%

- Epoch 2
  - Train Loss: 0.9082
  - Train Acc: 72.24%
  - Val Loss: 0.4933
  - Val Acc: 84.95%

- Epoch 3
  - Train Loss: 0.7770
  - Train Acc: 75.25%
  - Val Loss: 0.6506
  - Val Acc: 82.86%

### Initial interpretation
These first epochs suggest:

1. The model is learning normally
   - training loss is going down
   - training accuracy is going up

2. Validation accuracy rose quickly
   - this is common in a simple baseline when the first epochs already learn the largest patterns

3. Epoch 2 currently looks like the best checkpoint so far
   - highest validation accuracy among the first three epochs

### Caution
This does not mean the project is finished yet.

Still needed:
- complete all planned epochs
- run final evaluation
- generate confusion matrix
- inspect per-class performance
- test single-image inference

---

## Recommended next logging sections

When Phase 1 continues, add these sections next:

1. Final training summary
2. Evaluation metrics
3. Confusion matrix interpretation
4. Misclassification patterns
5. Follow-up improvements for Phase 1.5 / Phase 2

---

## Suggested future file placement
Recommended location for this file:

`AOI_Defect_Triage_v1/docs/DEBUG_LOG.md`

If `docs/` does not exist yet, create it.
