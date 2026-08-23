import os
import io
import time
import base64
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from PIL import Image
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.models as models
from huggingface_hub import hf_hub_download

app = FastAPI(title="SVHN ResNet-18 Classifier")

# Model Definition matching training script
def get_resnet18(num_classes: int = 10) -> nn.Module:
    model = models.resnet18(weights=None)
    model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
    model.maxpool = nn.Identity()
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model

# Global model state
MODEL_REPO = os.getenv("HF_REPO_ID", "ivanleomk/resnet18-svhn")
device = torch.device("cpu")
model: Optional[nn.Module] = None

transform = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize((0.4377, 0.4438, 0.4728), (0.1980, 0.2010, 0.1970)),
])

def load_model():
    global model
    if model is not None:
        return model

    print(f"Downloading checkpoint from Hugging Face Hub: {MODEL_REPO}")
    ckpt_path = hf_hub_download(repo_id=MODEL_REPO, filename="best_model.pt")
    m = get_resnet18(num_classes=10)
    state_dict = torch.load(ckpt_path, map_location=device, weights_only=True)
    m.load_state_dict(state_dict)
    m.eval()
    model = m
    print("Model loaded successfully into memory.")
    return model

@app.on_event("startup")
def startup_event():
    try:
        load_model()
    except Exception as e:
        print(f"Warning: Model pre-load deferred: {e}")

class PredictRequest(BaseModel):
    image_base64: Optional[str] = None
    sample_id: Optional[int] = None

def run_inference(image: Image.Image):
    m = load_model()
    start_time = time.perf_counter()

    rgb_image = image.convert("RGB")
    tensor = transform(rgb_image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = m(tensor)
        probs = torch.softmax(outputs, dim=1).squeeze(0).tolist()

    duration_ms = (time.perf_counter() - start_time) * 1000.0
    predicted_digit = int(torch.argmax(outputs, dim=1).item())
    confidence = probs[predicted_digit]

    return {
        "predicted_digit": predicted_digit,
        "confidence": confidence,
        "probabilities": {str(i): round(p, 4) for i, p in enumerate(probs)},
        "latency_ms": round(duration_ms, 2),
    }

@app.post("/api/predict")
async def predict(req: PredictRequest):
    if req.sample_id is not None:
        sample_path = f"static/samples/sample_{req.sample_id}.png"
        if not os.path.exists(sample_path):
            raise HTTPException(status_code=404, detail="Sample not found")
        img = Image.open(sample_path)
        return run_inference(img)

    if req.image_base64:
        header_split = req.image_base64.split(",")
        raw_b64 = header_split[1] if len(header_split) > 1 else header_split[0]
        img_bytes = base64.b64decode(raw_b64)
        img = Image.open(io.BytesIO(img_bytes))
        return run_inference(img)

    raise HTTPException(status_code=400, detail="Must provide either sample_id or image_base64")

@app.post("/api/predict-file")
async def predict_file(file: UploadFile = File(...)):
    contents = await file.read()
    img = Image.open(io.BytesIO(contents))
    return run_inference(img)

@app.get("/api/samples")
def get_samples():
    samples = []
    samples_dir = "static/samples"
    if os.path.exists(samples_dir):
        for fname in sorted(os.listdir(samples_dir)):
            if fname.endswith(".png"):
                digit = fname.replace("sample_", "").replace(".png", "")
                samples.append({
                    "digit": int(digit) if digit.isdigit() else 0,
                    "url": f"/static/samples/{fname}",
                })
    return {"samples": samples}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_repo": MODEL_REPO,
        "model_loaded": model is not None,
    }

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def index():
    return FileResponse("static/index.html")
