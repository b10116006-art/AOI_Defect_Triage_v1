"""Prepare the Roboflow wafer defect dataset for YOLO training.

Reads the raw Roboflow export (YOLOv11 format) from
`data/raw/roboflow_wafer/` and produces a clean copy under
`data/processed/roboflow_wafer_yolo/` with absolute paths in data.yaml
so Ultralytics works regardless of the current working directory.

Pipeline:
    1. If the extracted folder is missing but the zip exists, unzip it.
    2. Copy train/valid/test images and labels into the processed tree.
    3. Write a corrected data.yaml with absolute paths.
    4. Validate per-split image/label counts and sample 5 train images
       to confirm each has a matching label file.

This script does NOT train anything.
"""
from __future__ import annotations

import argparse
import random
import shutil
import sys
import zipfile
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_ROOT / "data" / "raw" / "roboflow_wafer"
RAW_EXTRACTED = RAW_DIR / "Wafer Defect.v2-final.yolov11"
RAW_ZIP = RAW_DIR / "Wafer Defect.v2-final.yolov11.zip"
PROCESSED_DIR = REPO_ROOT / "data" / "processed" / "roboflow_wafer_yolo"

SPLITS = ("train", "valid", "test")
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def ensure_extracted() -> Path:
    if RAW_EXTRACTED.exists():
        return RAW_EXTRACTED
    if not RAW_ZIP.exists():
        raise SystemExit(
            f"Neither extracted folder nor zip found under {RAW_DIR}.\n"
            f"Expected one of:\n  {RAW_EXTRACTED}\n  {RAW_ZIP}"
        )
    print(f"[unzip] {RAW_ZIP.name} -> {RAW_DIR}")
    with zipfile.ZipFile(RAW_ZIP) as zf:
        zf.extractall(RAW_DIR)
    if not RAW_EXTRACTED.exists():
        raise SystemExit(
            f"Unzip finished but {RAW_EXTRACTED} still missing. "
            f"Check the zip's internal folder name."
        )
    return RAW_EXTRACTED


def copy_split(src_root: Path, split: str, dst_root: Path) -> tuple[int, int]:
    src_img = src_root / split / "images"
    src_lbl = src_root / split / "labels"
    if not src_img.exists() or not src_lbl.exists():
        raise SystemExit(f"Missing {split} images/labels under {src_root}")

    dst_img = dst_root / split / "images"
    dst_lbl = dst_root / split / "labels"
    dst_img.mkdir(parents=True, exist_ok=True)
    dst_lbl.mkdir(parents=True, exist_ok=True)

    n_img = 0
    for p in src_img.iterdir():
        if p.suffix.lower() in IMAGE_EXTS and p.is_file():
            shutil.copy2(p, dst_img / p.name)
            n_img += 1

    n_lbl = 0
    for p in src_lbl.iterdir():
        if p.suffix.lower() == ".txt" and p.is_file():
            shutil.copy2(p, dst_lbl / p.name)
            n_lbl += 1

    return n_img, n_lbl


def load_class_names(src_root: Path) -> list[str]:
    with (src_root / "data.yaml").open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    names = raw.get("names")
    if not isinstance(names, list) or not names:
        raise SystemExit("Roboflow data.yaml has no usable 'names' field.")
    return names


def write_dataset_yaml(dst_root: Path, names: list[str]) -> Path:
    yaml_path = dst_root / "data.yaml"
    payload = {
        "path": str(dst_root.resolve()).replace("\\", "/"),
        "train": "train/images",
        "val": "valid/images",
        "test": "test/images",
        "nc": len(names),
        "names": names,
    }
    with yaml_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)
    return yaml_path


def sample_check(dst_root: Path, split: str = "train", k: int = 5) -> None:
    img_dir = dst_root / split / "images"
    lbl_dir = dst_root / split / "labels"
    imgs = [p for p in img_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS]
    if not imgs:
        print(f"[sample-check] no images in {img_dir}")
        return
    picks = random.sample(imgs, min(k, len(imgs)))
    print(f"[sample-check] random {len(picks)} from {split}:")
    all_ok = True
    for p in picks:
        lbl = lbl_dir / (p.stem + ".txt")
        ok = lbl.exists()
        all_ok = all_ok and ok
        print(f"  {'OK ' if ok else 'MISS'}  {p.name}  ->  {lbl.name}")
    if not all_ok:
        print("[sample-check] WARNING: some sampled images are missing labels.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force", action="store_true",
        help="Wipe processed/roboflow_wafer_yolo before rebuilding.",
    )
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    random.seed(args.seed)

    src_root = ensure_extracted()
    print(f"[src] {src_root}")

    if args.force and PROCESSED_DIR.exists():
        print(f"[clean] removing {PROCESSED_DIR}")
        shutil.rmtree(PROCESSED_DIR)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    names = load_class_names(src_root)
    print(f"[classes] nc={len(names)} names={names}")

    stats: dict[str, tuple[int, int]] = {}
    for split in SPLITS:
        n_img, n_lbl = copy_split(src_root, split, PROCESSED_DIR)
        stats[split] = (n_img, n_lbl)
        print(f"[copy] {split}: images={n_img}  labels={n_lbl}")
        if n_img == 0:
            print(f"  WARNING: {split} has zero images.")
        if n_img != n_lbl:
            # Allow unequal for negative (no-label) samples but warn loudly.
            print(
                f"  NOTE: images != labels for {split} "
                f"({n_img} vs {n_lbl}). Check if intentional."
            )

    yaml_path = write_dataset_yaml(PROCESSED_DIR, names)
    print(f"[yaml] wrote {yaml_path}")

    sample_check(PROCESSED_DIR, split="train", k=5)

    print("\n[summary]")
    for split, (n_img, n_lbl) in stats.items():
        print(f"  {split:<5}  images={n_img:>5}  labels={n_lbl:>5}")
    print(f"  data.yaml -> {yaml_path}")
    print("[done] prepare_roboflow_wafer completed. No training was run.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
