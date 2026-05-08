# B8.3 Evaluation Smoke Loop — v1 vs. v2 Baseline Analysis

_Last updated: 2026-05-08_

## 1. Purpose

This document records what changed between the v1 and v2 runs of the
B8.3 evaluation smoke loop and why the change matters.

It is **engineering analysis**, not a model release note. No model
weights, no API code, no `/predict` JSON contract, and no
`eval_smoke.py` logic were modified between the two runs. The only
thing that changed is the **gold-set manifest** consumed by the smoke
loop:

- v1 — `src/b_yolo/data/eval_gold_manifest_v1.txt` (20 images)
- v2 — `src/b_yolo/data/eval_gold_manifest_v2.txt` (50 images, strict
  superset of v1)

Reading order:

- `B_PROJECT_BRIEF.md` §8.3 defines B8.3 (the smoke loop step itself).
- `B_PROJECT_BRIEF.md` §9.2 defines DG-2 (the gold dataset).
- `B_PROJECT_BRIEF.md` §10 defines DG-1 v0 (the annotation spec
  draft).
- This file is the **evaluation evidence** captured against those
  definitions.

## 2. v1 vs. v2 metric comparison

| Metric | v1 (`b8_3_baseline.json`) | v2 (`b8_3_baseline_v2.json`) | Δ |
|---|---:|---:|---:|
| `image_count` | 20 | 50 | +30 |
| `detection_count` | 21 | 53 | +32 |
| `ng_count` | 17 | 45 | +28 |
| `ng_ratio` | 0.85 | 0.90 | +0.05 |
| `confidence` mean | 0.5712 | 0.5625 | −0.009 |
| low-conf detections (`<0.5`) | 10 / 21 | 21 / 53 | proportion ≈ unchanged |

Per-class **detection** counts (not ground-truth class counts):

| Class | v1 detections | v2 detections | v2 GT images in manifest |
|---|---:|---:|---:|
| SCRATCH | 8 | 15 | 7 |
| PARTICLE | 2 | 12 | 7 |
| COATING BAD | 4 | 8 | 7 |
| BLOCK ETCH | 0 | 6 | 7 |
| PIQ PARTICLE | 2 | 5 | 7 |
| PO CONTAMINATION | 5 | 5 | 8 |
| SEZ BURNT | 0 | 2 | 7 |

> Note: `ng_ratio` rose from 0.85 to 0.90, but this **is not a model
> improvement claim**. Sample composition changed; in particular, v1
> over-represented `PO CONTAMINATION` (8/20 = 40 %) while v2 spreads
> mass across all seven classes. Drift in `ng_ratio` between runs
> with different manifests cannot be attributed to the model.

## 3. Coverage gap fixed by v2

v1 had a structural manifest defect: three of the seven Roboflow
classes had **zero ground-truth images** in the gold set.

| Class | GT images in v1 | GT images in v2 | Detections in v2 |
|---|---:|---:|---:|
| BLOCK ETCH | 0 | 7 | 6 |
| PARTICLE | 0 | 7 | 12 |
| SEZ BURNT | 0 | 7 | 2 |

The v1 baseline therefore had a per-class blind spot: it was
impossible for the v1 smoke run to produce evidence for or against
the model's behaviour on these three classes.

v2 closes that gap mechanically (each class now has 7+ GT images;
PARTICLE has 8). v2 does **not** close it semantically — the images
were selected by alphabetical order from the test split, not by an
expert reviewer (DG-2 expert curation is still pending).

## 4. Why v2 is a better baseline than v1

1. **Class coverage is no longer zero anywhere.** Every class is
   represented by at least 7 ground-truth images. Future regression
   diffs can flag per-class movement on all seven classes; v1 could
   not.
2. **Reproducibility is preserved.** v2 is a strict superset of v1,
   selected deterministically (alphabetical sort within each class).
   The v1 baseline corresponds exactly to the v1 subset of v2 —
   v1-vs-v2 deltas are **manifest-driven**, not run-noise.
3. **Sample size is larger without being huge.** 50 images keep the
   smoke loop fast (still seconds, not minutes) while giving each
   class enough samples to make per-class regression checks
   meaningful. Bigger evaluations belong on a real eval set with
   labels loaded — out of scope for B8.3 by design (§8.3).
4. **It exposes a real recall risk that v1 hid.** SEZ BURNT now
   shows 2 detections against 7 GT images, surfacing what looks like
   a recall problem the v1 manifest could not see. That risk being
   visible is the point of an honest baseline — see §5.

## 5. Remaining risks

### 5.1 Low-confidence detections (21 / 53)

Roughly **40 % of v2 detections** sit below confidence 0.5 — the
distribution is bimodal (a cluster near the 0.25 service default and
another above 0.7). Two implications:

- The runtime threshold (`conf=0.25`, default in `predict.py`) is
  letting through detections that DG-1 §10.7 ("when in doubt, prefer
  defect") deliberately tolerates. That is by design, not a defect.
- For any future Enhancement trial measured against this baseline,
  a *raw count* drop in `detection_count` is not necessarily an
  improvement — it could be lost true positives in the low-conf
  band. Trials must report the bucket histogram, not just the
  count.

### 5.2 SEZ BURNT still under-covered in detections

v2 holds 7 SEZ BURNT ground-truth images, but the model returned
only 2 detections of class SEZ BURNT across all 50 images. This is a
**suspected per-class recall gap**, consistent with the B7 per-class
mAP table (`COATING BAD`, `PO CONTAMINATION`, `SEZ BURNT` were the
three weakest classes at training time).

Per §10.7, this is treated as a **false-negative priority concern**,
not a model-quality acceptance. SEZ BURNT requires expert DG-2
review before it is treated as a stable baseline number.

### 5.3 DG-1 annotation spec is still `draft_v0`

The spec used to interpret these results is `B_PROJECT_BRIEF.md` §10
v0 — a draft. The thresholds in §10.4 (≥8 px shorter side, ±10 %
intensity envelope) are documented heuristics, not measured
constants. Until DG-1 promotes to v1 with expert sign-off:

- Per-class flag rules in §10.2 are advisory, not authoritative.
- A class disagreement between Roboflow and the model is logged but
  not adjudicated.
- Promotion of any v2 number to a "released" baseline is premature.

## 6. Architecture interpretation

This work belongs to the **Data Governance / evaluation track**, not
the **model track**.

What did **not** change between v1 and v2:

- model weights (still `runs/detect/models/b_yolo/roboflow_wafer_v12/weights/best.pt`)
- `src/b_yolo/predict.py` (run_inference contract unchanged)
- `src/b_yolo/api.py` (`/predict`, `/health` unchanged)
- `src/b_yolo/eval_smoke.py` (loop logic unchanged)
- `B_PROJECT_BRIEF.md` §4.3 JSON contract (no field added, removed,
  reordered, or renamed)
- AOI Master Roadmap phase order

What did change:

- `src/b_yolo/data/eval_gold_manifest_v2.txt` (new manifest file)
- `src/b_yolo/analyze_baseline.py` (one bug fix: the report header
  now reflects `--input` instead of a hardcoded path; **no analysis
  logic touched**)

This separation is the point of having an Enhancement Track gated on
DG-1..DG-4 (`B_PROJECT_BRIEF.md` §9.3): we are still inside DG work,
not Enhancement work. Calling any v2 number a "model improvement"
would be category-incorrect.

## 7. Next recommended step

### 7.1 DG-2 expert review list

The first real DG-2 deliverable, in priority order (highest
false-negative risk first):

1. **SEZ BURNT** (7 GT, 2 detections) — review every miss; confirm
   each is a true SEZ BURNT instance per §10.2; decide whether the
   miss is a label issue (Roboflow label noise) or a model recall
   issue.
2. **PO CONTAMINATION** (8 GT, 5 detections) and **COATING BAD**
   (7 GT, 8 detections) — the classes flagged in §10.2 as mutually
   ambiguous. Expert pass should resolve overlapping cases.
3. **Low-confidence detections** (21 entries) — apply §10.4
   noise-vs-defect thresholds and §10.6 edge-case rules; tag each as
   *accept / flag / reject*.
4. **Class disagreement candidates** (e.g. multiple classes detected
   on a single image) — tag per §10.6.

The output is a per-image annotation: *accept Roboflow label*,
*accept-with-comment*, *flag for re-label*, *exclude*.

### 7.2 G4 regression gate / baseline comparison

After DG-2 expert review:

- Re-run `eval_smoke.py` against the curated v2 manifest with the
  promoted DG-1 v1 spec stamped into `annotation_spec_version`.
- Lock that record as the **G4 reference baseline**.
- Define a regression gate: on any subsequent run, fail loudly if
  - `schema_check_passed` is `False`,
  - per-class `detection_count` drops by more than a documented
    threshold without an explanatory note, or
  - `ng_count` drops without an explanatory note (treat as suspected
    FN regression per §10.7).

Only after the G4 gate exists is the **first** Enhancement Track
trial (augmentation or focal loss; `B_PROJECT_BRIEF.md` §8.4) eligible
to run. Until then, all Enhancement work remains gated.

## 8. What this document is not

- It is **not** a claim that v2 demonstrates model improvement.
- It is **not** a sign-off that DG-1 or DG-2 is complete; both are
  still open work items.
- It is **not** a roadmap change; the Main Track order in
  `B_PROJECT_BRIEF.md` §8 (B8.2 → B8.3 → Controlled Enhancement
  trial → B9 → B10 → B11) is unchanged.
- It is **not** a code-change record; no source file was modified
  for the purpose of this comparison.
