---
name: visualize-dataset
description: Use this when the user asks to explore, inspect, visualize, or understand a dataset (e.g., SVHN, CIFAR, MNIST, ImageNet, audio, or text).
---

# Dataset Exploration & Visualization

Rapidly inspect and communicate the essence of any dataset using lightweight slicing and high-impact in-chat visual carousels.

---

## 1. Environment & Fast Slicing Standard

- **Always use namespaced repository IDs (`<namespace>/<dataset_name>`)**: Modern Hugging Face Hub does not resolve bare dataset names without a namespace (e.g. use `ufldl-stanford/svhn`, `ylecun/mnist`, `uoft-cs/cifar10` instead of bare `svhn`, `mnist`, or `cifar10`). Calling bare dataset names causes `Invalid HF URI: Repository id must be 'namespace/name'` errors. If unsure of the exact repo ID, query `HfApi().list_datasets(search="...")` first. Do not pass deprecated `trust_remote_code=True`.
- **Always load `HF_TOKEN` from `.env`**: Check and load environment variables from `.env` (e.g., using `python-dotenv` or manual parsing) before making Hugging Face Hub calls. Pass the token to `datasets.load_dataset(..., token=os.getenv("HF_TOKEN"))` or set `os.environ["HF_TOKEN"]` to prevent rate-limiting and access authenticated datasets.
- **Always use the project `.venv`**: Execute scripts using the existing project environment (`.venv/bin/python` or `uv run python script.py` without ephemeral `--with` flags) to leverage pre-installed dependencies.
- **Never download the full multi-gigabyte dataset upfront.**
- Stream or slice only a tiny subset (e.g., 20–100 samples) to minimize latency:
  - Hugging Face `datasets`: `load_dataset("<namespace>/<name>", split="train[:50]", token=os.getenv("HF_TOKEN"))` or `streaming=True`.
  - PyTorch `torchvision`: slice indices or load a micro-batch.
- Run inspection scripts instantaneously via the project `.venv`:
  ```bash
  uv run python inspect_slice.py
  ```

---

## 2. In-Chat Visual Carousels

Instead of sending the user to separate artifact files or long walls of text, display the dataset directly in chat using Antigravity's native `carousel` syntax.

### Deliverable Format

1. **Save sample images** with metadata to a local directory:
   - Example: `./scratch/samples/sample_0_label_2.png`
2. **Present an in-chat carousel**:
   ````carousel
   ![Class 2 (Confidence: High)](/absolute/path/to/sample_0_label_2.png)
   <!-- slide -->
   ![Class 5 (Blurry Background Noise)](/absolute/path/to/sample_1_label_5.png)
   <!-- slide -->
   ![Class 9 (Distractor digits on borders)](/absolute/path/to/sample_2_label_9.png)
   <!-- slide -->
   ```
   Dataset Metrics:
   - Shape: 32x32x3 RGB
   - Class Balance: 10 classes (SVHN street digits)
   - Benchmark Difficulty: Severe lighting variation, cropped bounding box artifacts
   ```
   ````

---

## 3. High-Density Insights

Accompany the carousel with a concise, entity-dense breakdown:
- **Input Spec**: Resolution, channel depth, format, sample counts.
- **Intrinsic Difficulty**: Why standard baselines struggle (e.g., distractors, blur, class imbalance, sensor noise).
- **Recommended Modeling Strategy**: Architecture candidates, augmentation techniques (Cutout, Mixup, RandAugment), and loss functions.
- **Immediate Next Step**: Seamlessly transition to model training on Vertex AI or generating an explainer artifact.