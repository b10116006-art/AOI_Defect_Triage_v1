"""Single-image inference that emits the B Project detection JSON contract.

Output schema matches docs/core/B_PROJECT_BRIEF.md §4.3.
"""
import argparse
import json
import time
import uuid
from datetime import datetime, timezone

from ultralytics import YOLO

DEFAULT_WEIGHTS = "runs/detect/models/b_yolo/roboflow_wafer_v12/weights/best.pt"
MODEL_NAME = "yolo_aoi_camera"
MODEL_VERSION = "yolo_aoi_v1"
SCHEMA_VERSION = "v1"


_MODELS: dict = {}


def run_inference(
    image_path: str,
    weights: str = DEFAULT_WEIGHTS,
    image_id: str = "img_demo",
    lot_id=None,
    wafer_id=None,
    trigger_id=None,
    conf: float = 0.25,
) -> dict:
    model = _MODELS.get(weights)
    if model is None:
        model = YOLO(weights)
        _MODELS[weights] = model

    t0 = time.time()
    result = model(image_path, conf=conf, verbose=False)[0]
    elapsed_ms = (time.time() - t0) * 1000.0

    detections = []
    for box in result.boxes:
        x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]
        detections.append({
            "defect_class": result.names[int(box.cls[0])],
            "confidence": round(float(box.conf[0]), 4),
            "bbox": [round(x1), round(y1), round(x2), round(y2)],
            "bbox_format": "xyxy",
        })

    # Contract stability: all keys always present, even when value is None.
    return {
        "image_id": image_id,
        "trigger_id": trigger_id,
        "lot_id": lot_id,
        "wafer_id": wafer_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "detections": detections,
        "ng_flag": len(detections) > 0,
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "request_id": str(uuid.uuid4()),
        "processing_time_ms": round(elapsed_ms, 2),
        "schema_version": SCHEMA_VERSION,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--weights", default=DEFAULT_WEIGHTS)
    parser.add_argument("--image-id", default="img_demo")
    parser.add_argument("--lot-id", default=None)
    parser.add_argument("--wafer-id", default=None)
    parser.add_argument("--trigger-id", default=None)
    parser.add_argument("--conf", type=float, default=0.25)
    args = parser.parse_args()

    payload = run_inference(
        image_path=args.image,
        weights=args.weights,
        image_id=args.image_id,
        lot_id=args.lot_id,
        wafer_id=args.wafer_id,
        trigger_id=args.trigger_id,
        conf=args.conf,
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
