# ADR-001
Phase 3 Detection Not Feasible

Status:
Accepted

Date:
2026-06-03

## Context

The AOI Defect Triage Vision Layer has progressed through two established phases:

- **Phase 1:** WM-811K CNN classification — wafer maps are classified into defect
  pattern categories.
- **Phase 2:** A FastAPI service exposing the classifier behind a locked JSON
  contract.

A natural next question for the roadmap was whether **object detection** (drawing
bounding boxes around defects on a wafer map) could add value beyond
classification. **Phase 3** was scoped as a detection feasibility study to answer
that question before committing engineering effort to a detector.

This ADR records the outcome of that study.

## Decision

Wafer-map object detection was **evaluated** and is **closed as not feasible for
the current roadmap**.

Detection on wafer maps was assessed against the existing classification approach.
The conclusion is that wafer maps are **pattern distributions, not
natural-image object localization targets**. Classification remains the better
aligned approach for the current task, so the roadmap continues on the
classification track rather than adding a detection stage.

This decision closes detection **for the current roadmap only**. Detection is
**not removed forever** — it may be revisited if the task definition or data
characteristics change.

## Evidence

The feasibility study surfaced three consistent problems when framing wafer maps
as a detection problem:

- **Weak localization meaning** — a "location" on a wafer map does not carry the
  same semantic weight as an object location in a natural image. The defect
  signal is distributed across the map as a spatial pattern rather than
  concentrated in a discrete, localizable object.
- **Ambiguous object boundaries** — defect patterns blend into the surrounding
  die grid without crisp edges, so bounding-box annotations are subjective and
  hard to define consistently.
- **Classification is better aligned with the task** — the operational question
  ("what kind of defect pattern is this?") maps directly onto a classification
  output and does not require per-object boxes.

## Alternatives Considered

- **Train a wafer-map object detector (Phase 3 as a build).** Rejected for the
  current roadmap because of the weak localization meaning and ambiguous object
  boundaries described above; the annotation effort would not produce a
  well-posed detection target.
- **Continue with classification (Phases 1–2).** Selected. Classification is
  better aligned with the task and is already established and serving through the
  locked JSON contract.

## Consequences

- The roadmap continues on the classification track; no detection stage is added.
- No detector model, training pipeline, or detection-specific contract is
  introduced.
- The existing Phase 1 classifier and Phase 2 FastAPI + locked JSON contract
  remain the system of record for defect triage.
- The feasibility study is preserved as documentation so the reasoning does not
  need to be re-derived if the question is raised again.

## Future Direction

Detection is closed for the current roadmap, not abandoned. It may be reconsidered
if, for example, the data representation changes (e.g., higher-resolution or
image-like inputs where objects become well-defined) or if a new task emerges that
genuinely requires localization. Until such a change, classification remains the
aligned approach.
