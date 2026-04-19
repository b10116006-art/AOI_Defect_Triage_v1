"""Convert DAGM 2007 raw layout into YOLO detection format.

Input layout (data/raw/DAGM2007):
    Class1/Train/*.PNG
    Class1/Train/Label/*_label.PNG
    Class1/Test/*.PNG
    Class1/Test/Label/*_label.PNG
    Class2/...

Output layout (data/processed/dagm_yolo):
    images/train/<classN>_<stem>.png
    images/val/<classN>_<stem>.png
    labels/train/<classN>_<stem>.txt
    labels/val/<classN>_<stem>.txt
    dataset.yaml

Notes:
    - DAGM defect masks mark defective pixels with non-zero values.
    - Each defective image has exactly one ellipse → one bbox per file (MVP).
    - Defect-free images are skipped at MVP stage (detection only sees positives).
    - Mask → bbox conversion is semantically valid here because the underlying
      pixels really are defect pixels — unlike WM-811K, where pixel == 255 means
      "failing die" and bbox derivation was rejected (see A Project Phase 3 log).
"""
from pathlib import Path
import shutil

import numpy as np
from PIL import Image

NUM_CLASSES = 10
RAW_ROOT = Path("data/raw/DAGM2007")
OUT_ROOT = Path("data/processed/dagm_yolo")


def mask_to_yolo_bbox(mask_path: Path):
    """Return YOLO-normalized (cx, cy, w, h) for a single-defect mask, or None."""
    mask = np.array(Image.open(mask_path).convert("L"))
    ys, xs = np.where(mask > 0)
    if len(xs) == 0:
        return None
    h_img, w_img = mask.shape
    x_min, x_max = int(xs.min()), int(xs.max())
    y_min, y_max = int(ys.min()), int(ys.max())
    cx = (x_min + x_max) / 2.0 / w_img
    cy = (y_min + y_max) / 2.0 / h_img
    w = (x_max - x_min) / w_img
    h = (y_max - y_min) / h_img
    return cx, cy, w, h


def process_split(class_idx: int, split_src: Path, split_name: str) -> int:
    """Convert one class/split. split_name is 'train' or 'val'."""
    label_dir = split_src / "Label"
    if not label_dir.exists():
        return 0

    img_out = OUT_ROOT / "images" / split_name
    lbl_out = OUT_ROOT / "labels" / split_name
    img_out.mkdir(parents=True, exist_ok=True)
    lbl_out.mkdir(parents=True, exist_ok=True)

    count = 0
    for label_file in sorted(label_dir.glob("*_label.PNG")):
        stem = label_file.stem.replace("_label", "")
        img_file = split_src / f"{stem}.PNG"
        if not img_file.exists():
            continue
        bbox = mask_to_yolo_bbox(label_file)
        if bbox is None:
            continue
        cx, cy, w, h = bbox
        out_stem = f"class{class_idx + 1}_{stem}"
        shutil.copy(img_file, img_out / f"{out_stem}.png")
        with open(lbl_out / f"{out_stem}.txt", "w") as f:
            f.write(f"{class_idx} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")
        count += 1
    return count


def write_dataset_yaml() -> None:
    yaml_path = OUT_ROOT / "dataset.yaml"
    names_block = "\n".join(f"  {i}: class{i + 1}" for i in range(NUM_CLASSES))
    yaml_path.write_text(
        f"path: {OUT_ROOT.resolve().as_posix()}\n"
        f"train: images/train\n"
        f"val: images/val\n"
        f"nc: {NUM_CLASSES}\n"
        f"names:\n{names_block}\n"
    )
    print(f"Wrote {yaml_path}")


def main() -> None:
    if not RAW_ROOT.exists():
        raise SystemExit(
            f"DAGM raw root not found: {RAW_ROOT}\n"
            f"Place DAGM 2007 under {RAW_ROOT} (Class1..Class10)."
        )
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    totals = {"train": 0, "val": 0}
    for i in range(NUM_CLASSES):
        cls_dir = RAW_ROOT / f"Class{i + 1}"
        if not cls_dir.exists():
            print(f"[skip] {cls_dir} missing")
            continue
        totals["train"] += process_split(i, cls_dir / "Train", "train")
        totals["val"] += process_split(i, cls_dir / "Test", "val")
        print(f"Class{i + 1}: done")

    print(f"Totals: train={totals['train']}, val={totals['val']}")
    write_dataset_yaml()


if __name__ == "__main__":
    main()
