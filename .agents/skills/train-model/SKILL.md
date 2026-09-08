---
name: train-model
description: Use this when the user asks to train, fine-tune, or benchmark models on Google Cloud Vertex AI (including NVIDIA A100 GPUs) with GCS artifact storage.
---

# Model Training on Google Cloud Vertex AI

Orchestrate training jobs on Google Cloud Vertex AI using pre-built PyTorch GPU containers and NVIDIA A100 compute.

---

## 1. Environment & GCP Validation Gate

Before submitting remote jobs, verify GCP authentication and project configuration:

```bash
python3 .agents/skills/train-model/scripts/verify_gcp_credentials.py
```

Check:
1. **Active Project**: `gcloud config get-value project`
2. **Vertex AI API**: `aiplatform.googleapis.com` enabled
3. **Artifact Staging Bucket**: GCS bucket (e.g., `gs://<project>-vertex-artifacts/`)

---

## 2. Compute Right-Sizing & Hardware Tiers

Do not default to heavy, expensive accelerators when not required. Match hardware to the model workload and project quotas:

| Tier | Machine Type | Accelerator | When to Use | Cost / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Local Inner Loop** | Apple Silicon / CPU | `mps` / `cpu` | Fast validation (<20s), rapid prototyping, micro-runs | Free, instant iteration |
| **Cloud CPU** | `n1-standard-4` | None | Baseline cloud jobs, no quota prerequisites | Pennies, zero quota barriers |
| **Economical GPU (Recommended)** | `n1-standard-4` | `NVIDIA_TESLA_T4` (1x) | Vision models (SVHN, CIFAR), small CNNs, lightweight fine-tuning | ~$0.35/hr, 10x cheaper than A100 |
| **Modern GPU** | `g2-standard-4` | `NVIDIA_L4` (1x) | Modern PyTorch workloads, diffusion, mid-size models | ~$0.70/hr, 24GB VRAM |
| **Heavy Accelerator** | `a2-highgpu-1g` | `NVIDIA_TESLA_A100` (1x) | Large language models, massive batch training, distributed DDP | ~$3.67/hr, requires quota approval |

### Pre-Built Container Image URIs
Vertex AI requires specific image tags (including python version suffix):
- **GPU Training**: `us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.2-1.py310:latest`
- **CPU Training**: `us-docker.pkg.dev/vertex-ai/training/pytorch-xla.2-1.py310:latest`

---

## 3. Fast Local Micro-Run (Pre-flight Validation)

Before dispatching cloud compute, run a fast 1-epoch / 10-batch micro-run locally using `.venv`:

```bash
uv run python train.py --dry-run
```

Ensure loss decreases, tensor shapes match, and the model checkpoint serializes cleanly (`models/model.pt`).

---

## 4. Submitting Vertex AI Custom Job

### Python SDK (`google-cloud-aiplatform`)

Always use `job.submit()` rather than `job.run(sync=False)` to avoid background thread race conditions, and pass `HF_TOKEN` from `.env` to allow access to gated/authenticated datasets:

### Standard Target Environment
- **GCP Project**: `gen-lang-client-0287142723` (Mimir)
- **Region**: `us-central1`
- **Staging & Artifact Bucket**: `gs://mimir-svhn-artifacts-519332626090`
- **Container Images**:
  - GPU (T4/L4/A100): `us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.2-1.py310:latest`
  - CPU: `us-docker.pkg.dev/vertex-ai/training/pytorch-xla.2-1.py310:latest`

```python
import os
import dotenv
from google.cloud import aiplatform

dotenv.load_dotenv(".env")

PROJECT_ID = "gen-lang-client-0287142723"
REGION = "us-central1"
BUCKET = "gs://mimir-svhn-artifacts-519332626090"

aiplatform.init(
    project=PROJECT_ID,
    location=REGION,
    staging_bucket=f"{BUCKET}/staging",
)

job = aiplatform.CustomJob.from_local_script(
    display_name="svhn-cnn-training",
    script_path="train.py",
    container_uri="us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.2-1.py310:latest",
    requirements=["datasets>=2.14.0", "torchvision>=0.15.0", "pillow", "python-dotenv"],
    machine_type="n1-standard-4",
    accelerator_type="NVIDIA_TESLA_T4",
    accelerator_count=1,
    base_output_dir=f"{BUCKET}/models/svhn-cnn",
    args=["--epochs", "5", "--batch-size", "64"],
    environment_variables={"HF_TOKEN": os.getenv("HF_TOKEN", "")},
)

# Submit synchronously to Vertex AI API without blocking local terminal
job.submit()
print(f"Custom Job launched: {job.resource_name}")
```

### CLI Alternative (`gcloud`)

```bash
gcloud ai custom-jobs create \
  --project=gen-lang-client-0287142723 \
  --region=us-central1 \
  --display-name="svhn-cnn-training" \
  --worker-pool-spec=machine-type=n1-standard-4,accelerator-type=NVIDIA_TESLA_T4,accelerator-count=1,container-image-uri=us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.2-1.py310:latest \
  --args="--epochs=5,--batch-size=64"
```

---

## 5. Artifact Publishing & Handoff to Cloud Run

- The training script saves the model weights to `$AIP_MODEL_DIR` (which Vertex AI syncs to GCS) or mirrors to `models/model.pt`.
- Hand off the exported checkpoint to the Cloud Run service (`google-cloud` skill) for serverless inference deployment.
