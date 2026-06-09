# AOI Defect Triage

## Overview

AOI Defect Triage is an industrial AI portfolio project focused on automated optical inspection (AOI) defect analysis for semiconductor manufacturing. It forms the **Vision Layer** of a larger manufacturing AI architecture, turning inspection images into structured, machine-readable defect information that a downstream system can act on.

The project is organized into two complementary tracks. **Track A** classifies wafer-level defect patterns from the WM-811K wafer-map dataset using a CNN baseline. **Track B** performs camera-image defect detection on the Roboflow Wafer Defect dataset using a YOLOv8 model. The two tracks operate on different physical layers of a fab and share a JSON contract boundary rather than any pixels or model weights.

Beyond model training, the project emphasizes deployment and evidence: a FastAPI service exposes a `POST /predict` endpoint that returns a locked JSON contract, giving a structured output suitable for future integration with downstream manufacturing systems. Engineering decisions are recorded as documentation (e.g., an architecture decision record for the Phase 3 detection feasibility study) so the reasoning behind the roadmap is traceable.

## Track A — Wafer Map Classification

| Field               | Value        |
| ------------------- | ------------ |
| Dataset             | WM-811K      |
| Model               | cnn_baseline |
| Classes             | 9            |
| Usable Samples      | 172,950      |
| Validation Accuracy | 96.40%       |
| Test Accuracy       | 89.28%       |

## Track B — AOI Camera Defect Detection

| Field   | Value                 |
| ------- | --------------------- |
| Dataset | Roboflow Wafer Defect |
| Model   | YOLOv8                |
| Classes | 7                     |
| mAP50   | 0.715                 |

## API Contract

A FastAPI service exposes a single inference endpoint, `POST /predict`, which returns a locked JSON contract describing the predicted defect for an input image.

A complete example of the contract output is provided in:

* [`docs/json_contract_example.json`](json_contract_example.json)

## Baseline Metrics

Baseline evaluation metrics for both tracks are recorded in:

* [`docs/baseline_metrics.json`](baseline_metrics.json)

## Current Status

**Completed**

* Phase 1 — CNN classification (WM-811K)
* Phase 2 — FastAPI deployment (`POST /predict`)
* DG2 baseline review work

**Documented**

* Phase 3 — detection feasibility evaluated and closed as not feasible for the current roadmap (architecture decision record)

**Next**

* Stage A — Edge AI (ONNX → TensorRT → Jetson)
* Phase 4 — VQA-style Defect Explanation
* Phase 5 — Wafer Drift Tracking
* Phase 6 — Diffusion Augmentation
