"""Train a YOLOv8 baseline on the Roboflow wafer defect dataset.

MVP rules:
    - default hyperparameters, no tuning
    - small model (yolov8n) so it runs on CPU or a single GPU
    - goal is pipeline correctness, not mAP
"""
import argparse
from pathlib import Path

from ultralytics import YOLO

DEFAULT_DATA = "data/processed/roboflow_wafer_yolo/data.yaml"
DEFAULT_PROJECT = "models/b_yolo"
DEFAULT_NAME = "roboflow_wafer_v1"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=DEFAULT_DATA)
    parser.add_argument("--weights", default="yolov8n.pt")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument("--name", default=DEFAULT_NAME)
    args = parser.parse_args()

    if not Path(args.data).exists():
        raise SystemExit(
            f"dataset.yaml not found at {args.data}\n"
            f"Run: py -3.11 -m src.b_yolo.prepare_roboflow_wafer  first."
        )

    model = YOLO(args.weights)
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=args.project,
        name=args.name,
    )


if __name__ == "__main__":
    main()
