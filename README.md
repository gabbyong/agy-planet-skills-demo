# Antigravity Skills Demo

An end-to-end showcase of autonomous machine learning pipelines, remote GPU compute orchestration, telemetry tracking, cloud deployment, and mathematical visual explainers built with Antigravity Skills.

## Overview of Demonstrated Capabilities

- **Automated Remote GPU Training (`train-model`)**: Orchestrated single-run training and a 4-run parallel hyperparameter sweep across NVIDIA A100 GPUs on Modal with persistent volume caching (`modal.Volume`).
- **Telemetry & Experiment Tracking**: Streamed live loss, accuracy, and learning rate dynamics to Weights & Biases across all concurrent workers.
- **Model Registry Publishing**: Automatically versioned and pushed winning ResNet-18 checkpoints, benchmark cards, and metadata to Hugging Face Hub (`ivanleomk/resnet18-svhn`).
- **Serverless Edge Deployment (`google-cloud`)**: Packaged a FastAPI CPU inference service and deployed it live to Google Cloud Run with an interactive frontend testing authentic SVHN street digits.
- **Mathematical 3D Video Explainers (`explain`)**: Programmed 3Blue1Brown-style Manim 3D surface animations demonstrating Adam vs. SGD loss ravine dynamics with studio voiceover narration.

## Example: Parallel A100 Sweep & Optimization Dynamics

Using Modal's distributed execution engine, 4 distinct training configurations were evaluated in parallel on the SVHN benchmark in under 90 seconds:

| Model Run | Optimizer | Learning Rate | Regularization | Test Accuracy | Test Loss |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`adamw-fast` (Winner)** | AdamW | `0.001` | Decoupled Weight Decay ($10^{-2}$) | **96.13%** | `0.1460` |
| **`cutout-sgd`** | SGD + Momentum | `0.05` | Random Erasing ($p=0.5$) | **95.80%** | `0.1533` |
| **`baseline-sgd`** | SGD + Momentum | `0.05` | Weight Decay ($5 \times 10^{-4}$) | **95.68%** | `0.1557` |
| **`aggressive-sgd`** | SGD + Momentum | `0.10` | Cosine Annealing Decay | **95.68%** | `0.1588` |

### Live Links & Artifacts

- **Weights & Biases Sweep Dashboard**: [wandb.ai/ivanleo97-freelance/svhn-resnet18-sweep](https://wandb.ai/ivanleo97-freelance/svhn-resnet18-sweep)
- **Hugging Face Model Repository**: [huggingface.co/ivanleomk/resnet18-svhn](https://huggingface.co/ivanleomk/resnet18-svhn)
- **3D Manim Animation Source**: [`.agents/skills/explain/examples/adam-3d-optimization/adam_3d_animation.py`](.agents/skills/explain/examples/adam-3d-optimization/adam_3d_animation.py)

## Repository Structure

- `.agents/skills/train-model/`: Skill for key validation, volume caching, and remote GPU compute on Modal.
- `.agents/skills/google-cloud/`: Skill for source-based Cloud Run container deployments and health validation.
- `.agents/skills/explain/`: Skill for interactive HTML explainers, Manim mathematical animations, and TTS narration.
- `app/`: FastAPI application, Dockerfile, and frontend testing interface for Cloud Run.
- `train_svhn_resnet.py`: Single-run Modal training script.
- `sweep_svhn.py`: Parallel A100 hyperparameter sweep script with Modal Volume caching.
