# AOI Phase 1 — Approved Plan Snapshot

## Scope
Build a minimal CNN classification baseline using the WM-811K / LSWMD wafer map dataset.

## Dataset placement
- Raw file: `data/raw/LSWMD.pkl`
- Keep raw file untouched
- Processed outputs:
  - `data/processed/train/`
  - `data/processed/val/`
  - `data/processed/test/`

## Minimal implementation target
- `src/prepare_data.py`
- `src/train.py`
- `src/evaluate.py`
- `src/infer.py` (optional but recommended)
- `requirements.txt`
- `README_phase1.md`

## Notes
- Keep file count small
- No API
- No DB
- No UI
- No MES integration
- No Docker
- No broad framework setup

## Validation
- processed folders created
- no empty class folders
- training runs end-to-end
- validation metrics logged
- confusion matrix saved
- model weights saved
- rerun instructions documented

## Practical review adjustment
The original plan's fixed `> 80% overall accuracy` target should be treated as a soft baseline target, not a hard gate, because WM-811K class imbalance can make one fixed threshold misleading.
