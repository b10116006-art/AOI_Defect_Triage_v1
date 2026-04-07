"""
prepare_data.py

Reads the raw WM-811K wafer map dataset (LSWMD.pkl),
extracts labeled wafer maps, resizes each to 64x64 pixels,
and saves them as PNG images sorted into class subfolders under
data/processed/train/, data/processed/val/, and data/processed/test/.

Run this once before training.

Usage:
    python src/prepare_data.py
"""

import sys
import numpy as np
import pandas as pd
from PIL import Image
from pathlib import Path
from sklearn.model_selection import train_test_split

RAW_PKL    = Path("data/raw/LSWMD.pkl")
OUTPUT_DIR = Path("data/processed")
IMAGE_SIZE = 64

DEFECT_CLASSES = [
    "Center", "Donut", "Edge-Loc", "Edge-Ring",
    "Loc", "Near-full", "Random", "Scratch", "none",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_label(raw_value):
    """
    Normalize the failureType column to a plain string.
    In LSWMD.pkl every value is a 2D numpy ndarray:
        labeled  →  array([['none']], dtype='<U4')   shape (1,1)
        unlabeled→  array([], shape=(0, 0), dtype=float64)
    Returns the class name string, or None if unlabeled / empty.
    """
    if raw_value is None:
        return None
    if isinstance(raw_value, np.ndarray):
        if raw_value.size == 0:
            return None
        label = str(raw_value.flat[0]).strip()
        return label if label and label not in ("nan", "") else None
    # Fallback: plain list or string (defensive, not seen in this dataset)
    if isinstance(raw_value, list):
        if len(raw_value) == 0:
            return None
        inner = raw_value[0]
        label = inner[0] if isinstance(inner, list) and len(inner) > 0 else inner
    else:
        label = raw_value
    label = str(label).strip()
    return label if label and label not in ("nan", "") else None


def extract_split(raw_value):
    """
    Normalize the trianTestLabel column to 'Training' or 'Test'.
    In LSWMD.pkl stored as a 2D numpy ndarray: array([['Training']], dtype='<U8')
    or an empty array for unlabeled rows.
    """
    if isinstance(raw_value, np.ndarray):
        if raw_value.size == 0:
            return ""
        return str(raw_value.flat[0]).strip()
    if isinstance(raw_value, list) and len(raw_value) > 0:
        return str(raw_value[0]).strip()
    return str(raw_value).strip()


def wafermap_to_image(wafer_map):
    """
    Convert a 2D wafer map array to a 64x64 grayscale PIL Image.
    Pixel encoding:
        0 (background) → 0   (black)
        1 (good die)   → 128 (gray)
        2 (defect die) → 255 (white)
    """
    arr = np.asarray(wafer_map, dtype=np.uint8)
    lookup = np.array([0, 128, 255], dtype=np.uint8)
    arr = lookup[np.clip(arr, 0, 2)]
    img = Image.fromarray(arr, mode="L")
    img = img.resize((IMAGE_SIZE, IMAGE_SIZE), Image.NEAREST)
    return img


def save_split(split_name, split_df):
    """Create class subfolders and write one PNG per wafer map."""
    for cls in DEFECT_CLASSES:
        (OUTPUT_DIR / split_name / cls).mkdir(parents=True, exist_ok=True)

    print(f"  Saving {split_name} ({len(split_df)} samples) ...")
    for i, (_, row) in enumerate(split_df.iterrows()):
        img  = wafermap_to_image(row["waferMap"])
        cls  = row["label"]
        path = OUTPUT_DIR / split_name / cls / f"{split_name}_{i:06d}.png"
        img.save(path)
    print(f"  Done.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not RAW_PKL.exists():
        print(f"ERROR: Raw dataset not found at {RAW_PKL.resolve()}")
        print("  Place LSWMD.pkl in data/raw/ and re-run.")
        sys.exit(1)

    print(f"Loading {RAW_PKL} ...")
    df = pd.read_pickle(RAW_PKL)
    print(f"Total rows in dataset : {len(df):,}")

    # --- Label extraction ---------------------------------------------------
    df["label"] = df["failureType"].apply(extract_label)
    df_labeled  = df[df["label"].isin(DEFECT_CLASSES)].copy()
    print(f"Labeled samples       : {len(df_labeled):,}")
    print(f"Unlabeled / skipped   : {len(df) - len(df_labeled):,}")

    print("\nClass distribution:")
    for cls in DEFECT_CLASSES:
        count = (df_labeled["label"] == cls).sum()
        bar   = "#" * (count // 200)
        print(f"  {cls:15s}: {count:6,}  {bar}")

    # --- Train / val / test split -------------------------------------------
    if "trianTestLabel" in df_labeled.columns:   # note: typo is in the original dataset
        df_labeled["split"] = df_labeled["trianTestLabel"].apply(extract_split)
        train_val_df = df_labeled[df_labeled["split"] == "Training"].copy()
        test_df      = df_labeled[df_labeled["split"] == "Test"].copy()
        print(f"\nUsing built-in split: {len(train_val_df):,} train+val  |  {len(test_df):,} test")
    else:
        train_val_df, test_df = train_test_split(
            df_labeled, test_size=0.15, random_state=42, stratify=df_labeled["label"]
        )
        print(f"\nManual split: {len(train_val_df):,} train+val  |  {len(test_df):,} test")

    # Hold out ~15 % of the overall data as validation
    val_fraction = 0.15 / (1.0 - 0.15)
    train_df, val_df = train_test_split(
        train_val_df, test_size=val_fraction, random_state=42,
        stratify=train_val_df["label"]
    )
    print(f"Final split  : {len(train_df):,} train  |  {len(val_df):,} val  |  {len(test_df):,} test")

    # --- Save images --------------------------------------------------------
    print()
    save_split("train", train_df)
    save_split("val",   val_df)
    save_split("test",  test_df)

    print(f"\nData preparation complete.")
    print(f"Output directory: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
