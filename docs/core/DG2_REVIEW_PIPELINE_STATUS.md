# DG-2 Review Pipeline Status Snapshot

_Last updated: 2026-05-28._
**Status: snapshot, not closure.** This document records the current state
of the DG-2 review pipeline — which working artifacts exist, which are
authoritative, which are temporary, and what is intentionally not
committed. It does **not** declare DG-2 closure, does **not** promote any
in-progress working review, and does **not** modify any spec, contract,
or code.

---

## 1. Purpose / scope

### 1.1 Purpose

To give a future reader (or future contributor) one tracked answer to
"what does the DG-2 P1 review pipeline currently look like, and what is
intentionally outside the repo?" — without requiring them to reconstruct
it from the working tree.

### 1.2 Scope

- Reads from existing tracked sources and inspects the working-tree
  artifact set; no number, observation, or rule is re-derived here.
- Confines itself to the DG-2 review pipeline for B8.3
  (`B_PROJECT_BRIEF.md` §9.2 / §9.4 and `B8_3_V1_VS_V2_ANALYSIS.md` §7.1).
- Status tags used: **[authoritative]**, **[working]**,
  **[temporary]**, **[superseded]**, **[never-commit]**, **[held]**.

### 1.3 What this doc explicitly does NOT do

- Does **not** declare DG-2 closure. DG-2 expert curation on the §7.1
  priority list is still incomplete; the P1 expert review remains an
  in-progress working review.
- Does **not** promote any in-progress working artifact into the tracked
  governance set.
- Does **not** commit the DG-2 candidate-generator tooling
  (see §6); a future DG-3 (QA Mechanism) PR is its natural home.
- Does **not** un-gate the Enhancement Track
  (per `B8_3_CLOSEOUT_STATUS.md` §5).
- Does **not** modify the locked AOI JSON contract, the §4.3 detection
  schema, or any code path.
- Does **not** edit any other tracked doc; this is a new-file-only PR.

---

## 2. Artifact authority map

The DG-2 review pipeline currently consists of one local script, four
CSVs in `results/`, one draft memo in `outputs/`, and the upstream
`b8_3_baseline_v2.json` smoke-run output. Roles below are descriptive of
the working tree; nothing in this section authorizes any of these files
to enter the repo.

| Artifact | Path (working-tree only) | Role | Status |
|---|---|---|---|
| DG-2 candidate-generator | `src/b_yolo/dg2_review_candidates.py` | Deterministic, read-only generator that emits detection-level rows by four rules (`low_confidence`, `sez_burnt_miss`, `class_ambiguity`, `high_risk_class`); rules align with `B_PROJECT_BRIEF.md` §10.2 / §10.7 | **[authoritative]** for the candidate-vocabulary rules; **[held]** from commit pending a future DG-3 PR |
| Pre-filled per-detection review workbook | `results/b8_3_dg2_review_sheet_sorted_v1.csv` | 46 detection rows over 20 images, sorted, with pre-filled `decision` and `[PRE-FILL]` `comment` columns | **[working / authoritative]** for the in-progress P1 expert review; **[never-commit]** per `results/` policy |
| Image-level priority rollup | `results/b8_3_dg2_review_image_summary_v1.csv` | 20-image rollup with `priority` (P1–P4), `n_rows`, `n_distinct_classes`, `flags`, `suggested_decision`, `suggested_comment` | **[working / authoritative]** for the priority bucketing; **[never-commit]** |
| In-progress P1 observations memo | DG-2 P1 working observations (in-progress review, not a committed artifact) | Six-image observation patterns (Obs A–D) cited as "in-progress DG-2 P1 expert review" by `DG1_RARE_CLASS_FAILURE_ANALYSIS.md` | **[working]** in-progress review; **[never-commit]** per the Option 2 framing chosen in PR #9 |
| Raw candidates CSV | `results/b8_3_dg2_review_candidates.csv` | 46 raw candidate rows (5 columns; no decision/comment); equivalent in content to the sorted_v1 workbook minus pre-fills and ordering | **[temporary / regenerable]** by the generator; **[never-commit]** |
| Empty-form review sheet | `results/b8_3_dg2_review_sheet.csv` | Original sheet with empty `decision`/`comment` columns, carrying a UTF-8 BOM on the header (Excel save artifact) | **[superseded]** by `_sorted_v1.csv`; **[never-commit]** |
| Smoke-run input baseline | `results/b8_3_baseline_v2.json` | v2 smoke-run output, consumed by the generator | **[temporary / regenerable]** by `src/b_yolo/eval_smoke.py`; **[never-commit]** |
| Earlier baseline | `results/b8_3_baseline.json` | v1 smoke-run output; superseded for analysis purposes by v2 (see `B8_3_V1_VS_V2_ANALYSIS.md` §4) | **[superseded]**; **[never-commit]** |

The tracked narrative for the upstream B8.3 evaluation lives in
`B8_3_V1_VS_V2_ANALYSIS.md`; this section does not duplicate it.

---

## 3. P1 priority bucket = the six reviewed images

The image-level priority rollup distributes the 20-image working set
into four buckets. The P1 bucket has exactly six images, matching the
in-progress DG-2 P1 expert review one-for-one.

| Priority | Image count | Notes |
|---|---:|---|
| **P1** | **6** | one-for-one match with the in-progress P1 expert review |
| P2 | 5 | out of scope for the P1 review |
| P3 | 1 | out of scope for the P1 review |
| P4 | 8 | out of scope for the P1 review |

The six P1 images (image IDs only — the working artifacts hold the
full filenames):

- `10215` — multi-class predictions, `class_ambiguity` + `high_risk_class` + `low_confidence`
- `1022` — multi-class predictions, `class_ambiguity` + `high_risk_class` + `low_confidence`
- `1034` — multi-class predictions, `class_ambiguity` + `high_risk_class` + `low_confidence`
- `10720` — `sez_burnt_miss` (GT = `SEZ BURNT`, zero detections; FN risk per `B_PROJECT_BRIEF.md` §10.7)
- `14057` — multi-class predictions, `class_ambiguity` + `high_risk_class` + `low_confidence`
- `14070` — multi-class predictions, `class_ambiguity` + `high_risk_class` + `low_confidence`

This list mirrors the priority assignment in the working
`_image_summary_v1` rollup. It does **not** restate the per-pattern
observations themselves (those are governed by the in-progress P1 expert
review and the consolidated rare-class register at
`DG1_RARE_CLASS_FAILURE_ANALYSIS.md` §4 / §5 / §6).

P2 / P3 / P4 are not in scope for the P1 review pass and are not
discussed by this doc.

---

## 4. Open risks / known gaps

These are recorded so a future maintainer does not have to re-derive
them. None of them is being fixed by this PR.

1. **Generator script is untracked.** `src/b_yolo/dg2_review_candidates.py`
   is the only source of the candidate-vocabulary rules used by every
   downstream sheet, but it is intentionally not committed. A fresh
   clone cannot regenerate `results/b8_3_dg2_review_candidates.csv` from
   the smoke-run baseline alone. Resolution path: a future DG-3 (QA
   Mechanism) PR that commits the script alongside its DG-3 spec.
2. **Priority assignment + `[PRE-FILL]` enrichment are manual.** The
   `priority` (P1–P4) column in `_image_summary_v1.csv` and the pre-filled
   `decision` / `comment` columns in `_sorted_v1.csv` are not produced
   by any tracked code. They are an ad-hoc augmentation of the raw
   candidates output. Reproducibility gap: another reviewer cannot
   re-derive identical priority/pre-fill values without informal
   guidance.
3. **UTF-8 BOM on `b8_3_dg2_review_sheet.csv`** (`0xEF 0xBB 0xBF` at the
   start of the header). The other three CSVs are clean. The
   BOM-bearing file is already **[superseded]** by `_sorted_v1.csv`, so
   this only matters if the superseded file is ever re-used; a strict
   CSV parser would read the first column name as `﻿image_id`.
4. **In-progress P1 expert review is not a committed artifact.** Per
   the Option 2 framing adopted in PR #9, the P1 observations are cited
   as an "in-progress DG-2 P1 expert review (working review, not a
   committed artifact)" rather than as a tracked memo. Promotion is
   gated and is **not** attempted by this doc.
5. **Pre-fill label inconsistency between the two `_v1` workbooks.**
   `_sorted_v1.csv` uses the user-facing column names `decision` and
   `comment` with the `[PRE-FILL]` prefix inside values;
   `_image_summary_v1.csv` uses `suggested_decision` and
   `suggested_comment` as column names. Both are clear in isolation;
   the inconsistency is recorded for awareness, not as a defect.

---

## 5. Terminology consistency check

A read-only cross-check of the vocabulary used across the pipeline:

| Vocabulary axis | Status | Evidence |
|---|---|---|
| 7-class `CLASS_NAMES` (`BLOCK ETCH`, `COATING BAD`, `PARTICLE`, `PIQ PARTICLE`, `PO CONTAMINATION`, `SCRATCH`, `SEZ BURNT`) | **Consistent** across the generator, the four CSVs, `B_PROJECT_BRIEF.md` §10.2, and the per-class tables in `B8_3_V1_VS_V2_ANALYSIS.md` §2 | no drift observed |
| `candidate_type` vocabulary (`low_confidence`, `sez_burnt_miss`, `class_ambiguity`, `high_risk_class`) | **Consistent** across the generator and all three detection-level CSVs (`candidates`, `sheet`, `sorted_v1`) | no drift observed |
| `high_risk_class` set (`PO CONTAMINATION`, `COATING BAD`) | **Consistent** with `B_PROJECT_BRIEF.md` §10.7 weak-performer call-out (the third weak performer, `SEZ BURNT`, has its own dedicated `sez_burnt_miss` rule rather than being in the high-risk-class set) | by design |
| Provisional `sez_burnt_misclass` governance vocabulary | **Properly contained.** Present only in governance docs (`DG1_RARE_CLASS_FAILURE_ANALYSIS.md` §6 / §8 and the in-progress P1 review) as a *provisional future-discussion* category; absent from code, CSVs, and the runtime candidate vocabulary | as intended — observation, not runtime |

No terminology change is proposed by this doc.

---

## 6. Intentionally not committed / not promoted

The following are present in the working tree but intentionally remain
outside the repo. The reason for each is recorded so a future
maintainer can re-evaluate without re-deriving the rationale.

| Item | Reason held back |
|---|---|
| `src/b_yolo/dg2_review_candidates.py` | Reviewer hold — code review not yet performed against a tracked DG-3 (QA Mechanism) spec. Natural home is a future DG-3 PR that commits the tool together with its spec. |
| `results/b8_3_dg2_review_sheet_sorted_v1.csv`, `_image_summary_v1.csv`, `_candidates.csv`, `_sheet.csv` | Per repo policy `results/*` is not committed. The tracked narrative for the upstream B8.3 evaluation already exists at `B8_3_V1_VS_V2_ANALYSIS.md`; the DG-2 review workbooks are working artifacts behind it. |
| In-progress DG-2 P1 expert review (working memo) | Consistent with the Option 2 framing chosen in PR #9: the P1 review is cited by tracked governance as an in-progress working review, not promoted to a tracked artifact. Promotion is gated behind a full DG-2 §7.1 expert pass. |
| `results/b8_3_baseline.json`, `b8_3_baseline_v2.json`, `b8_3_analysis.txt`, `b8_3_analysis_v2.txt` | Per repo policy `results/*` is not committed; analysis narrative lives in `B8_3_V1_VS_V2_ANALYSIS.md`. |
| `PHASE_0.8.6_STAGE1_SECURITY_CLEANUP.md` (working-tree only) | Belongs to MES / public-readiness, not AOI; should be relocated to the MES repo rather than removed blindly. |
| Model weights, dataset folders | Covered by `.gitignore`; listed here only for completeness. |

This list does not authorize any of the items above to be committed by
a later PR without its own review.

---

## Cross-reference index

For navigation only — every reference points to existing tracked
material; no new claims are made.

- B8.3 evaluation analysis: `B8_3_V1_VS_V2_ANALYSIS.md` (closeout chain
  in §7).
- B8.3 closeout snapshot: `B8_3_CLOSEOUT_STATUS.md`.
- DG-1 v0 spec: `B_PROJECT_BRIEF.md` §10.
- DG track definition: `B_PROJECT_BRIEF.md` §9 and `AOI_MASTER_ROADMAP.md` §13.
- Rare-class register (cites the in-progress P1 review):
  `DG1_RARE_CLASS_FAILURE_ANALYSIS.md`.
- Enhancement Track gating: `B_PROJECT_BRIEF.md` §8.4 / §9.3 and
  `B8_3_CLOSEOUT_STATUS.md` §5.
- Locked JSON contract: `AOI_PROJECT_STATE.md` §3,
  `AOI_MASTER_ROADMAP.md` §7.
