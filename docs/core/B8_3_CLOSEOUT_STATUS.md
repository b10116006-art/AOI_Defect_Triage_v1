# B8.3 Closeout Status Snapshot

_Last updated: 2026-05-27._
**Status: snapshot, not closeout.** This document records what has been
delivered toward B8.3 closeout and what remains gated. It does **not**
declare full B8.3 closeout, does **not** un-gate the Enhancement Track,
and does **not** modify any spec, contract, or code.

---

## 1. Purpose / scope

### 1.1 Purpose

To give a future reader (or a future contributor / interview reviewer) a
single tracked answer to "where is B8.3 right now, and what is still
blocking full closeout?" — without having to reconstruct it from five
separate docs.

### 1.2 Scope

- Reads from existing tracked sources only — no number is re-measured
  here.
- Confines itself to **B8.3 (`B_PROJECT_BRIEF.md` §8.3)** plus the DG
  items that are referenced by B8.3 gating
  (`B_PROJECT_BRIEF.md` §9.3 / §9.4 and `B8_3_V1_VS_V2_ANALYSIS.md` §7).
- Status tags used below:
  **[implemented]** / **[validated]** / **[gated]** / **[planned]** /
  **[deferred]**.

### 1.3 What this doc explicitly does NOT do

- Does **not** declare full B8.3 closeout. Per
  `B8_3_V1_VS_V2_ANALYSIS.md` §7.2, full closeout requires DG-2 expert
  review → DG-1 v0 → v1 promotion → G4 reference baseline lock, none of
  which is complete.
- Does **not** un-gate the Enhancement Track
  (`B_PROJECT_BRIEF.md` §8.4 / §9.3).
- Does **not** promote any in-progress draft into a tracked governance
  artifact.
- Does **not** modify the locked AOI JSON contract
  (`AOI_PROJECT_STATE.md` §3, `AOI_MASTER_ROADMAP.md` §7).
- Does **not** edit any other tracked doc; this is a new-file-only PR.

---

## 2. What is already delivered

| Item | Status | Authoritative reference |
|---|---|---|
| B8 — Evidence Service | **[implemented]** | `B_PROJECT_BRIEF.md` §8.1 |
| B8.1 — Health check | **[implemented]** | `B_PROJECT_BRIEF.md` §8.1 |
| B8.2 — Service hardening (weights config, request logging, error handling) | **[implemented]** | `B_PROJECT_BRIEF.md` §8.2; `README.md` Development Status table |
| B8.3 — Evaluation smoke loop (v1 run, 20-image manifest) | **[implemented]** | `B8_3_V1_VS_V2_ANALYSIS.md` §1 / §2 |
| B8.3 — Evaluation smoke loop (v2 run, 50-image manifest, strict superset of v1) | **[implemented]** | `B8_3_V1_VS_V2_ANALYSIS.md` §1 / §2 |
| DG-2 gold manifests v1 / v2 (mechanical coverage of all 7 classes) | **[validated]** — mechanical only | `B8_3_V1_VS_V2_ANALYSIS.md` §3; `src/b_yolo/data/eval_gold_manifest_v{1,2}.txt` |
| DG-1 v0 Annotation Spec (defect ontology, bbox vs. segmentation, thresholds, clustered-defect rules, edge cases, FN priority) | **[implemented]** — v0 | `B_PROJECT_BRIEF.md` §10 (sections §10.1 – §10.9) |
| DG-1 rare-class failure register (cross-track observations) | **[implemented]** | `DG1_RARE_CLASS_FAILURE_ANALYSIS.md` (added PR #9) |
| Course-tech gap aligned to canonical Phase 4 logic | **[implemented]** | `COURSE_TECH_GAP_ANALYSIS.md` (added PR #8) |
| Portfolio Stage Overlay + Edge Deployment Track reference | **[implemented]** | `AOI_MASTER_ROADMAP.md` §14 / §15 (added PR #7) |

The "smoke loop produced a baseline output record" requirement of
`B_PROJECT_BRIEF.md` §8.3 is satisfied by the v1 and v2 runs analysed in
`B8_3_V1_VS_V2_ANALYSIS.md` §2. The raw artifacts behind those runs
remain outside the repo per policy (see §6).

---

## 3. What remains gated for full B8.3 closeout

Per `B8_3_V1_VS_V2_ANALYSIS.md` §7.2, the chain that converts the
current state into a full B8.3 closeout is, in order:

1. **DG-2 expert review on the §7.1 priority list** — **[gated]**.
   The full pass covers: SEZ BURNT misses (every miss reviewed per
   `B_PROJECT_BRIEF.md` §10.2 / §10.7), PO CONTAMINATION ↔ COATING BAD
   ambiguity, the 21 low-confidence detections, and class-disagreement
   candidates. The existing 6-image P1 pilot covered one instance of
   each pattern, not the full priority list. Reference:
   `B8_3_V1_VS_V2_ANALYSIS.md` §7.1.
2. **DG-1 v0 → v1 promotion** — **[gated]** behind expert-review
   sign-off on §10.2 flags and §10.4 thresholds, per
   `B_PROJECT_BRIEF.md` §10.9.
3. **Re-run `eval_smoke.py` with `annotation_spec_version` stamped** —
   **[gated]** behind item 2.
4. **Lock the G4 reference baseline** — **[gated]** behind item 3.
   Definition lives in `B8_3_V1_VS_V2_ANALYSIS.md` §7.2 (schema check,
   per-class detection_count drift threshold, ng_count drift treated as
   suspected FN regression).

None of items 1–4 is being attempted by this snapshot. The chain is
recorded here so a future contributor can pick up at the right step.

---

## 4. DG-by-DG status

Statuses below are the DG-item-level view; they do **not** redefine
anything in `B_PROJECT_BRIEF.md` §9.

| DG item | Scope (from §9.2) | Status today | Notes |
|---|---|---|---|
| **DG-1** Annotation Spec | 7-class ontology, bbox/seg, thresholds, clustered-defect rule, edge cases, FN priority, gold examples | **[implemented v0]** + rare-class register | v0 in `B_PROJECT_BRIEF.md` §10; rare-class register in `DG1_RARE_CLASS_FAILURE_ANALYSIS.md`. v0 → v1 promotion is **[gated]** per §10.9. |
| **DG-2** Gold Dataset | Expert-reviewed subset for B8.3 / Enhancement / future-model comparison | **[validated mechanically]**, **[gated semantically]** | v2 manifest has ≥7 GT images per class (`B8_3_V1_VS_V2_ANALYSIS.md` §3). Expert curation is still pending; the §7.1 priority pass has not been completed. |
| **DG-3** QA Mechanism | Auto format checks (YOLO `.txt` schema), double-label sampling, blind gold-data insertion | **[planned]** — no tracked spec yet | A DG-3-shaped review-candidate generator exists locally but is intentionally not committed (see §6). |
| **DG-4** Metrics emphasis | mAP50 / IoU + false-negative priority (`missed defect ≫ false alarm`) | **[partial]** | FN priority is in `B_PROJECT_BRIEF.md` §10.7 and used in `B8_3_V1_VS_V2_ANALYSIS.md`'s ng_count framing. No standalone DG-4 metrics doc yet. |
| **DG-5** Annotator qualification | IoU ≥ 0.85 threshold, ongoing scoring | **[planned, low-priority]** | Per `B_PROJECT_BRIEF.md` §9.1 / §9.2: no in-house annotation team; kept planned for edge-case re-label scenarios. |
| **DG-6** Closed-loop feedback | error → review → spec → dataset-version bump | **[planned]** | Required gate for B10 / B11 per `B_PROJECT_BRIEF.md` §9.3. |
| **DG-7** Version control | `annotation_spec_version` + `dataset_version` + `model_version` + `eval_version` bound together | **[planned]** | Critical gate for B9 ingestion per `B_PROJECT_BRIEF.md` §9.3. The G4 baseline lock (§3 item 4 above) is the first step where `annotation_spec_version` is stamped. |
| **DG-8** Tooling | Pre-label seed, audit log, IAA (Kappa / Krippendorff α) | **[planned]** | Per `B_PROJECT_BRIEF.md` §9.1, IAA primarily exists to validate Roboflow labels when re-labelling edge cases. |

---

## 5. Enhancement Track gating status

Per `B_PROJECT_BRIEF.md` §8.4 / §9.3 and `B8_3_V1_VS_V2_ANALYSIS.md` §7.2:

- The Enhancement Track is **[gated]**, not deferred forever.
- Required gate conditions: **DG-1 through DG-4 stable** *and* the
  **G4 reference baseline locked** (so any enhancement trial can be
  measured against a stable baseline, per §8.4).
- Today: DG-1 is at **v0** (not yet v1); DG-2 is **mechanically** valid
  but not yet semantically curated; DG-3 has **no tracked spec**;
  DG-4 is **partial**. G4 baseline is **not** locked.
- Therefore: the Enhancement Track gate **does not open** as a result of
  this snapshot. This document explicitly does not constitute a gate
  evaluation, and no augmentation, focal-loss, backbone, or other
  Enhancement Track work is authorized by it.

The candidate Enhancement items themselves remain catalogued in
`COURSE_TECH_GAP_ANALYSIS.md` (Enhancement / Expansion / Advanced
tracks); the wording there already reflects the post-PR #8 gating.

---

## 6. Intentionally deferred artifacts

The following are present in the working tree but are **intentionally
not committed** by this PR. The reason for each is recorded so a future
maintainer can re-evaluate without re-deriving the rationale.

| Artifact | Type | Reason held back |
|---|---|---|
| `outputs/DG2_P1_REVIEW_OBSERVATIONS_DRAFT.md` | in-progress draft memo | The 6-image P1 pilot is intentionally kept as an in-progress working review, not a tracked artifact (consistent with how `DG1_RARE_CLASS_FAILURE_ANALYSIS.md` cites it). Promotion is **[gated]** behind a full DG-2 §7.1 expert pass. |
| `src/b_yolo/dg2_review_candidates.py` | local tooling | Reviewer hold — code review not yet performed. Natural home is a future DG-3 (QA Mechanism) spec PR that commits the tool alongside its spec. |
| `results/b8_3_baseline.json`, `b8_3_baseline_v2.json`, `b8_3_analysis.txt`, `b8_3_analysis_v2.txt`, `b8_3_dg2_review_*.csv` | raw smoke-run / review artifacts | Per repo policy `results/*` is not committed; the tracked narrative lives in `B8_3_V1_VS_V2_ANALYSIS.md`. |
| `PHASE_0.8.6_STAGE1_SECURITY_CLEANUP.md` (working-tree only) | wrong-repo file | Belongs to MES / public-readiness, not AOI. Should be relocated to the MES repo rather than removed blindly. |
| Model weights (`*.pt`, `*.pth`) and dataset folders | binary / data | Covered by `.gitignore`; out of scope here for completeness. |

This list is the explicit answer to "what is sitting in the tree and
why isn't it in the repo." It does not authorize any of the items
above to be committed by a later PR without its own review.

---

## Cross-reference index

For navigation only — every reference points to existing tracked
material; no new claims are made by this index.

- Phase / order: `AOI_PROJECT_STATE.md` §6, `AOI_MASTER_ROADMAP.md` §5
  + §14, `B_PROJECT_BRIEF.md` §8.
- DG track definition: `AOI_MASTER_ROADMAP.md` §13,
  `B_PROJECT_BRIEF.md` §9.
- DG-1 v0 spec: `B_PROJECT_BRIEF.md` §10 (all subsections).
- B8.3 evaluation analysis: `B8_3_V1_VS_V2_ANALYSIS.md` (whole doc;
  closeout chain in §7).
- Rare-class register: `DG1_RARE_CLASS_FAILURE_ANALYSIS.md`.
- Enhancement candidates (gated): `COURSE_TECH_GAP_ANALYSIS.md`.
- Locked JSON contract: `AOI_PROJECT_STATE.md` §3,
  `AOI_MASTER_ROADMAP.md` §7.
