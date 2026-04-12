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
