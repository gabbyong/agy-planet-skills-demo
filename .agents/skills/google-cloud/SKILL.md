---
name: google-cloud
description: Use this when the user asks to deploy, manage, or configure applications, containers, endpoints, or infrastructure on Google Cloud Platform (such as Cloud Run, Cloud Build, Artifact Registry, or GCS).
---

# Google Cloud Platform Deployment

## Credential and Project Validation

Before running deployment commands, verify local GCP authentication and the active project:

```bash
gcloud config list --format="json"
```

Ensure the active project has the necessary service APIs enabled:
- Cloud Run: `run.googleapis.com`
- Cloud Build: `cloudbuild.googleapis.com`
- Artifact Registry: `artifactregistry.googleapis.com`

Enable missing services directly if required:

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

## Cloud Run Serverless Deployments

Deploy containerized services directly using source-based Cloud Run deployments:

- Ensure the application directory contains a valid `Dockerfile` listening on `PORT` (default `8080`).
- Execute source deployment with explicit region and access policies:

```bash
gcloud run deploy <service-name> \
  --source <source-dir> \
  --region <region> \
  --allow-unauthenticated \
  --memory <memory> \
  --cpu <cpu>
```

## Build Progress and Deployment Communication

- Extract and share the live Google Cloud Build log URL immediately so the user can track image compilation and registry push progress.
- Inform the user that the Cloud Run service entry is created only after the container image finishes pushing.
- Once the deployment finishes, verify the endpoint live via `curl` against `/health` or test API endpoints.
- Provide the user with the direct live endpoint HTTPS URL upon successful health check verification.
