# DG-1 Rare-Class Failure Analysis (Draft)

_Last updated: 2026-05-26._ **Status: DRAFT — observation-only formalization. No retraining, augmentation, focal-loss, threshold, spec, or code changes are proposed.**

This document consolidates rare- and weak-class failure observations across
Track A (WM-811K CNN) and Track B (Roboflow YOLO, B8.3) into a single
governance register, cross-referenced to the DG-1 v0 ontology spec. It is
**not** a model release note and **not** a fix proposal.

---

## 1. Scope & boundary

### 1.1 Scope
- Track A — Phase 1 CNN baseline on WM-811K (per `AOI_PROJECT_STATE.md` §2).
- Track B — YOLO B8.3 baseline v1 and v2 on Roboflow (per
  `B_PROJECT_BRIEF.md` §8.3 / §9.2 / §10).
- DG-2 P1 expert-review observations on 6 images, from the in-progress
  DG-2 P1 expert review (a working review, not a committed artifact).

### 1.2 Boundary — what this doc is NOT
- Not a model release note.
- Not a fix proposal — no retraining, no augmentation, no focal loss, no
  threshold/confidence-cutoff change, no spec rewrite, no code change.
- Not a re-measurement — every number is quoted from an existing tracked
  source, never recomputed here.
- Not a root-cause attribution — every entry is a **candidate observation**,
  not a finding.
- Enhancement Track remains **gated** behind DG-1..DG-4 stabilization and
  B8.3 closeout (per `AOI_MASTER_ROADMAP.md` §12 / §14 and
  `B_PROJECT_BRIEF.md` §7.4).

### 1.3 Posture (implemented / validated / planned, kept separated)

| Item | Status |
|---|---|
| Per-class numeric tables (Track A, Track B v1/v2) | **[implemented]** — already in tracked docs |
| B8.3 v1 → v2 coverage closure on `BLOCK ETCH` / `PARTICLE` / `SEZ BURNT` | **[validated]** — recorded in `B8_3_V1_VS_V2_ANALYSIS.md` §3 |
| 6-image DG-2 P1 expert review | **[validated]** — observations captured in the in-progress DG-2 P1 expert review (working review, not yet committed) |
| This formalization doc | **[planned, draft]** |
| DG-1 v0 → v1 spec promotion, DG-2 expansion, Enhancement Track work | **[planned, gated]** — not addressed here |

---

## 2. Source-evidence map

| Source | Tracked? | What it provides |
|---|---|---|
| `docs/core/B_PROJECT_BRIEF.md` §10.7 | yes | Authoritative weak-class list for Track B (`COATING BAD`, `PO CONTAMINATION`, `SEZ BURNT` from B7 baseline); the FN-priority cost model ("missed defect ≫ false alarm") |
| `docs/core/B_PROJECT_BRIEF.md` §10.2 | yes | DG-1 v0 defect-ontology cues, referenced per-class below |
| `docs/core/COURSE_TECH_GAP_ANALYSIS.md` "Phase 1 已知弱點" table | yes (post PR #8) | Per-class Track A test accuracy and sample counts; Val→Test gap |
| `docs/core/B8_3_V1_VS_V2_ANALYSIS.md` §2 / §3 | yes | Per-class detection counts v1/v2; v1 zero-GT blind spot on three classes; v2 mechanical closure |
| In-progress DG-2 P1 expert review (working review, not a committed artifact) | n/a (not committed) | Expert-review observations on six images (10720, 10215, 1022, 1034, 14057, 14070) |
| `results/b8_3_baseline.json` / `_v2.json`, `b8_3_analysis*.txt`, `b8_3_dg2_review_*.csv` | no (policy) | Raw artifacts behind the tracked analyses; **not re-quoted here** |

---

## 3. Track A (CNN, WM-811K) — weak-class inventory

Per-class test accuracy as recorded in `COURSE_TECH_GAP_ANALYSIS.md`
(Phase 1 baseline: overall test acc **89.28 %**, val **96.40 %**, 9-class):

| Class | Test Acc | Samples | Observation tag |
|---|---:|---:|---|
| `none` (dominant) | 91.52 % | 110,701 | not a weak class — sample dominance caveat (masks overall accuracy) |
| `Scratch` | **31.89 %** | 693 | weakest; rare-class |
| `Loc` | **45.31 %** | 1,973 | weak; rare-class |
| `Center` | 59.38 % | 832 | weak; rare-class |
| `Donut` | 61.64 % | 146 | weak + extreme rarity |
| `Edge-Ring` | 66.07 % | 1,126 | sub-baseline |
| `Edge-Loc` | 66.74 % | 2,772 | sub-baseline |

(`Near-full` and `Random` are part of the 9-class set per `README.md` but
the source table does not list per-class numbers for them; recorded as a
data-completeness gap, not a finding.)

`COURSE_TECH_GAP_ANALYSIS.md` also records: Val→Test gap 96.40 % → 89.28 %
is consistent with overfitting, and no data augmentation is applied in
`src/train.py`. Both are existing observations, quoted not re-derived.

### Observation A.1 — rare-class accuracy is bimodal
The seven non-`none` classes split into two visible bands: very weak
(`Scratch` 31.89 %, `Loc` 45.31 %) and weak-but-mid (Center / Donut /
Edge-Ring / Edge-Loc 59–67 %). Sample count alone does **not** explain
the ordering — `Donut` (146 samples, 61.64 %) outperforms `Scratch`
(693 samples, 31.89 %). Observation only.

### Observation A.2 — `none` dominance is a presentation caveat, not a defect
At 110,701 / ~118,000 samples, the `none` class governs any unweighted
average. Recording this so overall 89.28 % is not read as evidence about
defect-class behaviour.

---

## 4. Track B (YOLO, Roboflow B8.3) — rare-class inventory

### 4.1 Per-class detection counts (quoted from `B8_3_V1_VS_V2_ANALYSIS.md` §2)

| Class | v1 dets | v2 dets | v2 GT imgs | §10.7 B7 weak performer? |
|---|---:|---:|---:|---|
| `SCRATCH` | 8 | 15 | 7 | — |
| `PARTICLE` | 2 | 12 | 7 | — |
| `COATING BAD` | 4 | 8 | 7 | **yes** |
| `BLOCK ETCH` | 0 | 6 | 7 | — |
| `PIQ PARTICLE` | 2 | 5 | 7 | — |
| `PO CONTAMINATION` | 5 | 5 | 8 | **yes** |
| `SEZ BURNT` | 0 | 2 | 7 | **yes** |

### 4.2 v1 zero-GT coverage blind spot — validated, closed
`B8_3_V1_VS_V2_ANALYSIS.md` §3 records that v1 had **zero ground-truth
images** for `BLOCK ETCH`, `PARTICLE`, and `SEZ BURNT`. v2 closes that gap
**mechanically** (each class now has ≥7 GT images) but **not semantically**
— the v2 manifest was selected by alphabetical order from the test split,
not by expert reviewer. DG-2 expert curation is still pending.

### Observation B.1 — `SEZ BURNT` under-detection persists into v2
After v1's zero-GT was closed, v2 still shows only 2 detections against
7 GT images. Consistent with the in-progress DG-2 P1 expert review (Observation B
on image 10720: GT = `SEZ BURNT`, model predicted `(none)`, flagged
`sez_burnt_miss`).

### Observation B.2 — `PARTICLE` v2 detection count (12) exceeds v2 GT image count (7)
Numeric observation only. Could reflect multi-instance images,
over-detection, or a mix; the tracked source does not attribute. Not in
the §10.7 priority list, but worth tracking.

### Observation B.3 — `PO CONTAMINATION` detection count unchanged v1 → v2 (5 → 5) under composition shift
v1 over-represented `PO CONTAMINATION` (8/20 = 40 % of v1 GT, per
`B8_3_V1_VS_V2_ANALYSIS.md` §2 note). In v2 the class is spread across
50 images, yet detection count is identical. `B8_3_V1_VS_V2_ANALYSIS.md`
already cautions against reading manifest-deltas as model improvement;
recorded here as a pattern, not a finding.

### Observation B.4 — §10.7 priority weak performers cluster in the DG-2 P1 review
All three §10.7 weak performers appear in the 6-image DG-2 P1 sample:
`COATING BAD` in four images (10215, 1034, 14057, 14070), `PO CONTAMINATION`
in one (1022), `SEZ BURNT` in one as a miss (10720). The sample is small
and not yet statistical; the *direction* matches §10.7's prioritization.

---

## 5. Cross-track observations

### Observation X.1 — same class name, different ontologies
`Scratch` (Track A, WM-811K) is a wafer-level binary failing-die pattern;
`SCRATCH` (Track B, Roboflow) is a camera-image surface defect. Identical
surface label, **non-comparable underlying semantics**. Per
`AOI_MASTER_ROADMAP.md` §4.1 the two tracks are joined only at the JSON
contract boundary, never by sharing pixels. Recorded as a naming
observation; no unification is proposed.

### Observation X.2 — rare-class weakness is a shared symptom, not a shared mechanism
Track A's weakness centres on minority classes in a single-image
classification task with no augmentation. Track B's weakness centres on
per-class FN risk under the §10.7 cost model, against a small gold set
whose coverage was only mechanically closed in v2. Same *symptom* (low
per-class numbers); different *mechanism*. No joint treatment is proposed.

### Observation X.3 — `none` (Track A) and `ng_ratio` (Track B) are structurally analogous composition-sensitive numbers
`none` dominates Track A's per-class averaging. `ng_ratio` in Track B is
similarly a composition-sensitive number explicitly warned against in
`B8_3_V1_VS_V2_ANALYSIS.md` §2. Both must be read with sample-composition
context, not as headline metrics. Observation only.

---

## 6. Per-pattern classification

Classification schema mirrors the in-progress DG-2 P1 expert review: **candidate** fix-data
/ fix-spec / model-behavior / governance blind spot. Every entry is
candidate, not finding.

| Pattern | Source observation(s) | Classification (candidate) |
|---|---|---|
| Track A: `Scratch` 31.89 % / `Loc` 45.31 % extreme weakness | A.1 | model-behavior + fix-data (imbalance) |
| Track A: `Donut` 146 samples, 61.64 % (low N, mid acc) | A.1 | fix-data (sample scarcity) |
| Track A: Val→Test gap 96.40 % → 89.28 % | `COURSE_TECH_GAP_ANALYSIS.md` "Phase 1 已知弱點" | model-behavior (generalization) |
| Track A: `Near-full` / `Random` missing from the source per-class table | §3 completeness note | governance blind spot (data completeness in source doc) |
| Track B: `SEZ BURNT` 2/7 dets in v2 + DG-2 P1 miss on 10720 | B.1 + DG-2 P1 Obs B | model-behavior + governance blind spot (review candidate vocabulary captures "no detection" only) |
| Track B: `COATING BAD` over-predict on design-feature-heavy images | DG-2 P1 Obs A | model-behavior + fix-data |
| Track B: `COATING BAD` ↔ `PO CONTAMINATION` boundary on dark / contamination-texture regions | DG-2 P1 Obs C | fix-spec (DG-1 §10.2 cue clarity) |
| Track B: `BLOCK ETCH` ↔ `COATING BAD` co-prediction on design-feature-heavy images | DG-2 P1 Obs A (14070, 14057 sub-pattern) | model-behavior + fix-spec |
| Track B: possible real multi-defect (1022) | DG-2 P1 Obs D | valid multi-defect (not confusion) |
| Track B: `PARTICLE` v2 dets (12) > v2 GT imgs (7) | B.2 | numeric observation; classification not yet warranted |
| Track B: `PO CONTAMINATION` v1 = v2 = 5 across composition shift | B.3 | numeric observation; classification not yet warranted |
| Cross-track: `Scratch` / `SCRATCH` name overlap, different semantics | X.1 | governance observation (naming) |

---

## 7. Current boundary

To keep this doc within its intended scope, the following are **explicitly
NOT proposed** by anything above:

- **No retraining** of Track A CNN or Track B YOLO.
- **No augmentation** added to `src/train.py`.
- **No focal-loss** or other loss-function changes.
- **No threshold or confidence-cutoff changes.**
- **No edits to `B_PROJECT_BRIEF.md` §10 DG-1 spec** — Observations
  pointing at §10.2 cue clarity are *questions*, not rewrites.
- **No changes to `src/b_yolo/dg2_review_candidates.py`** — Observation B.1
  on the review-candidate vocabulary is a recorded blind spot, not a code
  change request.
- **No CSV / JSON / TXT artifact edits**; no new artifacts under
  `results/` or `outputs/`.
- **No promotion of the in-progress DG-2 P1 expert review** out of
  working-review status as part of this doc.
- **No roadmap / phase changes** — Phase 4 (LLM defect/evidence
  explanation) and Phase 5 (MES integration) ordering and Enhancement
  Track gating remain per `AOI_MASTER_ROADMAP.md` §14.

This doc records what is observed. It does not authorize action.

---

## 8. Next recommendations

These are **suggestions for later, gated discussion**, not commitments
here.

1. **DG-1 spec clarification candidates** — Observation X.1 (Track A/B
   `Scratch` naming overlap) and the Track B fix-spec patterns
   (`COATING BAD` ↔ `PO CONTAMINATION` cue clarity from DG-2 P1 Obs C;
   `BLOCK ETCH` ↔ `COATING BAD` boundary) are candidates for a future
   DG-1 v0 → v1 promotion discussion, which `B_PROJECT_BRIEF.md` §10.9
   already gates behind expert review sign-off.

2. **DG-2 expansion candidates** — The §10.7 priority weak performers
   (`COATING BAD`, `PO CONTAMINATION`, `SEZ BURNT`) and the v1-coverage-gap
   classes (`BLOCK ETCH`, `PARTICLE`) are natural targets for the next
   DG-2 expert-review pass beyond the 6-image P1 sample. Sequencing
   remains gated; no commitment here.

3. **Enhancement Track gating reminder** — Track A's bimodal rare-class
   accuracy (Observation A.1) is the natural target population for the
   augmentation / focal-loss / backbone items enumerated in
   `COURSE_TECH_GAP_ANALYSIS.md`. Per the post-PR #8 alignment that track
   remains **gated** behind DG-1..DG-4 stability + B8.3 closeout. This
   doc adds no new pressure to un-gate.

4. **Governance vocabulary to register** — DG-2 P1 Observation B
   (provisional `sez_burnt_misclass` category alongside the existing
   `sez_burnt_miss`) is a future DG governance topic, recorded here so it
   stays visible alongside the rare-class inventory. Not a code request.

5. **G4 regression watch** — The patterns recorded in §3–§5 are the
   natural reference set for future G4 regression discussion (per the
   in-progress DG-2 P1 expert review §4). No threshold or metric is proposed here.
