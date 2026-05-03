"""FastAPI wrapper around predict.run_inference — B8 AOI Evidence Service.

Exposes POST /predict returning the B Project detection JSON contract
(docs/core/B_PROJECT_BRIEF.md §4.3) verbatim from run_inference().

Run locally from the project root:
    uvicorn src.b_yolo.api:app --reload --port 8000

Environment:
    AOI_WEIGHTS_PATH — overrides the YOLO weights file used at inference.
                       Falls back to predict.DEFAULT_WEIGHTS when unset.
"""
import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .predict import DEFAULT_WEIGHTS, run_inference

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("aoi.evidence")

WEIGHTS_PATH = os.environ.get("AOI_WEIGHTS_PATH", DEFAULT_WEIGHTS)
if not Path(WEIGHTS_PATH).is_file():
    raise RuntimeError(
        f"AOI weights file not found at '{WEIGHTS_PATH}'. "
        f"Set AOI_WEIGHTS_PATH or place weights at the default location "
        f"({DEFAULT_WEIGHTS})."
    )

app = FastAPI(title="AOI Evidence Service", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


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
        payload = run_inference(
            image_path=req.image_path,
            weights=WEIGHTS_PATH,
            image_id=req.image_id,
            lot_id=req.lot_id,
            wafer_id=req.wafer_id,
            trigger_id=req.trigger_id,
            conf=req.conf,
        )
    except FileNotFoundError as exc:
        logger.warning(
            "predict: image not found image_id=%s detail=%s",
            req.image_id, exc,
        )
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("predict: inference failed image_id=%s", req.image_id)
        raise HTTPException(
            status_code=500,
            detail=f"inference failed: {type(exc).__name__}",
        )

    logger.info(
        "predict: image_id=%s wafer_id=%s processing_time_ms=%s model_version=%s",
        payload.get("image_id"),
        payload.get("wafer_id"),
        payload.get("processing_time_ms"),
        payload.get("model_version"),
    )
    return payload
