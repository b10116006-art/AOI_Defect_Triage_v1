"""B8.3 baseline analysis — read-only summary of results/b8_3_baseline.json.

Produces a human-readable text report covering:
  - per-class detection count
  - confidence distribution (min / mean / median / max + bucket histogram)
  - low-confidence detections (below --low-conf, default 0.5)
  - ng_count summary

Does NOT touch the model, the API, or the §4.3 JSON contract. Read-only.

Run from the project root:
    python -m src.b_yolo.analyze_baseline
"""
import argparse
import json
import statistics
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = PROJECT_ROOT / "results" / "b8_3_baseline.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "results" / "b8_3_analysis.txt"
DEFAULT_LOW_CONF = 0.5

CONF_BUCKETS = [(0.0, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 0.9), (0.9, 1.0001)]


def fmt(x, n=4):
    return f"{x:.{n}f}" if x is not None else "n/a"


def analyze(record: dict, low_conf: float, input_path: str) -> str:
    predictions = record.get("predictions") or []
    image_count = record.get("image_count", len(predictions))

    ng_count = sum(1 for p in predictions if p.get("ng_flag"))
    ok_count = image_count - ng_count
    ng_ratio = (ng_count / image_count) if image_count else 0.0

    flat = []
    for p in predictions:
        for d in p.get("detections") or []:
            flat.append(
                (
                    p.get("image_id"),
                    d.get("defect_class"),
                    float(d.get("confidence", 0.0)),
                )
            )
    detection_count = len(flat)

    class_counter = Counter(c for _, c, _ in flat)

    confs = [c for _, _, c in flat]
    if confs:
        conf_min = min(confs)
        conf_max = max(confs)
        conf_mean = statistics.fmean(confs)
        conf_median = statistics.median(confs)
    else:
        conf_min = conf_max = conf_mean = conf_median = None

    buckets = []
    for lo, hi in CONF_BUCKETS:
        n = sum(1 for c in confs if lo <= c < hi)
        buckets.append((lo, hi, n))

    low = sorted(
        [(img, cls, c) for img, cls, c in flat if c < low_conf],
        key=lambda x: x[2],
    )

    lines = []
    lines.append("B8.3 baseline analysis")
    lines.append("=" * 60)
    lines.append(f"input               : {input_path}")
    lines.append(f"dataset_version     : {record.get('dataset_version')}")
    lines.append(f"annotation_spec_ver : {record.get('annotation_spec_version')}")
    lines.append(f"model_version       : {record.get('model_version')}")
    lines.append(f"eval_version        : {record.get('eval_version')}")
    lines.append(f"baseline_timestamp  : {record.get('timestamp')}")
    lines.append(f"low_conf_threshold  : {low_conf}")
    lines.append(f"schema_check_passed : {record.get('schema_check_passed')}")
    lines.append("")

    lines.append("ng_count summary")
    lines.append("-" * 60)
    lines.append(f"image_count     = {image_count}")
    lines.append(f"ng_count        = {ng_count}")
    lines.append(f"ok_count        = {ok_count}")
    lines.append(f"ng_ratio        = {fmt(ng_ratio, 4)}")
    lines.append(f"detection_count = {detection_count}")
    lines.append(
        "note: per B_PROJECT_BRIEF §10.7, a future ng_count drop without"
    )
    lines.append(
        "a documented reason is treated as a suspected false-negative"
    )
    lines.append("regression, not a quality improvement.")
    lines.append("")

    lines.append("per-class detection count")
    lines.append("-" * 60)
    if class_counter:
        for cls, n in sorted(class_counter.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append(f"{cls:<20s} {n}")
    else:
        lines.append("(no detections)")
    lines.append("")

    lines.append("confidence distribution")
    lines.append("-" * 60)
    lines.append(f"min    = {fmt(conf_min)}")
    lines.append(f"mean   = {fmt(conf_mean)}")
    lines.append(f"median = {fmt(conf_median)}")
    lines.append(f"max    = {fmt(conf_max)}")
    lines.append("")
    lines.append("bucket counts (half-open; final bucket is inclusive of 1.0)")
    for lo, hi, n in buckets:
        hi_disp = 1.0 if hi > 1.0 else hi
        lines.append(f"  [{lo:.1f}, {hi_disp:.1f})  {n}")
    lines.append("")

    lines.append(f"low-confidence detections (confidence < {low_conf})")
    lines.append("-" * 60)
    if low:
        lines.append(f"{'conf':<6s}  {'class':<20s}  image_id")
        for img, cls, c in low:
            lines.append(f"{fmt(c, 4):<6s}  {cls:<20s}  {img}")
    else:
        lines.append("(none)")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="B8.3 baseline analysis (read-only)."
    )
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--low-conf", type=float, default=DEFAULT_LOW_CONF)
    args = parser.parse_args()

    record = json.loads(Path(args.input).read_text(encoding="utf-8"))
    report = analyze(record, args.low_conf, args.input)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    print(report)
    print(f"--- written to {out_path}")


if __name__ == "__main__":
    main()
