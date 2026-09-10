# Multicrop Disease Dataset Inspection

This example demonstrates the output of Antigravity's **`visualize-dataset`** skill on the Multicrop Disease benchmark (21.8k images across 30 crop and pathogen classes).

## Antigravity Prompt

```text
Inspect the field samples my multicrop disease dataset and show me an in-chat visual carousel breakdown
```

---

## Output: Interactive Field Sample Inspector

Antigravity renders an in-chat visual inspection component featuring:
- **Interactive Crop Filtering**: Switch between `All Crops`, `Banana`, `Chilli`, `Groundnut`, `Cauliflower`, and `Radish`.
- **Annotation & Bounding Box Overlays**: Instant toggle of YOLOv8 object detection boxes for necrotic lesions, leaf spots, and insect damage.
- **Pathogen Profiles & Severity Ratings**: Granular diagnostic metadata including pathogen classification (e.g. *Pseudocercospora fijiensis* for Sigatoka), severity flags (`HIGH`, `MODERATE`), and native image dimensions (`640x640 RGB`).

![Multicrop Disease Field Sample Inspector](multicrop_inspector_carousel.png)

---

## Dataset Breakdown

| Crop | Classes & Pathogens | Total Images |
| :--- | :--- | :--- |
| **Banana** | Bract Mosaic Virus, Cordana, Healthy, Insect Pest, Moko, Panama, Pestalotiopsis, Sigatoka, Yellow Sigatoka | ~7,200 |
| **Chilli** | Anthracnose, Healthy, Leaf Curl, Leaf Spot, Whitefly, Yellowish | ~5,100 |
| **Groundnut** | Early Leaf Spot, Early Rust, Healthy, Late Leaf Spot, Nutrition Deficiency, Rust | ~4,300 |
| **Cauliflower** | Black Rot, Bacterial Spot Rot, Downy Mildew, Healthy | ~2,900 |
| **Radish** | Black Leaf Spot, Downey Mildew, Flea Beetle, Healthy, Mosaic | ~2,300 |
