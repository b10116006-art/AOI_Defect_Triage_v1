"""
evaluate.py

Loads the trained CNN model and evaluates it against the held-out test set.
Prints a full report (overall accuracy + per-class accuracy + confusion matrix)
and saves it to results/eval_report.txt.

Usage:
    python src/evaluate.py
"""

import sys
import torch
import numpy as np
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from pathlib import Path
from datetime import datetime

# Re-use WaferCNN from train.py (same src/ directory)
sys.path.insert(0, str(Path(__file__).parent))
from train import WaferCNN

PROCESSED_DIR = Path("data/processed")
MODEL_PATH    = Path("models/cnn_baseline_v1.pth")
RESULTS_DIR   = Path("results")
BATCH_SIZE    = 64


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_confusion_matrix(all_labels, all_preds, num_classes):
    matrix = np.zeros((num_classes, num_classes), dtype=int)
    for true, pred in zip(all_labels, all_preds):
        matrix[true][pred] += 1
    return matrix


def format_report(classes, all_labels, all_preds, model_path, checkpoint):
    conf_matrix = build_confusion_matrix(all_labels, all_preds, len(classes))
    overall_acc = (np.array(all_labels) == np.array(all_preds)).mean()

    lines = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines.append("=" * 60)
    lines.append("  AOI Defect Triage — Phase 1 Evaluation Report")
    lines.append("=" * 60)
    lines.append(f"  Generated : {ts}")
    lines.append(f"  Model     : {model_path.name}  (best epoch: {checkpoint['epoch']})")
    lines.append(f"  Val acc at save time : {checkpoint['val_acc']:.2%}")
    lines.append(f"  Test samples : {len(all_labels):,}")
    lines.append("")
    lines.append(f"  OVERALL TEST ACCURACY : {overall_acc:.2%}")
    lines.append("")

    lines.append("  Per-Class Accuracy:")
    lines.append(f"  {'Class':15s}  {'Correct':>7}  {'Total':>7}  {'Accuracy':>8}  {'Status':>6}")
    lines.append("  " + "-" * 55)

    all_labels_arr = np.array(all_labels)
    all_preds_arr  = np.array(all_preds)
    for i, cls in enumerate(classes):
        mask    = all_labels_arr == i
        total   = int(mask.sum())
        correct = int((all_preds_arr[mask] == i).sum())
        acc     = correct / total if total > 0 else 0.0
        status  = "OK" if acc >= 0.70 else "LOW"
        lines.append(f"  {cls:15s}  {correct:>7}  {total:>7}  {acc:>8.2%}  {status:>6}")

    lines.append("")
    lines.append("  Confusion Matrix  (rows = actual class, cols = predicted class)")
    lines.append("")

    # Header row
    short = [c[:6] for c in classes]
    lines.append("  " + " " * 15 + "".join(f"{s:>7}" for s in short))
    lines.append("  " + " " * 15 + "-" * (7 * len(classes)))
    for i, cls in enumerate(classes):
        row = f"  {cls:15s}" + "".join(f"{conf_matrix[i][j]:>7}" for j in range(len(classes)))
        lines.append(row)

    lines.append("")
    lines.append("  Note: bbox is set to full image in Phase 1.")
    lines.append("        Real bounding boxes will be added in Phase 3 (YOLO).")
    lines.append("=" * 60)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    RESULTS_DIR.mkdir(exist_ok=True)

    if not MODEL_PATH.exists():
        print(f"ERROR: Model not found at {MODEL_PATH.resolve()}")
        print("  Run src/train.py first.")
        sys.exit(1)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    print(f"Loading model from {MODEL_PATH} ...")

    checkpoint = torch.load(MODEL_PATH, map_location=device)
    classes    = checkpoint["classes"]
    image_size = checkpoint.get("image_size", 64)

    model = WaferCNN(num_classes=len(classes)).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    print(f"Checkpoint: epoch {checkpoint['epoch']}, val acc {checkpoint['val_acc']:.2%}")
    print(f"Classes   : {classes}")

    transform = transforms.Compose([
        transforms.Grayscale(num_output_channels=1),
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5]),
    ])

    test_ds     = datasets.ImageFolder(PROCESSED_DIR / "test", transform=transform)
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    print(f"Test samples: {len(test_ds):,}")

    all_labels, all_preds = [], []
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            preds  = model(images).argmax(1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.numpy())

    report = format_report(classes, all_labels, all_preds, MODEL_PATH, checkpoint)

    print("\n" + report)

    report_path = RESULTS_DIR / "eval_report.txt"
    report_path.write_text(report, encoding="utf-8")
    print(f"\nReport saved to: {report_path.resolve()}")


if __name__ == "__main__":
    main()
