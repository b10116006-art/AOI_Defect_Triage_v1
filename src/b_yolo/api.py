"""FastAPI wrapper around predict.run_inference — B8 AOI Evidence Service.

Exposes POST /predict returning the B Project detection JSON contract
(docs/core/B_PROJECT_BRIEF.md §4.3) verbatim from run_inference().

Run locally from the project root:
    uvicorn src.b_yolo.api:app --reload --port 8000
"""
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .predict import DEFAULT_WEIGHTS, run_inference

app = FastAPI(title="AOI Evidence Service", version="0.1.0")


class PredictRequest(BaseModel):
    image_path: str
    image_id: str = "img_demo"
    lot_id: Optional[str] = None
    wafer_id: Optional[str] = None
    trigger_id: Optional[str] = None
    conf: float = 0.25


@app.post("/predict")
def predict(req: PredictRequest) -> dict:
    try:
        return run_inference(
            image_path=req.image_path,
            weights=DEFAULT_WEIGHTS,
            image_id=req.image_id,
            lot_id=req.lot_id,
            wafer_id=req.wafer_id,
            trigger_id=req.trigger_id,
            conf=req.conf,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
