# CLAUDE_PHASE2_API_PROMPT.md

Use this prompt in Claude for the next implementation step.

---

You are working on `AOI_Defect_Triage_v1`.

Role:
Architect-minded implementation assistant.

Current repo status:
- Phase 1 completed
- preprocessing works
- CNN training works
- evaluation works
- infer.py works
- structured JSON contract already exists
- repo is on GitHub
- this repo is intended to become the Vision Layer of a larger AI MES Copilot system

Current task:
Implement **Phase 2 — FastAPI Service Layer**

Important rules:
- Minimal diff only
- Do NOT touch training logic unless strictly required
- Do NOT rewrite the model
- Do NOT break the current JSON output contract
- Keep AOI independent from MES runtime
- Design so future MES integration is easy
- No Docker, no Kubernetes, no over-engineering
- This is for demo + interview + future integration safety

Required deliverables:
1. Create `src/api.py`
2. Add a FastAPI endpoint:
   - `POST /predict`
3. Input:
   - image file upload
   - optional metadata fields:
     - `image_id`
     - `machine_id`
     - `lot_id`
     - `layer`
4. Output:
   - return the SAME JSON contract as current `infer.py`
   - append:
     - `request_id`
     - `processing_time_ms`
5. Reuse current inference logic as much as possible
6. Keep path handling clean and non-hardcoded
7. Add the minimal documentation update needed to `docs/README_phase1.md` or create a short API usage doc if cleaner

Before editing, first show:
- impacted files
- purpose of each file
- user-visible effect
- whether any existing file needs a minimal helper refactor

After implementation, provide:
- full `uvicorn` run command
- sample `curl` request
- explanation of how this service can later connect to the MES system
