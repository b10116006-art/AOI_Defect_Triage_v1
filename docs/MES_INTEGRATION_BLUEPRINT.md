# MES_INTEGRATION_BLUEPRINT.md
_Last updated: 2026-04-09_

## 1. Purpose

This document defines the **safe future integration path** between:
- `AOI_Defect_Triage_v1`
- `AI MES Copilot`
- future `RAG / LLM decision layer`

The goal is to prevent:
- brittle code coupling
- premature integration
- broken contracts
- duplicate logic across repos

---

## 2. Design Principle

The AOI repo should integrate with MES through a **service/data contract boundary**, not by directly importing AOI training code into the MES runtime.

### Recommended boundary
AOI API → JSON payload → MES integration service

### Avoid
- direct runtime import of `train.py`, `prepare_data.py`, or model internals from the MES repo
- hardcoded file exchange
- manual copy/paste of predictions

---

## 3. Future Integration Flow

## Stage A — AOI predicts
AOI service receives:
- image
- machine metadata
- lot metadata
- layer metadata

AOI returns:
- defect class
- confidence
- bbox
- ng_flag
- timestamp
- metadata fields

## Stage B — MES enriches
MES service adds:
- machine state
- recent scrap trend
- layer KPI
- anomaly context
- recent maintenance / issue context

## Stage C — Unified case object
A merged case object is created, for example:

```json
{
  "aoi": {},
  "mes": {},
  "case_id": "...",
  "created_at": "...",
  "severity": "...",
  "status": "open"
}
```

## Stage D — RAG / LLM reasoning
The case object is sent to:
- retriever
- SOP knowledge
- similar issue lookup
- LLM decision layer

LLM generates:
- explanation
- root-cause hypothesis
- next action recommendation

---

## 4. What AOI Should Own vs What MES Should Own

### AOI repo should own
- image preprocessing for AOI inference
- CV model inference
- AOI-specific output contract
- Vision-layer API serving

### MES repo should own
- process telemetry
- machine state
- scrap/KPI context
- case lifecycle
- action workflow
- dashboard/ops UI
- workflow continuity

### RAG/LLM layer should own
- retrieval
- knowledge grounding
- explanation generation
- action suggestion
- evidence synthesis

---

## 5. Contract Recommendation

### AOI Output Contract
Keep current AOI output stable.

### MES Enriched Case Contract
Define later in MES repo after Phase 2 API is stable.

Recommended rule:
- AOI contract should be versioned
- MES should consume AOI contract as-is, then enrich rather than mutate destructively

---

## 6. Recommended Development Order

1. AOI Phase 2 API
2. Testable AOI service contract
3. MES-side AOI ingestion endpoint or adapter
4. Unified case object schema
5. RAG grounding over unified case
6. LLM decision layer

This order minimizes integration breakage.

---

## 7. What to Avoid Right Now

Do not do these yet:
- directly merge repos
- copy AOI code into MES repo
- add MongoDB writes inside AOI service before contract is stable
- wire MQTT directly into AOI repo
- redesign AOI output fields casually

---

## 8. Demo-safe Story

For demo and interview, the correct architecture story is:
- AOI acts as the Vision Layer
- MES acts as the Process Layer
- RAG acts as the Knowledge Layer
- LLM acts as the Decision Layer

Together they form:

**image → process → reasoning → decision**
