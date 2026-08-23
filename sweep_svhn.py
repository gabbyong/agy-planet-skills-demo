import os
import json
import modal

app = modal.App("svhn-resnet-sweep")

dataset_vol = modal.Volume.from_name("svhn-dataset-cache", create_if_missing=True)

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

SWEEP_CONFIGS = [
    {"name": "baseline-sgd", "optimizer": "sgd", "lr": 0.05, "use_cutout": False},
    {"name": "aggressive-sgd", "optimizer": "sgd", "lr": 0.10, "use_cutout": False},
    {"name": "adamw-fast", "optimizer": "adamw", "lr": 0.001, "use_cutout": False},
    {"name": "cutout-sgd", "optimizer": "sgd", "lr": 0.05, "use_cutout": True},
]

@app.function(
    image=image,
    gpu="A100",
    timeout=1800,
    volumes={"/cache": dataset_vol},
    secrets=[
        modal.Secret.from_name("wandb"),
        modal.Secret.from_name("hf-secret"),
    ],
)
def train_single_run(
    config: dict,
    epochs: int = 5,
    batch_size: int = 128,
    wandb_project: str = "svhn-resnet18-sweep",
    hf_repo_id: str = "ivanleomk/resnet18-svhn",
):
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, Dataset
    import torchvision.transforms as transforms
    import torchvision.models as models
    from datasets import load_dataset
    import wandb
    from huggingface_hub import HfApi

    run_name = config["name"]
    opt_type = config["optimizer"]
    lr = config["lr"]
    use_cutout = config["use_cutout"]

    run = wandb.init(
        project=wandb_project,
        name=run_name,
        config={
            "epochs": epochs,
            "batch_size": batch_size,
            "optimizer": opt_type,
            "learning_rate": lr,
            "use_cutout": use_cutout,
            "architecture": "ResNet-18",
            "dataset": "SVHN",
            "gpu": "NVIDIA A100",
        },
        reinit=True,
    )
    print(f"[{run_name}] Live W&B Run URL: {run.get_url()}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def get_resnet18(num_classes: int = 10) -> nn.Module:
        m = models.resnet18(weights=None)
        m.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
        m.maxpool = nn.Identity()
        m.fc = nn.Linear(m.fc.in_features, num_classes)
        return m

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

    # Transforms
    train_transform_list = [
        transforms.RandomCrop(32, padding=4),
        transforms.ToTensor(),
        transforms.Normalize((0.4377, 0.4438, 0.4728), (0.1980, 0.2010, 0.1970)),
    ]
    if use_cutout:
        train_transform_list.append(transforms.RandomErasing(p=0.5, scale=(0.02, 0.2), value="random"))

    train_transform = transforms.Compose(train_transform_list)
    test_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4377, 0.4438, 0.4728), (0.1980, 0.2010, 0.1970)),
    ])

    # Dataset loading with Modal Volume caching
    cache_dir = "/cache/huggingface_svhn"
    os.makedirs(cache_dir, exist_ok=True)
    raw_dataset = load_dataset("ufldl-stanford/svhn", "cropped_digits", cache_dir=cache_dir)
    dataset_vol.commit()

    train_loader = DataLoader(SVHNWrapper(raw_dataset["train"], transform=train_transform), batch_size=batch_size, shuffle=True, num_workers=4)
    test_loader = DataLoader(SVHNWrapper(raw_dataset["test"], transform=test_transform), batch_size=batch_size, shuffle=False, num_workers=4)

    model = get_resnet18(10).to(device)
    criterion = nn.CrossEntropyLoss()

    if opt_type == "adamw":
        optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-2)
    else:
        optimizer = optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=5e-4)

    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    best_acc = 0.0
    checkpoint_dir = f"/tmp/checkpoints_{run_name}"
    os.makedirs(checkpoint_dir, exist_ok=True)
    best_ckpt_path = os.path.join(checkpoint_dir, "best_model.pt")

    for epoch in range(1, epochs + 1):
        # Train
        model.train()
        t_loss, t_correct, t_total = 0.0, 0, 0
        for imgs, lbls in train_loader:
            imgs, lbls = imgs.to(device), lbls.to(device)
            optimizer.zero_grad()
            out = model(imgs)
            loss = criterion(out, lbls)
            loss.backward()
            optimizer.step()

            t_loss += loss.item() * imgs.size(0)
            _, preds = out.max(1)
            t_correct += preds.eq(lbls).sum().item()
            t_total += lbls.size(0)

        train_acc = t_correct / t_total if t_total > 0 else 0
        train_loss = t_loss / t_total if t_total > 0 else 0

        # Eval
        model.eval()
        v_loss, v_correct, v_total = 0.0, 0, 0
        with torch.no_grad():
            for imgs, lbls in test_loader:
                imgs, lbls = imgs.to(device), lbls.to(device)
                out = model(imgs)
                loss = criterion(out, lbls)
                v_loss += loss.item() * imgs.size(0)
                _, preds = out.max(1)
                v_correct += preds.eq(lbls).sum().item()
                v_total += lbls.size(0)

        val_acc = v_correct / v_total if v_total > 0 else 0
        val_loss = v_loss / v_total if v_total > 0 else 0
        scheduler.step()

        cur_lr = optimizer.param_groups[0]["lr"]
        wandb.log({
            "epoch": epoch,
            "train_loss": train_loss,
            "train_acc": train_acc,
            "val_loss": val_loss,
            "val_acc": val_acc,
            "lr": cur_lr,
        })
        print(f"[{run_name}] Epoch {epoch}/{epochs} | Train Loss: {train_loss:.4f} Acc: {train_acc*100:.2f}% | Val Loss: {val_loss:.4f} Acc: {val_acc*100:.2f}%")

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), best_ckpt_path)

    wandb_url = run.get_url()
    wandb.finish()

    return {
        "name": run_name,
        "best_val_acc": best_acc,
        "best_ckpt_path": best_ckpt_path,
        "wandb_url": wandb_url,
        "config": config,
    }

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("hf-secret")],
    timeout=600,
)
def upload_winner_to_hf(winner_dict: dict, all_results: list, hf_repo_id: str = "ivanleomk/resnet18-svhn"):
    from huggingface_hub import HfApi
    import json

    artifact_dir = "/tmp/sweep_artifacts"
    os.makedirs(artifact_dir, exist_ok=True)

    summary_file = os.path.join(artifact_dir, "sweep_results.json")
    with open(summary_file, "w") as f:
        json.dump({
            "winning_run": winner_dict["name"],
            "winning_val_acc": winner_dict["best_val_acc"],
            "all_runs": [
                {"name": r["name"], "best_val_acc": r["best_val_acc"], "config": r["config"]}
                for r in all_results
            ]
        }, f, indent=2)

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

# ResNet-18 SVHN - Sweep Winner

Trained via Modal parallel A100 GPU sweep with persistent dataset volume caching.

## Sweep Leaderboard
| Run | Optimizer | LR | Cutout | Best Val Acc |
| :--- | :--- | :--- | :--- | :--- |
"""
    for r in sorted(all_results, key=lambda x: x["best_val_acc"], reverse=True):
        cfg = r["config"]
        readme_content += f"| **{r['name']}** | {cfg['optimizer']} | {cfg['lr']} | {cfg['use_cutout']} | **{r['best_val_acc']*100:.2f}%** |\n"

    with open(os.path.join(artifact_dir, "README.md"), "w") as f:
        f.write(readme_content)

    api = HfApi(token=os.environ["HF_TOKEN"])
    api.create_repo(repo_id=hf_repo_id, exist_ok=True, private=False)
    api.upload_folder(
        folder_path=artifact_dir,
        repo_id=hf_repo_id,
        commit_message=f"Upload sweep results (Winner: {winner_dict['name']} at {winner_dict['best_val_acc']*100:.2f}%)",
    )
    print(f"Uploaded sweep summary and model card to https://huggingface.co/{hf_repo_id}")

@app.local_entrypoint()
def main(
    epochs: int = 5,
    wandb_project: str = "svhn-resnet18-sweep",
    hf_repo_id: str = "ivanleomk/resnet18-svhn",
):
    print("Launching 4 parallel A100 GPU training runs on Modal...")
    results = list(train_single_run.map(
        SWEEP_CONFIGS,
        kwargs={"epochs": epochs, "wandb_project": wandb_project, "hf_repo_id": hf_repo_id},
    ))

    print("\n--- Sweep Completed ---")
    winner = max(results, key=lambda x: x["best_val_acc"])
    for r in results:
        print(f"Run: {r['name']} | Best Val Acc: {r['best_val_acc']*100:.2f}% | W&B: {r['wandb_url']}")

    print(f"\nWinner: {winner['name']} with {winner['best_val_acc']*100:.2f}% validation accuracy!")
    upload_winner_to_hf.remote(winner, results, hf_repo_id=hf_repo_id)
