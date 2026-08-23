import os
import json
import modal

app = modal.App("svhn-resnet-training")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch",
        "torchvision",
        "datasets",
        "wandb",
        "huggingface_hub",
        "tqdm",
    )
)

@app.function(
    image=image,
    gpu="T4",
    timeout=3600,
    secrets=[
        modal.Secret.from_name("wandb"),
        modal.Secret.from_name("hf-secret"),
    ],
)
def train(
    epochs: int = 5,
    batch_size: int = 128,
    lr: float = 0.05,
    hf_repo_id: str = "ivanleomk/resnet18-svhn",
    wandb_project: str = "svhn-resnet18",
):
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, Dataset
    import torchvision
    import torchvision.transforms as transforms
    from datasets import load_dataset
    import wandb
    from huggingface_hub import HfApi

    def get_resnet18(num_classes: int = 10) -> nn.Module:
        model = torchvision.models.resnet18(weights=None)
        model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
        model.maxpool = nn.Identity()
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        return model

    class SVHNWrapper(Dataset):
        def __init__(self, hf_dataset, transform=None):
            self.ds = hf_dataset
            self.transform = transform

        def __len__(self):
            return len(self.ds)

        def __getitem__(self, idx):
            item = self.ds[idx]
            img = item["image"].convert("RGB")
            label = int(item["label"])
            if self.transform:
                img = self.transform(img)
            return img, label

    def train_epoch(model, loader, criterion, optimizer, device):
        model.train()
        total_loss, correct, total = 0.0, 0, 0
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * images.size(0)
            _, preds = outputs.max(1)
            correct += preds.eq(labels).sum().item()
            total += labels.size(0)

        if total == 0:
            return 0.0, 0.0
        return total_loss / total, correct / total

    def eval_epoch(model, loader, criterion, device):
        model.eval()
        total_loss, correct, total = 0.0, 0, 0
        with torch.no_grad():
            for images, labels in loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)

                total_loss += loss.item() * images.size(0)
                _, preds = outputs.max(1)
                correct += preds.eq(labels).sum().item()
                total += labels.size(0)

        if total == 0:
            return 0.0, 0.0
        return total_loss / total, correct / total

    run = wandb.init(
        project=wandb_project,
        config={
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": lr,
            "architecture": "ResNet-18",
            "dataset": "SVHN",
            "optimizer": "SGD(momentum=0.9, weight_decay=5e-4)",
            "scheduler": "CosineAnnealingLR",
        },
    )

    print(f"W&B Run URL: {run.get_url()}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")

    train_transform = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.ToTensor(),
        transforms.Normalize((0.4377, 0.4438, 0.4728), (0.1980, 0.2010, 0.1970)),
    ])
    test_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4377, 0.4438, 0.4728), (0.1980, 0.2010, 0.1970)),
    ])

    print("Loading SVHN dataset from Hugging Face Hub fast cache...")
    raw_dataset = load_dataset("ufldl-stanford/svhn", "cropped_digits")
    train_set = SVHNWrapper(raw_dataset["train"], transform=train_transform)
    test_set = SVHNWrapper(raw_dataset["test"], transform=test_transform)

    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True, num_workers=2)
    test_loader = DataLoader(test_set, batch_size=batch_size, shuffle=False, num_workers=2)

    model = get_resnet18(num_classes=10).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=5e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    artifact_dir = "/tmp/artifacts"
    os.makedirs(artifact_dir, exist_ok=True)
    best_ckpt_path = os.path.join(artifact_dir, "best_model.pt")

    best_acc = 0.0
    for epoch in range(1, epochs + 1):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = eval_epoch(model, test_loader, criterion, device)
        scheduler.step()

        current_lr = optimizer.param_groups[0]["lr"]
        wandb.log({
            "epoch": epoch,
            "train_loss": train_loss,
            "train_acc": train_acc,
            "val_loss": val_loss,
            "val_acc": val_acc,
            "learning_rate": current_lr,
        })

        print(f"Epoch {epoch:02d}/{epochs:02d} | Train Loss: {train_loss:.4f} Acc: {train_acc*100:.2f}% | Val Loss: {val_loss:.4f} Acc: {val_acc*100:.2f}%")

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), best_ckpt_path)

    wandb.finish()

    if not os.path.exists(best_ckpt_path):
        return {"status": "error", "message": "Checkpoint not created"}

    config_data = {
        "model_architecture": "ResNet-18",
        "dataset": "SVHN",
        "num_classes": 10,
        "best_val_acc": best_acc,
        "epochs": epochs,
        "batch_size": batch_size,
    }
    with open(os.path.join(artifact_dir, "config.json"), "w") as f:
        json.dump(config_data, f, indent=2)

    readme_content = f"""---
tags:
- image-classification
- pytorch
- resnet
- svhn
datasets:
- svhn
metrics:
- accuracy
---

# ResNet-18 on SVHN

Trained on Modal GPU, tracked on Weights & Biases, published to Hugging Face Hub.

## Benchmark Results
- Best Validation Accuracy: {best_acc * 100:.2f}%
- Epochs: {epochs}
- Optimizer: SGD (CosineAnnealingLR)
"""
    with open(os.path.join(artifact_dir, "README.md"), "w") as f:
        f.write(readme_content)

    print(f"Uploading artifacts to Hugging Face Hub ({hf_repo_id})...")
    api = HfApi(token=os.environ["HF_TOKEN"])
    api.create_repo(repo_id=hf_repo_id, exist_ok=True, private=False)
    api.upload_folder(
        folder_path=artifact_dir,
        repo_id=hf_repo_id,
        commit_message=f"Upload ResNet-18 SVHN model with val accuracy {best_acc*100:.2f}%",
    )

    print(f"Uploaded successfully to https://huggingface.co/{hf_repo_id}")
    return {
        "status": "success",
        "best_val_accuracy": best_acc,
        "hf_url": f"https://huggingface.co/{hf_repo_id}",
    }

@app.local_entrypoint()
def main(
    epochs: int = 5,
    batch_size: int = 128,
    lr: float = 0.05,
    hf_repo_id: str = "ivanleomk/resnet18-svhn",
):
    train.remote(
        epochs=epochs,
        batch_size=batch_size,
        lr=lr,
        hf_repo_id=hf_repo_id,
    )
