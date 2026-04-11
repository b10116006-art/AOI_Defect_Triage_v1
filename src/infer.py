"""
infer.py

Runs inference on a single wafer map image using the trained CNN.
Prints a JSON result that matches the locked AOI contract format.

Phase 1 note:
    The 'bbox' field is set to the full image dimensions [0, 0, W, H]
    because Phase 1 is classification-only. Real bounding boxes
    will be produced by YOLO in Phase 3.

Usage:
    python src/infer.py --image data/processed/test/Scratch/test_000123.png

    Optional metadata flags (all have safe defaults):
        --image-id   img_0001
        --machine-id AOI_01
        --lot-id     LOT123
        --layer      ILD
"""

import sys
import json
import argparse
import torch
import torch.nn.functional as F
from torchvision import transforms
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

# Re-use WaferCNN from train.py (same src/ directory)
sys.path.insert(0, str(Path(__file__).parent))
from train import WaferCNN

MODEL_PATH = Path("models/cnn_baseline_v1.pth")
IMAGE_SIZE = 64   # default; overridden by checkpoint if available

transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5]),
])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_model(model_path, device):
    checkpoint = torch.load(model_path, map_location=device)
    classes    = checkpoint["classes"]
    img_size   = checkpoint.get("image_size", IMAGE_SIZE)
    model      = WaferCNN(num_classes=len(classes)).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    return model, classes, img_size


def predict(image_path, model, img_size, device):
    """Load one PNG, run through model, return (defect_class, confidence)."""
    img    = Image.open(image_path).convert("RGB")
    resize = transforms.Resize((img_size, img_size))
    tensor = transform(resize(img)).unsqueeze(0).to(device)

    with torch.no_grad():
        logits     = model(tensor)
        probs      = F.softmax(logits, dim=1)
        confidence, pred_idx = probs.max(dim=1)

    return pred_idx.item(), confidence.item()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_result_dict(image_id, machine_id, lot_id, layer,
                      classes, pred_idx, confidence, img_size) -> dict:
    """Build the locked AOI JSON contract dict from inference outputs."""
    defect_class = classes[pred_idx]
    ng_flag      = defect_class.lower() != "none"
    return {
        "image_id":      image_id,
        "machine_id":    machine_id,
        "lot_id":        lot_id,
        "layer":         layer,
        "timestamp":     datetime.now(timezone.utc).isoformat(),
        "defect_class":  defect_class,
        "confidence":    round(confidence, 4),
        "bbox":          [0, 0, img_size, img_size],   # Phase 1: full image placeholder
        "ng_flag":       ng_flag,
        "model_name":    "cnn_baseline",
        "model_version": MODEL_PATH.stem,
    }


def main():
    parser = argparse.ArgumentParser(
        description="AOI Defect Triage — single image inference (Phase 1)"
    )
    parser.add_argument("--image",      required=True, help="Path to wafer map PNG image")
    parser.add_argument("--image-id",   default="img_0001",    help="Image identifier")
    parser.add_argument("--machine-id", default="AOI_01",      help="AOI machine ID")
    parser.add_argument("--lot-id",     default="LOT_UNKNOWN", help="Lot ID")
    parser.add_argument("--layer",      default="UNKNOWN",     help="Process layer (e.g. ILD)")
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"ERROR: Image not found: {image_path.resolve()}")
        sys.exit(1)

    if not MODEL_PATH.exists():
        print(f"ERROR: Model not found at {MODEL_PATH.resolve()}")
        print("  Run src/train.py first.")
        sys.exit(1)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, classes, img_size = load_model(MODEL_PATH, device)

    pred_idx, confidence = predict(image_path, model, img_size, device)

    # Build locked JSON contract output
    result = build_result_dict(
        args.image_id, args.machine_id, args.lot_id, args.layer,
        classes, pred_idx, confidence, img_size,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
