"""
train.py

Trains a simple CNN on the processed wafer map images.
Handles class imbalance with inverse-frequency loss weights.
Saves the best checkpoint (by validation accuracy) to:
    models/cnn_baseline_v1.pth

Usage:
    python src/train.py
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from pathlib import Path

PROCESSED_DIR = Path("data/processed")
MODELS_DIR    = Path("models")
MODEL_PATH    = MODELS_DIR / "cnn_baseline_v1.pth"

IMAGE_SIZE    = 64
BATCH_SIZE    = 64
EPOCHS        = 20
LEARNING_RATE = 1e-3
NUM_CLASSES   = 9


# ---------------------------------------------------------------------------
# Model definition
# ---------------------------------------------------------------------------

class WaferCNN(nn.Module):
    """
    Simple 3-block CNN for wafer map defect classification.

    Input : 1 x 64 x 64 grayscale image
    Output: logits for 9 defect classes

    Spatial flow: 64 → 32 → 16 → 8  (one MaxPool per block)
    Classifier  : Flatten → FC(256) → Dropout(0.5) → FC(9)
    """
    def __init__(self, num_classes=NUM_CLASSES):
        super().__init__()
        self.features = nn.Sequential(
            # Block 1
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),          # 64 → 32

            # Block 2
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),          # 32 → 16

            # Block 3
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2),          # 16 → 8
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 8 * 8, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes),
        )

    def forward(self, x):
        return self.classifier(self.features(x))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def compute_class_weights(dataset):
    """
    Inverse-frequency weights so rare defect classes are not drowned
    out by the dominant 'none' (clean wafer) class.
    """
    counts = np.zeros(NUM_CLASSES, dtype=np.float64)
    for _, label_idx in dataset.samples:
        counts[label_idx] += 1
    weights = 1.0 / np.where(counts > 0, counts, 1.0)
    # Normalize so weights sum to NUM_CLASSES (keeps loss scale stable)
    weights = weights / weights.sum() * NUM_CLASSES
    return torch.tensor(weights, dtype=torch.float)


def run_epoch(model, loader, criterion, optimizer, device, training):
    """One full pass over a DataLoader. Returns (avg_loss, accuracy)."""
    model.train(training)
    total_loss, correct, total = 0.0, 0, 0

    with torch.set_grad_enabled(training):
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)

            if training:
                optimizer.zero_grad()

            outputs = model(images)
            loss    = criterion(outputs, labels)

            if training:
                loss.backward()
                optimizer.step()

            total_loss += loss.item() * images.size(0)
            correct    += (outputs.argmax(1) == labels).sum().item()
            total      += images.size(0)

    return total_loss / total, correct / total


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    MODELS_DIR.mkdir(exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # Grayscale → tensor → normalize to [-1, 1]
    transform = transforms.Compose([
        transforms.Grayscale(num_output_channels=1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5]),
    ])

    train_ds = datasets.ImageFolder(PROCESSED_DIR / "train", transform=transform)
    val_ds   = datasets.ImageFolder(PROCESSED_DIR / "val",   transform=transform)

    print(f"Train samples : {len(train_ds):,}")
    print(f"Val samples   : {len(val_ds):,}")
    print(f"Classes       : {train_ds.classes}")

    class_weights = compute_class_weights(train_ds).to(device)
    print("\nClass weights (higher = rarer class):")
    for cls, w in zip(train_ds.classes, class_weights.cpu().numpy()):
        print(f"  {cls:15s}: {w:.3f}")

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,  num_workers=0)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    model     = WaferCNN().to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    # Halve the learning rate every 7 epochs
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.5)

    best_val_acc = 0.0
    print(f"\nTraining for {EPOCHS} epochs ...\n")
    print(f"{'Epoch':>6}  {'Train Loss':>10}  {'Train Acc':>9}  {'Val Loss':>8}  {'Val Acc':>7}  {'':>2}")
    print("-" * 60)

    for epoch in range(1, EPOCHS + 1):
        train_loss, train_acc = run_epoch(model, train_loader, criterion, optimizer, device, training=True)
        val_loss,   val_acc   = run_epoch(model, val_loader,   criterion, optimizer, device, training=False)
        scheduler.step()

        saved = val_acc > best_val_acc
        marker = " <-- saved" if saved else ""
        print(f"{epoch:>6}  {train_loss:>10.4f}  {train_acc:>8.2%}  {val_loss:>8.4f}  {val_acc:>6.2%}{marker}")

        if saved:
            best_val_acc = val_acc
            torch.save(
                {
                    "epoch":            epoch,
                    "model_state_dict": model.state_dict(),
                    "val_acc":          val_acc,
                    "classes":          train_ds.classes,
                    "image_size":       IMAGE_SIZE,
                },
                MODEL_PATH,
            )

    print(f"\nBest val accuracy : {best_val_acc:.2%}")
    print(f"Model saved to    : {MODEL_PATH.resolve()}")


if __name__ == "__main__":
    main()
