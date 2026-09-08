---
name: google-cloud
description: Use this when the user asks to deploy, manage, or configure applications, containers, endpoints, or ML services on Google Cloud Platform (Cloud Run, Vertex AI, GCS, Cloud Build).
---

# Google Cloud Platform & Serverless ML Deployment

Deploy ML inference services and web applications to Google Cloud Run with zero-friction source builds and embedded interactive testing interfaces.

---

## 1. Project & Service Gate

Before running deployment commands, verify GCP authentication and project settings:

```bash
# Ensure Python 3.10+ is used by gcloud (avoids system Python 3.9 issues on macOS)
export CLOUDSDK_PYTHON="$(pwd)/.venv/bin/python"

gcloud config list --format="json"
```

Ensure required APIs are enabled on the target project:
```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

---

## 2. Serverless ML Inference Service Pattern

When packaging an ML model (e.g. PyTorch checkpoint from Vertex AI or local MPS) for Cloud Run:

1. **Lightweight FastAPI Service**:
   - `/health`: Fast probe returning `{"status": "healthy", "checkpoint_loaded": bool}`.
   - `/predict`: Accepts base64 image or tensor payload, runs inference with PyTorch (`torch.no_grad()`), and returns class probabilities.
   - `/`: Serves a self-contained, responsive HTML/JS web UI allowing visitors to draw on a canvas or test samples with real-time confidence bars.
   - **Resilient Path Resolution**: Check multiple candidate paths for checkpoints (e.g., `/app/models/...` and `models/...`) so the service works identically in local development and within the container.

2. **Source Build Optimization (`.gcloudignore`)**:
   Always create a `.gcloudignore` file to exclude local virtual environments and caches from the build upload:
   ```text
   .git
   .venv
   __pycache__
   *.pyc
   scratch
   .agents
   ```

3. **Minimal Dockerfile**:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
   COPY src/ /app/src/
   COPY models/ /app/models/
   COPY service/app.py /app/app.py
   ENV PORT=8080
   CMD ["sh", "-c", "exec uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
   ```

---

## 3. One-Command Source Deployment

Deploy directly from source without manual Docker registry tagging:

```bash
gcloud run deploy svhn-classifier \
  --project gen-lang-client-0287142723 \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1
```

- **Target Project**: `gen-lang-client-0287142723` (Mimir)
- **Region**: `us-central1`
- **Live Endpoint**: `https://svhn-classifier-519332626090.us-central1.run.app`

---

## 4. Verification & Presentation

1. Extract and output the live Google Cloud Build log URL so the build can be monitored.
2. Once the service deploys, run a quick automated smoke test:
   ```bash
   curl -s https://svhn-classifier-519332626090.us-central1.run.app/health
   ```
3. Share the live HTTPS URL with the user, highlighting the embedded interactive web UI for testing predictions live in browser.
