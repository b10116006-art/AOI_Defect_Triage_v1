"""
api.py

Phase 2 — FastAPI inference service for AOI Defect Triage.

Exposes a single endpoint:
    POST /predict

Request body (JSON):
    {
        "image_base64": "<base64-encoded PNG>",
        "image_id":    "img_0001",      (optional)
        "machine_id":  "AOI_01",        (optional)
        "lot_id":      "LOT_UNKNOWN",   (optional)
        "layer":       "UNKNOWN"        (optional)
    }

Response:
    Locked AOI JSON contract fields (unchanged from infer.py),
    followed by: request_id, processing_time_ms, schema_version.

Run:
    uvicorn src.api:app --reload
"""

import base64
import sys
import time
import uuid
from io import BytesIO
from pathlib import Path

import torch
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from PIL import Image
from pydantic import BaseModel

# Re-use inference helpers from infer.py (same src/ directory)
sys.path.insert(0, str(Path(__file__).parent))
from infer import MODEL_PATH, build_result_dict, load_model, predict

# ---------------------------------------------------------------------------
# App + model initialisation
# ---------------------------------------------------------------------------

app = FastAPI(title="AOI Defect Triage API", version="2.0.0")

_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_model, _classes, _img_size = load_model(MODEL_PATH, _device)


# ---------------------------------------------------------------------------
# Request schema
# ---------------------------------------------------------------------------

class PredictRequest(BaseModel):
    image_base64: str
    image_id:    str = "img_0001"
    machine_id:  str = "AOI_01"
    lot_id:      str = "LOT_UNKNOWN"
    layer:       str = "UNKNOWN"


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@app.post("/predict")
def predict_endpoint(request: PredictRequest):
    # --- decode base64 image ---
    try:
        image_bytes = base64.b64decode(request.image_base64, validate=True)
        # verify() catches truncated / corrupt files; stream is exhausted after call
        Image.open(BytesIO(image_bytes)).verify()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid image: could not decode base64 or open image file."},
        )

    # --- run inference ---
    # predict() calls Image.open() internally, so pass a fresh BytesIO stream
    t0 = time.perf_counter()
    try:
        pred_idx, confidence = predict(BytesIO(image_bytes), _model, _img_size, _device)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Inference failed. Check model and image format."},
        )
    processing_time_ms = round((time.perf_counter() - t0) * 1000, 2)

    # --- build locked contract result ---
    result = build_result_dict(
        request.image_id,
        request.machine_id,
        request.lot_id,
        request.layer,
        _classes,
        pred_idx,
        confidence,
        _img_size,
    )

    # --- append Phase 2 metadata (after locked fields) ---
    result["request_id"]         = str(uuid.uuid4())
    result["processing_time_ms"] = processing_time_ms
    result["schema_version"]     = "v1"

    return result
