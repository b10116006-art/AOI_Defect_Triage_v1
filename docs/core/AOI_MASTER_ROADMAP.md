# AOI_MASTER_ROADMAP.md
_Last updated: 2026-04-09_

## 1. Purpose

This is the master roadmap for `AOI_Defect_Triage_v1`.

It consolidates:
- completed Phase 1 work
- current repo state
- next-step implementation direction
- safe integration path into the larger AI MES Copilot system
- future RAG / LLM expansion
- repo / demo / interview logic

This file is intended to become the single source of truth for:
- project phase tracking
- system architecture direction
- what is implemented vs validated vs planned vs deferred

---

## 2. Executive Summary

`AOI_Defect_Triage_v1` is not a standalone toy CV project.

It is the **Vision Layer** of a broader manufacturing AI architecture:

**image → defect → process context → reasoning → decision**

The long-term target is:
1. detect / classify AOI defects from image input
2. convert model output into structured JSON
3. fuse AOI result with MES process data
4. retrieve relevant historical / SOP knowledge through RAG
5. use an LLM decision layer to produce engineering explanation and action recommendations

Current status:
- Phase 1 completed
- repo cleaned and pushed
- next safest engineering step: Phase 2 API service
- integration with MES remains planned, not yet coupled at runtime

---

## 3. Current System Positioning

### What this project is
- an AOI defect triage system prototype
- a CV module designed for future system integration
- a demoable AI engineering project with data pipeline, training, evaluation, and inference output

### What this project is not
- not yet an online production system
- not yet a full detection system with real bbox localization
- not yet connected live to the MES runtime
- not yet using RAG in the AOI repo itself
- not yet using LLM for defect explanation inside this repo

---

## 4. Architecture Role in the Larger AI Stack

### Larger target architecture
1. **AOI Vision Layer**
   - image ingestion
   - defect classification / detection
   - JSON output contract

2. **MES Process Layer**
   - scrap / KPI / machine state
   - anomaly context
   - process-side signals

3. **Knowledge Layer**
   - SOPs
   - failure cases
   - corrective action records
   - RAG retrieval

4. **Decision Layer**
   - LLM synthesis
   - root-cause reasoning
   - recommended action
   - workflow continuity

### AOI repo scope
This repo currently owns only the Vision Layer and its immediate serving path.

### 4.1 Revised layered architecture (post Phase 3 validation)

The system is now explicitly layered by data source, not by model type:

1. **Wafer Map → Pattern Classification** (existing Phase 1, WM-811K)
2. **AOI Camera → Defect Detection** (separate dataset, YOLO or similar)
3. **MES / Decision Layer** (process context fusion)
4. **Automation / Robot Action Layer** (downstream response)

End-to-end pipeline:

**pattern diagnosis → visual localization → automated action**

Each layer owns its own dataset and its own model. They are joined only
through the JSON contract boundary, never by sharing pixels across
incompatible data sources.

---

## 5. Phase Map

## Phase 1 — Data Engineering + CNN Baseline + JSON Inference
### Goal
Prove that the AOI pipeline can run end-to-end on a real semiconductor-style defect dataset.

### Implemented
- raw dataset parsing
- schema debugging
- usable sample recovery
- processed dataset generation
- CNN baseline training
- evaluation report
- single-image inference
- structured JSON output verification
- repo cleanup and GitHub publication

### Validated results
- usable labeled samples recovered: **172,950**
- validation accuracy: **96.40%**
- test accuracy: **89.28%**

### Key engineering story
The largest early blocker was not modeling.
It was **real dataset schema mismatch** and **data usability recovery**.

This is important for interview/demo because it shows:
- data debugging ability
- schema inspection ability
- practical ML engineering, not notebook-only work

### Output state
- `prepare_data.py` works
- `train.py` works
- `evaluate.py` works
- `infer.py` works
- JSON contract is defined and demonstrated

### Status
**Completed**

---

## Phase 2 — FastAPI Service Layer
### Goal
Turn script-based inference into a callable service.

### Why this phase matters
Without API serving, the model remains a script.
With API serving, it becomes a reusable system module.

### Deliverables
- `src/api.py`
- `POST /predict`
- image upload support
- optional metadata fields:
  - `machine_id`
  - `lot_id`
  - `layer`
  - `image_id`
- return same JSON contract as `infer.py`
- append:
  - `request_id`
  - `processing_time_ms`

### Rules
- do not rewrite model
- do not change training code
- do not change JSON contract
- keep minimal diff

### Status
**Next immediate step**

---

## Phase 3 — Detection Feasibility Validation (completed)
### Goal
Validate whether YOLO-style bbox detection can be derived directly from
WM-811K wafer maps.

### Conclusion
**Not feasible on this dataset.** WM-811K is a pattern-classification
dataset: pixel value 255 indicates a failing die, not a defect object
region. Any bbox derived from connected-component logic on these pixels
is therefore semantically invalid and must not be used as a detection
ground truth.

### What was tried (preserved for history)
- dataset conversion to YOLO format (`src/convert_to_yolo.py`, dry-run)
- annotation strategy via failing-die clustering
- bbox sanity inspection on Scratch / Loc / edge patterns

### Decision
Detection on wafer maps is **deferred / re-scoped**. Real defect
detection belongs to a separate AOI-camera dataset, not WM-811K.
See the new layered architecture in §4.1.

### Status
**Validated and closed. Detection path moved to AOI camera layer.**

---

## Phase 4 — Batch Inference + Production-style IO
### Goal
Move from single-image demo inference to workload-style inference.

### Planned work
- batch folder inference
- CSV / JSONL output
- traceable request logging
- predictable output schema per image
- easier testing for system integration

### Why this phase matters
This is the bridge between one-off model demo and factory-style usage.

### Status
**Planned**

---

## Phase 5 — AOI → MES Integration
### Goal
Fuse AOI output with MES process context.

### Integration logic
AOI output should become one of the signals consumed by the MES decision flow.

### Example flow
1. AOI predicts `Scratch`
2. JSON output sent to MES-side service
3. MES service adds:
   - machine state
   - recent scrap trend
   - layer KPI
   - anomaly context
4. unified case object is created
5. downstream decision layer reasons over combined evidence

### Required integration design rules
- keep AOI runtime independent until API contract is stable
- use JSON as boundary, not direct code coupling
- do not import AOI training logic into MES repo
- define an AOI event schema / payload shape first
- use API or message/event boundary, not ad-hoc file coupling

### Status
**Planned but architecturally aligned**

---

## Phase 6 — RAG + LLM Decision Layer
### Goal
Turn AOI + MES evidence into engineering explanation and next action.

### Planned behavior
- retrieve similar cases / SOPs / troubleshooting knowledge
- summarize defect + process context
- generate:
  - probable root cause
  - explanation
  - recommended engineering action
  - confidence / evidence trace

### Important note
This phase should happen **after**
- JSON contract is stable
- AOI API exists
- MES-side fusion contract exists

### Status
**Planned**

---

## 6. Current Training and Model State

### Current baseline
- model type: CNN classification baseline
- framework: PyTorch
- dataset: WM-811K / LSWMD-derived wafer map images
- imbalance handling: class weights
- evaluation available: yes

### Current strengths
- strong proof-of-pipeline
- high validation metric
- reasonably strong test metric
- clean inference output contract
- reproducible local flow

### Current known weaknesses
- not yet detection-grade
- minority classes still weaker than dominant class
- no live service yet
- no integrated MES-side feedback loop yet

### Honest positioning
This is a **strong baseline and architecture foundation**, not the final CV model.

---

## 7. JSON Contract Status

### Current status
Locked and should not be casually changed.

### Purpose
The JSON output is the boundary between:
- AOI model repo
- MES integration layer
- future RAG / decision systems

### Current rule
Phase 2 may append metadata such as:
- `request_id`
- `processing_time_ms`

But must not break the existing output contract fields.

---

## 8. Safe Integration Strategy (Do Not Break Future Coupling)

### Good strategy
- AOI repo remains independent
- AOI serves inference via API
- MES consumes AOI JSON output
- RAG consumes unified case object later

### Bad strategy
- import AOI scripts directly into MES runtime
- hardcode MES paths into AOI repo
- mix training and serving logic into one file
- redesign JSON fields casually

---

## 9. Immediate Next Step

### Recommended
Implement **Phase 2 FastAPI service** now.

### Why
This is the highest-value, lowest-risk next step because it:
- preserves Phase 1 work
- upgrades the repo into a callable service
- prepares clean future integration with MES
- improves interview/demo value immediately

---

## 10. Deferred on Purpose

Do not force these decisions now:
- full YOLO production metrics
- Docker/Kubernetes
- CI/CD
- live MQTT integration in AOI repo
- LLM explanation in AOI repo
- vector DB design
- final MES event bus architecture

These belong later, after the service boundary is stable.

---

## 11. Interview-safe Summary

You can accurately say:
- The AOI project has completed a full Phase 1 baseline: data parsing, CNN training, evaluation, and JSON-based inference.
- The next stage is to wrap inference into a FastAPI service.
- The AOI system is intentionally designed as the Vision Layer of a broader MES + RAG + LLM decision architecture.
- YOLO detection is planned as the next CV extension for localization, after the classification baseline and service layer are stabilized.

---

## 12. Enhancement Track reference (non-blocking)

`docs/core/COURSE_TECH_GAP_ANALYSIS.md` defines an **Enhancement Track**
of course-driven improvement ideas (data augmentation, focal loss,
ResNet backbone, Grad-CAM, Optuna, U-Net, ControlNet synthetic data,
domain adaptation, etc.).

Rules:

- The Enhancement Track is a **reference**, not a phase. It does **not**
  change the order of Phase 1 → Phase 6 above.
- Enhancement items are **non-blocking** and **planned only** — none
  are implemented.
- Each item is gated by a Main Track milestone. See
  `docs/core/B_PROJECT_BRIEF.md` §7 for the trigger-based timing table
  (after B8.2 / after ingestion+eval loop / after MES+decision
  readiness).
- Items in §10 "Deferred on Purpose" stay deferred; the Enhancement
  Track does not override them.

---

## 13. Data Governance / Annotation Quality Track (parallel, planned)

The Data Governance (DG) Track defines the **annotation-quality
preconditions** under which model numbers can be trusted. It is a
parallel, planned track — none of its items are implemented.

Items DG-1 through DG-8 are defined in `docs/core/B_PROJECT_BRIEF.md`
§9. Headlines:

- DG-1 Annotation Spec — rules for accepting / rejecting Roboflow
  pre-labels, not a from-scratch SOP
- DG-2 Gold Dataset — expert-reviewed reference subset
- DG-3 QA Mechanism — format checks, double-label sampling, gold
  insertion
- DG-4 Metrics emphasis — mAP / IoU + false-negative priority
- DG-5 Annotator qualification — *low priority short-term, no
  in-house annotation team*
- DG-6 Closed-loop feedback — error → review → spec → dataset bump
- DG-7 Version control — annotation_spec / dataset / model / eval
  versions bound together
- DG-8 Tooling — pre-label seed, audit log, IAA (Cohen's Kappa /
  Krippendorff's Alpha)

### Positioning

- DG is the **quality precondition** for the Enhancement Track.
  Enhancement asks "how do we make the number better?"; DG asks "is
  the number itself trustworthy?".
- DG uses its own `DG-N` numbering and does **not** consume Main
  Track numbers (no B8.4, B8.5).
- DG does **not** reorder Main Track. The current order remains
  B8.2 → B8.3 → (Controlled Enhancement trial) → B9 → B10 → B11.

### Hard dependencies (gates)

- **B8.3** *(current focus)* — needs minimal DG-1 (spec draft) and
  DG-2 (gold subset, even 20–50 samples) to be meaningful, but DG is
  non-blocking for B8.3 itself.
- **Enhancement Track** — DG-1 through DG-4 must be **stable** before
  any enhancement (augmentation, focal loss, backbone, etc.) is run.
- **B9** *(critical gate)* — DG-7 versioning must be in place.
  Ingested evidence must carry `dataset_version` and
  `annotation_spec_version`. MES must not consume ambiguous evidence.
- **B10 / B11** — DG-6 closed-loop feedback must be ready.

### Rules

- All DG items are **planned only** and must not be presented as
  implemented in any document or interview narrative until they are.
- DG does **not** modify the JSON contract (§4 in
  `B_PROJECT_BRIEF.md`). Any version metadata exposed downstream
  (e.g., for B9) is added at ingestion time, not by changing the
  existing detection schema.

See `docs/core/B_PROJECT_BRIEF.md` §9 for the execution-level item
definitions, B8.3 integration, and gating timing.

---

## 14. Portfolio Stage Overlay (Stage 1–4)

_Added 2026-05-22. Append-only overlay. This section does not modify the Phase
Map in §5; it maps existing phases/tracks onto a delivery timeline and records
planned documentation deliverables. Status tags used below:_
**[implemented] / [in progress] / [planned] / [gated] / [deferred]**.

### 14.0 Phase 4 canonical identity (reconciliation)

This overlay sets the canonical identity of **Phase 4 = LLM defect / evidence
explanation**, consistent with `AOI_PROJECT_STATE.md` §6. The earlier §5 entry
"Phase 4 — Batch Inference + Production-style IO" is **reframed as a supporting
production-hardening / future serving capability**, not the main Phase 4
identity. Batch inference remains an optional serving enhancement that may land
before, during, or after Phase 4 explanation work; it no longer defines the
phase.

§5 above is left unedited for history. Where §5 and this section differ on the
meaning of "Phase 4," **this section is canonical**. (`README.md` still carries
the old Phase 4 label and should be reconciled during the Stage 1 README pass.)

### 14.1 Scope and exclusions

- Records **repo-facing** roadmap items only.
- Deliberately excludes external portfolio activity (resume wording, articles,
  social posts, hiring targets, hardware budgets, admissions/IELTS timelines)
  and other repos' internal milestones. Those live outside this repo.

### 14.2 Stage map

**Stage 1 — Foundation Polish [planned]**
Order rule: B8.3 / DG closeout proceeds first; Stage 1 polish follows.
- `docs/adr/ADR_001_phase3_detection_not_feasible.md` — promote the existing
  §Phase 3 trade-off narrative into a standalone ADR. **[planned]**
- `LICENSE` (MIT) file at repo root — README already states MIT; the file
  itself is missing. **[planned]**
- `docs/images/confusion_matrix.png` + README embed (Phase 1 per-class result).
  **[planned]**
- `docs/images/json_contract_example.json` + README block (contract example +
  rationale). **[planned]**
- README portfolio pass: architecture diagram, quantitative results block,
  JSON contract example, "Industrial AI Stack" cross-link. **[planned]**
  (cross-link to `mes-rag-assistant` already partially present.)

**Stage 2 — Phase 4 LLM Explanation + closeout [planned]**
- **Phase 4 first increment** — LLM-based explanation over a CNN/YOLO
  prediction; spec + minimal POC. **[planned]**
  - Output structured as a Pydantic `LLMExplanation` schema (input: image +
    predicted class + confidence; output: structured explanation). **[planned]**
- B8.3 / DG track closeout. **[in progress → planned closeout]**
- `docs/track_a_b_integration_spec.md` — how Track A (wafer-map classification)
  and Track B (camera detection) fit together at the contract boundary.
  **[planned]** (The A→B contract itself is already specified in
  `B_PROJECT_BRIEF.md` §4; this is the integration-level spec, not a contract
  change.)

**Stage 3 — MES Integration + Cross-System Demo [planned, gated]**
- `docs/mes_integration_spec.md` — AOI-side integration spec. **[gated]** — see
  §9 of `MES_INTEGRATION_BLUEPRINT.md`; blocked until the MES repo publishes
  `aoi_sidecar_spec.md`.
- Track A + B integration demo notebook. **[planned]**
- End-to-end cross-repo demo notebook (AOI → MES → RAG). **[planned]**
  (cross-repo; coordinate before committing.)
- `INDUSTRIAL_AI_STACK.md`. **[planned]** (cross-repo artifact.)

**Stage 4 — Post-enrollment / research [deferred]**
- Thesis topic, publication draft, real industrial dataset access.
  **[deferred]** — out of self-study scope; recorded for direction only.
- Edge deployment work — see §15. **[gated / deferred]**

### 14.3 Ordering invariants (unchanged)

1. B8.3 / DG closeout before new feature phases.
2. Stage 1 polish before Phase 4 build.
3. Phase 4 (LLM explanation) is the Stage 2 priority.
4. Phase 5 / MES integration only **after** the MES sidecar spec exists.
5. Locked JSON contract (§7) is not modified by any item above.

---

## 15. Edge Deployment Track (planned, gated — reference only)

_Added 2026-05-22. Append-only. This track is **not** an active phase and is
**not** promoted to implementation. Recorded for direction only._

### 15.1 Status and gate

- Status: **[planned, gated]** — strictly after Stage 2, and dependent on a
  **stable AOI evidence service + Phase 4 explanation layer** being in place
  first.
- Does **not** reorder the Phase Map (§5) and does **not** override §10
  "Deferred on Purpose." Docker remains deferred per §10 until the serving
  boundary is stable.
- Nothing here authorizes hardware purchase or repo code now.

### 15.2 Reference scope (when un-gated)

Potential future items, in rough dependency order — all **[deferred]**:
- ONNX export of the trained classifier (with output-equivalence test).
- TensorRT FP16/INT8 quantization + accuracy-delta report.
- Jetson-class edge deploy + latency/throughput benchmark.
- Containerized inference image (still subject to §10).
- Live-camera ingest demo.
- `docs/adr/ADR_002_edge_deployment.md` to capture the decision when the gate
  opens.

### 15.3 Honesty note

This is a portfolio-grade engineering-pattern track, not a fab-deployment claim.
It must not be presented as implemented until items land.
