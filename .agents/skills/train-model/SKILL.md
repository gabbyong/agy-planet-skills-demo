---
name: train-model
description: Use this when the user asks to train, fine-tune, or benchmark models on remote compute (Modal) with Weights & Biases tracking and Hugging Face Hub uploads.
---

# Model Training on Remote Compute

## Key Validation and Environment Gate

Before creating or launching any training code, validate the environment and remote secrets by running the credential checker:

```bash
python3 .agents/skills/train-model/scripts/verify_credentials.py
```

Verify all three platforms:
- **Modal**: Profile authenticated (`modal profile current`).
- **Hugging Face (`HF_TOKEN`)**: Authenticated with write access (`https://huggingface.co/api/whoami-v2`).
- **Weights & Biases (`WANDB_API_KEY`)**: Authenticated (`https://api.wandb.ai/graphql`).

If any credential is missing or invalid:
- Immediately prompt the user for the specific missing key.
- Do not proceed with mock tokens or placeholder runs.
- Once provided, persist the key to `~/.config/shell.env` and update Modal secrets (`modal secret create <name> <KEY=VAL> --force`).

## Experiment Planning and Parameter Proposal

Before launching jobs, discuss and align on the training setup:
- Propose architecture choices and hyperparameters (learning rate, batch size, scheduler, epochs).
- Clarify trade-offs (e.g. convergence speed vs memory, learning rate warmup, regularization).
- Provide an estimated execution duration and resource profile (defaulting to `gpu="A100"`).

## Concrete Job Proposal and Result Shape

Present the user with a structured proposal specifying:
- The exact job(s) to run (single training run vs hyperparameter sweep).
- The exact shape of the output (number of models, checkpoint format `.pt` / `safetensors`, metadata `config.json`, model card `README.md`).
- Target destinations (Weights & Biases project name and Hugging Face repository ID).

## Explicit Confirmation Gate

- Request explicit user approval on the proposed plan before triggering GPU compute.
- Only launch remote execution once the user gives the green light.

## Dataset Ingestion and Caching

- **Prefer Hugging Face Hosted Datasets**: Always prefer loading datasets hosted on Hugging Face Hub (e.g. via `datasets.load_dataset(...)`) rather than downloading from legacy academic/university servers to avoid severe rate-limiting and connection throttling.
- **Bake Datasets into Container Images**: If you need to use a dataset multiple times across runs or parallel containers, bake the dataset directly into the Modal container image build step (or pre-seed the volume) so workers start with zero download latency.
- **Persistent Modal Volumes**: Attach a persistent volume `modal.Volume.from_name("dataset-cache", create_if_missing=True)` mounted at `/cache`. Point `HF_HOME=/cache/huggingface` or `TORCH_HOME=/cache/torch` so datasets, tokenizers, and pretrained weights persist across executions. Commit newly downloaded data via `vol.commit()` so other containers can reuse it immediately.

## Training Script Standards

- Use `modal.App` with an explicit container image installing dependencies via `pip_install`.
- Default to `gpu="A100"` for high compute throughput.
- Attach required secrets (`modal.Secret.from_name("wandb")`, `modal.Secret.from_name("hf-secret")`).
- Use early returns and functional structure.

## Weights & Biases Experiment Tracking

- Initialize `wandb.init()` with project name, run configuration, model hyperparameters, dataset details, and architecture name.
- Print the live W&B run URL immediately (`run.get_url()`) and provide the direct clickable link to the user.
- Log per-epoch and step-level metrics including training loss, training accuracy, validation loss, validation accuracy, and learning rate.
- Close the run cleanly using `wandb.finish()` upon training completion.

## Hugging Face Hub Artifact Publishing

- Use `huggingface_hub.HfApi` authenticated with `HF_TOKEN`.
- Create repository if it does not already exist via `api.create_repo(repo_id=..., exist_ok=True)`.
- Upload the best model checkpoint weights (`.pt` or `model.safetensors`).
- Upload accompanying metadata, configuration summary, and a concise model card `README.md` describing model architecture, dataset, and benchmark results.
- Provide the user with the direct link to the Hugging Face model repository upon upload.
