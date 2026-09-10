# Antigravity Skills Demo

An end-to-end showcase of autonomous AI agent workflows orchestrating dataset exploration, interactive visual explainers, local model training, and serverless deployment to Google Cloud Run built with Antigravity Skills.

## The Core Pipeline

### 1. Dataset Exploration (`visualize-dataset`)
Rapidly slice and inspect benchmarks without heavy upfront downloads. Using streaming and fast slicing, agents inspect subsets from the [`ufldl-stanford/svhn`](https://huggingface.co/datasets/ufldl-stanford/svhn) (Street View House Numbers) dataset on Hugging Face and provide immediate visual feedback using native in-chat `carousel` components.

### 2. Multi-Modal Visual Explainers (`explain`)
Deliver deep, engaging explanations by generating self-contained interactive HTML artifacts. These visualizers feature dynamic parameter sliders, state machines, architectural walkthroughs, and self-checking interactive quizzes (see the showcases in [`examples/explain/`](examples/explain/), including systems architectures like Agent Harness, deep learning dynamics in LLM Training & ResNet-18, and continental satellite pipelines in **Agricultural Landscape Understanding (ALU)**).

### 3. Local Model Training (`train-model`)
Validate and train models locally using rapid micro-runs on Apple Silicon (`mps`) or CPU before serializing clean PyTorch checkpoints for production.

### 4. Serverless Edge Deployment (`google-cloud`)
Package trained PyTorch models into a lightweight FastAPI service with an embedded interactive HTML test canvas, then deploy directly to Google Cloud Run via `gcloud run deploy`.

---

## Live Links & References

- **Google Cloud Run Live Demo**: [https://svhn-classifier-519332626090.us-central1.run.app/](https://svhn-classifier-519332626090.us-central1.run.app/) *(Prior live deployment testing SVHN street digit classification)*
- **SVHN Dataset on Hugging Face**: [`ufldl-stanford/svhn`](https://huggingface.co/datasets/ufldl-stanford/svhn)
- **Interactive Explainer Showcases**: [`examples/README.md`](examples/README.md)

---

## Repository Structure

- `.agents/skills/visualize-dataset/`: Skill for progressive dataset exploration, streaming slices, and visual carousels.
- `.agents/skills/explain/`: Skill for interactive HTML explainers, architecture walkthroughs, and visual artifacts.
- `.agents/skills/train-model/`: Skill for local micro-runs and PyTorch model training.
- `.agents/skills/google-cloud/`: Skill for containerizing PyTorch models and deploying FastAPI inference services to Google Cloud Run.
- `examples/`: Standalone interactive HTML explainers and visual demo showcases.
