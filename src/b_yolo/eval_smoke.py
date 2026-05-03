"""B8.3 Evaluation Smoke Loop — minimal reproducible baseline run.

Runs predict.run_inference() over a fixed gold-set manifest (the DG-2
seed defined in src/b_yolo/data/eval_gold_manifest_v1.txt), validates
each payload against the §4.3 detection contract, and writes a single
baseline record JSON to results/.

This is NOT a performance evaluation. Its purpose is:
  - prove the inference path is reproducible run-to-run
  - lock a baseline (predictions + minimal counts) that future
    Enhancement trials must measure against (B_PROJECT_BRIEF §8.4)
  - enforce a schema regression check on every run

Run from the project root:
    python -m src.b_yolo.eval_smoke
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from .predict import MODEL_VERSION, run_inference

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = (
    PROJECT_ROOT / "src" / "b_yolo" / "data" / "eval_gold_manifest_v1.txt"
)
DEFAULT_OUTPUT = PROJECT_ROOT / "results" / "b8_3_baseline.json"

REQUIRED_PAYLOAD_KEYS = (
    "image_id",
    "trigger_id",
    "lot_id",
    "wafer_id",
    "timestamp",
    "detections",
    "ng_flag",
    "model_name",
    "model_version",
    "request_id",
    "processing_time_ms",
    "schema_version",
)


def load_manifest(path: Path):
    paths = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        candidate = Path(line)
        if not candidate.is_absolute():
            candidate = PROJECT_ROOT / candidate
        paths.append(candidate)
    return paths


def schema_check(payload: dict):
    errors = []
    for key in REQUIRED_PAYLOAD_KEYS:
        if key not in payload:
            errors.append(f"missing key: {key}")
    detections = payload.get("detections")
    if not isinstance(detections, list):
        errors.append("detections is not a list")
    else:
        for i, det in enumerate(detections):
            if det.get("bbox_format") != "xyxy":
                errors.append(f"detections[{i}].bbox_format != 'xyxy'")
    return (len(errors) == 0, errors)


def run_eval_smoke(
    manifest: Path,
    output: Path,
    dataset_version: str,
    annotation_spec_version: str,
    eval_version: str,
) -> dict:
    images = load_manifest(manifest)
    predictions = []
    schema_errors = []
    detection_count = 0
    ng_count = 0

    for image_path in images:
        if not image_path.is_file():
            schema_errors.append({
                "image": str(image_path),
                "errors": ["image file not found"],
            })
            continue
        try:
            payload = run_inference(
                image_path=str(image_path),
                image_id=image_path.name,
            )
        except Exception as exc:
            schema_errors.append({
                "image": str(image_path),
                "errors": [f"inference error: {type(exc).__name__}: {exc}"],
            })
            continue

        ok, errs = schema_check(payload)
        if not ok:
            schema_errors.append({"image": str(image_path), "errors": errs})

        detection_count += len(payload.get("detections") or [])
        if payload.get("ng_flag"):
            ng_count += 1
        predictions.append(payload)

    record = {
        "dataset_version": dataset_version,
        "annotation_spec_version": annotation_spec_version,
        "model_version": MODEL_VERSION,
        "eval_version": eval_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "image_count": len(images),
        "predictions": predictions,
        "schema_check_passed": len(schema_errors) == 0,
        "schema_errors": schema_errors,
        "metrics": {
            "image_count": len(images),
            "detection_count": detection_count,
            "ng_count": ng_count,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(
        description="B8.3 evaluation smoke loop — writes a fixed baseline record."
    )
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--dataset-version", default="roboflow_wafer_v2_dg2_v1")
    parser.add_argument("--annotation-spec-version", default="draft_v0")
    parser.add_argument("--eval-version", default="b8_3_smoke_v1")
    args = parser.parse_args()

    record = run_eval_smoke(
        manifest=Path(args.manifest),
        output=Path(args.output),
        dataset_version=args.dataset_version,
        annotation_spec_version=args.annotation_spec_version,
        eval_version=args.eval_version,
    )
    print(
        f"B8.3 baseline written to {args.output}\n"
        f"  image_count        = {record['image_count']}\n"
        f"  detection_count    = {record['metrics']['detection_count']}\n"
        f"  ng_count           = {record['metrics']['ng_count']}\n"
        f"  schema_check_passed= {record['schema_check_passed']}"
    )


if __name__ == "__main__":
    main()
