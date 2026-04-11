You are working on AOI_Defect_Triage_v1 only.

Current state:
- Phase 1 planning is approved
- We are now ready for minimal implementation
- Keep this subproject independent from MES runtime

Important rules:
- Before editing, explain impacted files, purpose, and user-visible effect in plain language
- Minimal diff only
- No API
- No DB
- No UI
- No LLM
- No Docker
- No integration work yet

Please implement Phase 1 now.

Approved scope:
1. create the folder structure
2. create:
   - src/prepare_data.py
   - src/train.py
   - src/evaluate.py
   - src/infer.py
   - requirements.txt
   - README_phase1.md
3. assume raw dataset file path:
   - data/raw/LSWMD.pkl
4. keep raw data untouched
5. write processed outputs to:
   - data/processed/train
   - data/processed/val
   - data/processed/test

Implementation style:
- simple PyTorch baseline only
- readable code
- no over-engineering
- clear console output
- save model weights and evaluation report

Before writing code, first show:
- impacted files
- purpose of each file
- expected user-visible effect

Then proceed with implementation.
