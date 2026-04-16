"""Single-image inference that emits the B Project detection JSON contract.

Output schema matches docs/core/B_PROJECT_BRIEF.md §4.3.
"""
import argparse
import json
import time
import uuid
from datetime import datetime, timezone

from ultralytics import YOLO

DEFAULT_WEIGHTS = "models/b_yolo/dagm_v1/weights/best.pt"
MODEL_NAME = "yolo_aoi_camera"
MODEL_VERSION = "yolo_aoi_v1"
SCHEMA_VERSION = "v1"


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

    model = YOLO(args.weights)
    t0 = time.time()
    result = model(args.image, conf=args.conf, verbose=False)[0]
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

    payload = {
        "image_id": args.image_id,
        "trigger_id": args.trigger_id,
        "lot_id": args.lot_id,
        "wafer_id": args.wafer_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "detections": detections,
        "ng_flag": len(detections) > 0,
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "request_id": str(uuid.uuid4()),
        "processing_time_ms": round(elapsed_ms, 2),
        "schema_version": SCHEMA_VERSION,
    }
    # Drop optional fields that were not provided so the payload stays clean.
    payload = {k: v for k, v in payload.items() if v is not None}
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
