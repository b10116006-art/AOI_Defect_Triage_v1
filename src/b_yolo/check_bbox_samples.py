"""Draw YOLO bboxes on sampled images for visual sanity check.

Reads processed dataset, picks random images, overlays bounding boxes
with class labels, and saves annotated copies to runs/sanity_check/.
Does NOT train anything.
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

import cv2
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = REPO_ROOT / "data" / "processed" / "roboflow_wafer_yolo"
OUTPUT_DIR = REPO_ROOT / "runs" / "sanity_check"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

COLORS = [
    (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0),
    (255, 0, 255), (0, 255, 255), (128, 255, 0),
]


def load_class_names() -> list[str]:
    yaml_path = PROCESSED_DIR / "data.yaml"
    with yaml_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg["names"]


def parse_yolo_labels(label_path: Path) -> list[tuple[int, float, float, float, float]]:
    boxes = []
    for i, line in enumerate(label_path.read_text(encoding="utf-8").strip().splitlines()):
        parts = line.strip().split()
        if len(parts) < 5:
            print(f"  WARNING: {label_path.name} line {i}: expected >=5 fields, got {len(parts)}")
            continue
        try:
            cls_id = int(parts[0])
            cx, cy, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
            boxes.append((cls_id, cx, cy, w, h))
        except ValueError:
            print(f"  WARNING: {label_path.name} line {i}: parse error")
    return boxes


def draw_boxes(img_path: Path, label_path: Path, names: list[str], out_path: Path) -> None:
    img = cv2.imread(str(img_path))
    if img is None:
        print(f"  WARNING: cannot read image {img_path}")
        return

    ih, iw = img.shape[:2]

    if not label_path.exists():
        print(f"  WARNING: label not found {label_path.name} — saving image without boxes")
        cv2.imwrite(str(out_path), img)
        return

    boxes = parse_yolo_labels(label_path)
    for cls_id, cx, cy, w, h in boxes:
        x1 = int((cx - w / 2) * iw)
        y1 = int((cy - h / 2) * ih)
        x2 = int((cx + w / 2) * iw)
        y2 = int((cy + h / 2) * ih)
        color = COLORS[cls_id % len(COLORS)]
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        label = names[cls_id] if cls_id < len(names) else f"cls_{cls_id}"
        cv2.putText(img, label, (x1, max(y1 - 6, 12)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

    cv2.imwrite(str(out_path), img)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="train")
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)

    names = load_class_names()
    print(f"[classes] nc={len(names)} names={names}")

    img_dir = PROCESSED_DIR / args.split / "images"
    lbl_dir = PROCESSED_DIR / args.split / "labels"
    if not img_dir.exists():
        raise SystemExit(f"Image dir not found: {img_dir}")

    imgs = sorted(p for p in img_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS)
    if not imgs:
        raise SystemExit(f"No images found in {img_dir}")

    picks = random.sample(imgs, min(args.count, len(imgs)))

    out_dir = OUTPUT_DIR / args.split
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[sample] {len(picks)} images from {args.split}\n")
    for img_path in picks:
        lbl_path = lbl_dir / (img_path.stem + ".txt")
        out_path = out_dir / img_path.name
        print(f"  in:  {img_path}")
        print(f"  lbl: {lbl_path}{'' if lbl_path.exists() else '  (MISSING)'}")
        draw_boxes(img_path, lbl_path, names, out_path)
        print(f"  out: {out_path}\n")

    print(f"[done] {len(picks)} annotated images saved to {out_dir}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
