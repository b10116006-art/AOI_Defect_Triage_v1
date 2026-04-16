# B_PROJECT_BRIEF.md — AOI Camera YOLO Demo (B Project)

_Sibling project to `AOI_Defect_Triage_v1` (A Project)._
_Status: planned, not yet started. This document defines scope before any code is written._

---

## 1. Project positioning

The B Project is the concrete implementation of **Layer 2** in the
layered architecture defined in
`AOI_MASTER_ROADMAP.md` §4.1:

```
1. Wafer Map        → Pattern Classification     ← A Project (this repo)
2. AOI Camera       → Defect Detection           ← B Project (new repo)
3. MES / Decision Layer
4. Automation / Robot Action Layer
```

End-to-end pipeline:

**pattern diagnosis → visual localization → automated action**

The B Project owns one and only one responsibility: given an AOI camera
image of an inspected surface, return a structured JSON payload
containing localized defect bounding boxes, defect classes, and
confidence scores. It does **not** own wafer-map classification (that
is A's job), it does **not** own MES decision logic (that is Layer 3's
job), and it does **not** own physical actuation (that is Layer 4's
job).

### Why B is a separate repo, not a new branch

A and B operate on **different physical layers** of a real fab / OSAT
flow:

- A consumes wafer-level binary maps (die pass/fail), trained on
  WM-811K. The pixels mean *failing die*.
- B consumes camera images of physical surfaces (wafer surface, package
  surface, PCB surface). The pixels mean *intensity at a coordinate*.

These are not the same data modality and cannot share a model, a
preprocessor, or a dataset directory. Forcing them into one repo would
re-create exactly the semantic confusion that caused Phase 3 of A to be
re-scoped (see `AOI_DEBUG_EVOLUTION.md` → Phase 3 — Detection
Feasibility Validation).

A and B are joined only by a **JSON contract**, never by shared pixels.

### Repo naming

Proposed name for the new repo: `AOI_Camera_YOLO_Demo_v1`.

---

## 2. Primary dataset — Roboflow Wafer Defect v2

### Why Roboflow wafer defect is now the primary dataset

After the Phase 3 re-scope of A, the B Project needs a dataset whose
pixels are *already* real semiconductor surface defects with
bounding-box labels. The Roboflow **Wafer Defect v2 (final)** export
(YOLOv11 format) provides exactly that:

- Real wafer-surface defect imagery, not synthesized textures.
- Seven defect classes already relevant to fab AOI vocabulary:
  `BLOCK ETCH`, `COATING BAD`, `PARTICLE`, `PIQ PARTICLE`,
  `PO CONTAMINATION`, `SCRATCH`, `SEZ BURNT`.
- Pre-split into `train/valid/test` with YOLO `.txt` labels — directly
  compatible with Ultralytics, no ellipse-to-bbox conversion needed.
- License: CC BY 4.0 (workspace `wafer-irhuv`, project
  `wafer-defect-rv1vx`, version 2).

This replaces DAGM 2007 as the **primary** training source for the B
Project. DAGM is retained as a methodology control (see §2.1).

### 2.1 DAGM 2007 — demoted to control / method validation

DAGM 2007 is no longer the primary training set. It is kept in the
B Project strictly as a **comparison / method validation** dataset:
a synthetic-texture benchmark we can point to when explaining that
the training methodology (YOLO bounding-box detection on surface
defects) is the same one used by the academic inspection community
for fifteen years. We do not claim DAGM numbers are semiconductor
numbers; the Roboflow dataset is what carries that claim.

Historical rationale for DAGM is retained below because the A → B
story still relies on it as a credibility anchor in interviews.

### The honest constraint

Real semiconductor SEM defect datasets with bounding-box annotations
are not publicly available at meaningful scale. Fabs (TSMC, Intel,
Hitachi, ASML, etc.) treat SEM defect imagery as proprietary process
data. Public alternatives are either:

- classification-only (WM-811K, MixedWM38) — already eliminated in
  A Project Phase 3,
- too small for honest detection training (a few hundred images per
  class), or
- not semiconductor at all (steel, fabric, PCB).

DAGM 2007 is the dataset the academic semiconductor inspection
community has used for over fifteen years as the **public proxy for
wafer surface inspection**. It is referenced in surface-defect
detection literature precisely because it fills the gap left by
proprietary fab data.

### What DAGM 2007 actually is

- **Source**: DAGM (German Association for Pattern Recognition),
  Weakly Supervised Learning for Industrial Optical Inspection
  benchmark, 2007.
- **Task**: defect localization on textured backgrounds.
- **Annotation**: weak ellipse masks marking defect regions
  (convertible to axis-aligned bounding boxes for YOLO without
  semantic loss — unlike WM-811K, the underlying pixels here actually
  *are* the defect).
- **Volume**: 10 texture classes; each class contains roughly 1,000
  defect-free images and ~150 defect images, for a total of around
  11,500 images — large enough for honest YOLO training, not just
  anomaly detection.
- **Defect types**: ten different synthesized surface defects on ten
  different textured backgrounds (scratches, blobs, contamination
  patterns, structural irregularities).

### Why this is defensible in an interview

The story is honest and load-bearing:

1. The B Project simulates **wafer surface inspection** — the AOI
   step that happens after pattern-level diagnosis.
2. Real wafer SEM defect data is proprietary and not publicly
   distributable.
3. DAGM 2007 is the **public benchmark used by the academic
   inspection community** as a wafer-surface proxy. It is synthetic
   *texture*, but the defect localization task it represents is the
   same task a fab AOI engineer is trying to solve.
4. By training on DAGM, the B Project is producing a model whose
   *methodology* — bounding-box detection of localized surface
   defects on textured backgrounds — transfers directly to the
   proprietary case once real data is available.

This framing avoids overclaiming ("trained on real wafer SEM data") and
also avoids underclaiming ("just a generic object detector"). It lands
exactly where a fab process engineer would expect a public-data
prototype to land.

---

## 3. Why MVTec AD — transistor subset is the semiconductor anchor

DAGM gives volume and methodology. It does **not** give a single image
of an actual semiconductor part. To close that gap, the B Project also
includes the **MVTec AD `transistor` subset** as a semiconductor
realism anchor.

### What it is

- **Source**: MVTec Anomaly Detection dataset.
- **Subset used**: `transistor` only.
- **Annotation**: pixel-level masks for four defect modes —
  `bent_lead`, `cut_lead`, `damaged_case`, `misplaced`.
- **Volume**: 213 training images (defect-free) + 100 test images
  (mixed defect-free and defective). Small.
- **License**: CC BY-NC-SA 4.0 — non-commercial. Acceptable for a
  portfolio / interview demo, **not** acceptable for a productized
  service.

### Role in the B Project

MVTec transistor is **not** the training set. It is the
**demonstration set**. Concretely:

- A YOLO model (or a segmentation model converted to bounding boxes)
  is trained primarily on DAGM 2007.
- A second, much smaller fine-tuning pass is run on the MVTec
  transistor subset to adapt the model to a real semiconductor
  package.
- The interview demo and the README headline image both use the
  transistor subset, so the visible output of the B Project is "YOLO
  bounding boxes localizing bent leads on a real transistor package"
  — not "YOLO bounding boxes on a synthesized texture".

### Why this two-dataset split matters

- DAGM alone is honest about volume but invites the question "but is
  this really semiconductor?".
- MVTec transistor alone is honest about realism but cannot support a
  multi-class detector — too few images.
- Together, they answer both questions. DAGM proves the methodology
  scales; MVTec transistor proves the methodology lands on real
  semiconductor parts.

This is the same pattern A used: prove the pipeline works end-to-end
first, then be explicit about which results are *baseline* and which
are *aspirational*.

---

## 4. A → B JSON contract

A and B are joined exclusively through JSON. The contract has three
roles:

1. **A → B inspection trigger** — A publishes a wafer-level pattern
   diagnosis. The diagnosis carries enough metadata for an
   orchestrator (or a human) to decide whether B should be invoked
   on a downstream image.
2. **B → MES detection result** — B publishes localized bounding
   boxes for one image, in a format that mirrors A's contract style
   so a single MES consumer can normalize both.
3. **Joint case object** — the orchestrator (Layer 3, MES) is the one
   that fuses A's diagnosis with B's detection into a single case
   record. Neither A nor B is responsible for that fusion.

### 4.1 A's existing output (unchanged)

A already emits the locked AOI contract:

```json
{
  "image_id": "img_0001",
  "machine_id": "AOI_01",
  "lot_id": "LOT123",
  "layer": "ILD",
  "timestamp": "2026-04-12T10:00:00Z",
  "defect_class": "Scratch",
  "confidence": 0.97,
  "bbox": [0, 0, 64, 64],
  "ng_flag": true,
  "model_name": "cnn_baseline",
  "model_version": "cnn_baseline_v1",
  "request_id": "uuid-...",
  "processing_time_ms": 12.5,
  "schema_version": "v1"
}
```

A's `bbox` stays at `[0, 0, 64, 64]` (full image) by design — A is a
classifier, not a detector. The B Project does not change A.

### 4.2 Inspection trigger (derived from A's output)

When A reports `ng_flag: true` with a pattern class that warrants
downstream visual inspection, the orchestrator constructs an
inspection trigger and calls B:

```json
{
  "trigger_id": "trig-2026-04-12-0001",
  "source": {
    "system": "A_wafer_pattern",
    "request_id": "uuid-of-A-call",
    "lot_id": "LOT123",
    "wafer_id": "W07",
    "pattern_class": "Scratch",
    "pattern_confidence": 0.97
  },
  "inspection": {
    "target_image_id": "aoi_cam_0042",
    "expected_defect_family": "linear_scratch",
    "priority": "high"
  },
  "schema_version": "v1"
}
```

The B Project does **not** need to know about A's CNN. It only needs
to know which image to inspect and (optionally) what kind of defect
the upstream layer was already worried about. The
`expected_defect_family` field is advisory only — B is allowed to
disagree and report a different class.

### 4.3 B's detection output

B emits one record per inspected image:

```json
{
  "image_id": "aoi_cam_0042",
  "trigger_id": "trig-2026-04-12-0001",
  "lot_id": "LOT123",
  "wafer_id": "W07",
  "timestamp": "2026-04-12T10:00:01Z",
  "detections": [
    {
      "defect_class": "bent_lead",
      "confidence": 0.91,
      "bbox": [120, 84, 144, 102],
      "bbox_format": "xyxy"
    },
    {
      "defect_class": "damaged_case",
      "confidence": 0.74,
      "bbox": [200, 150, 232, 188],
      "bbox_format": "xyxy"
    }
  ],
  "ng_flag": true,
  "model_name": "yolo_aoi_camera",
  "model_version": "yolo_aoi_v1",
  "request_id": "uuid-of-B-call",
  "processing_time_ms": 27.3,
  "schema_version": "v1"
}
```

Design notes:

- `image_id`, `lot_id`, `wafer_id`, `timestamp`, `ng_flag`,
  `model_name`, `model_version`, `request_id`, `processing_time_ms`,
  `schema_version` — same field names and ordering style as A's
  contract, so a single MES parser handles both.
- `detections` is a list — B may return zero, one, or many bounding
  boxes per image. Zero detections with `ng_flag: false` is a valid
  "clean" result.
- `bbox_format` is explicit. We default to `xyxy` (top-left,
  bottom-right pixel coordinates) so downstream consumers do not
  guess.
- `trigger_id` provides traceability back to the upstream A diagnosis.
  If B is called standalone (no A), `trigger_id` is omitted.

### 4.4 Joint case object (Layer 3 / MES, not B)

For completeness, the MES layer fuses A and B by `lot_id` + `wafer_id`
into a single case record. That record is **out of scope** for the B
Project. B's contract ends at "valid detection JSON returned". The B
repo will not contain MES code.

---

## 5. First milestone — YOLO baseline on Roboflow wafer defect

The first milestone is intentionally narrow. It exists to prove the
pipeline runs end-to-end on real data, in the same spirit as A's
Phase 1.

### Goal

Train a YOLO baseline on the Roboflow wafer defect v2 dataset (7
classes) and produce one valid detection JSON for one test image.
DAGM 2007 is retained only as a comparison / method-validation run
and is **not** required for milestone 1 to be green.

### In scope

- New repo `AOI_Camera_YOLO_Demo_v1` initialized with the same
  layout discipline as A: `data/raw/`, `data/processed/`, `src/`,
  `models/`, `results/`, `docs/`.
- DAGM 2007 download script (raw files placed under `data/raw/`,
  never modified in place).
- DAGM-to-YOLO format conversion script: ellipse masks → axis-aligned
  bounding boxes → YOLO `.txt` label files. This conversion is
  semantically valid (the underlying pixels really are defect
  pixels), and this is explicitly documented in the conversion
  script's docstring to avoid repeating the WM-811K mistake.
- YOLO baseline training script using a standard framework (Ultralytics
  YOLOv8 or YOLO11). Single GPU, default hyperparameters, no tuning.
- Per-class mAP evaluation, saved to `results/eval_report.txt`.
- A `predict.py` that takes one image, runs inference, and emits the
  B-side JSON contract defined in §4.3.
- A `README_milestone1.md` that lets another person rerun the entire
  pipeline from scratch.

### Out of scope for milestone 1

- MVTec transistor fine-tuning (milestone 2).
- FastAPI service wrapper (milestone 3, mirrors A's Phase 2).
- Real A → B end-to-end orchestration (milestone 4).
- MES integration (never; that is Layer 3's repo).
- Hyperparameter sweeps, model architecture comparisons, or any
  "improve mAP" work. Milestone 1 is about pipeline correctness, not
  model quality.

### Definition of done

Milestone 1 is complete when **all** of the following are true:

- Roboflow wafer defect v2 raw data exists under
  `data/raw/roboflow_wafer/` and has not been modified in place.
- `src/b_yolo/prepare_roboflow_wafer.py` has been run, producing a
  clean YOLO-format tree under
  `data/processed/roboflow_wafer_yolo/` with `train/`, `valid/`, and
  `test/` splits and a `data.yaml` that uses absolute paths.
- `train.py` runs end-to-end against that `data.yaml` without errors
  and saves a checkpoint under `models/b_yolo/.../weights/best.pt`.
- `evaluate.py` produces a per-class mAP table (7 classes) and saves
  `results/eval_report.txt`.
- `predict.py` runs on one Roboflow test image and prints a JSON
  payload that matches the B-side contract in §4.3 exactly (field
  names, field ordering, `bbox_format: "xyxy"`). The `defect_class`
  values must be drawn from the seven Roboflow class names.
- `README_milestone1.md` allows a fresh clone to rerun the full
  pipeline.

### Explicit non-goals for milestone 1

- We do **not** chase a target mAP number. The numbers we get from a
  default-config YOLO baseline are the numbers we report. Honest
  weak baselines are more credible than tuned hero numbers.
- We do **not** modify the JSON contract during milestone 1. If the
  contract turns out to need a new field, that is a separate
  decision documented in the B repo's own evolution log.
- We do **not** start the FastAPI wrapper before milestone 1 is
  green. A's Phase 1 → Phase 2 sequencing is the model: prove the
  offline pipeline first, wrap it in a service second.

---

## 6. Relationship to A Project commitments

This brief does not modify any A Project file other than its own
addition. Specifically:

- A's locked JSON contract is unchanged.
- A's Phase 1 / Phase 2 records are unchanged.
- A's Phase 3 status (validated, detection path on WM-811K deferred)
  is unchanged — and is in fact the reason this brief exists.
- A's `MES_INTEGRATION_BLUEPRINT.md` is unchanged. B's output JSON
  is designed to be consumable by the same MES integration layer
  described there, with no additional adapters required on A's side.

The B Project will live in a separate repository. This brief stays in
A's `docs/core/` because the layered architecture in
`AOI_MASTER_ROADMAP.md` §4.1 needs an authoritative pointer to where
Layer 2 is being built and why.
