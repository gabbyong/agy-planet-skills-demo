---
name: explain
description: Use this when the user asks for an explanation, visual guide, interactive deep dive, or architecture walkthrough of a concept, algorithm, or model.
---

# Explain

Deliver deep, engaging, and multi-modal explanations by immediately generating two complementary artifacts:
1. An **Antigravity Markdown Artifact** in chat.
2. A **Self-Contained Interactive HTML Artifact** ready for local viewing.

---

## 1. Immediate Artifact Generation

When invoked, do not stall or produce plain text in chat. Immediately create:

1. **The Antigravity Artifact (`artifact.md`)**:
   - Write to the conversation artifact directory (`<appDataDir>/brain/<conversation-id>/...`).
   - Structure with entity-dense technical breakdowns, KaTeX math formulas, Mermaid architecture diagrams, and GitHub callout alerts.
   - Embed media using `![caption](/absolute/path/to/media.jpg)`.

2. **The Interactive HTML Artifact (`index.html`)**:
   - Produce a standalone, styled HTML document (using `scripts/render.py` or a dedicated single-file HTML/CSS/JS page).
   - Include interactive UI controls: dynamic parameter sliders, step-by-step state machines, reactive visualizers, or self-checking quizzes.
   - Reference templates in `examples/explain/` (e.g., `agent-harness`, `llm-training`, `resnet-18`).

---

## 2. Media & Modalities Reference

- [**Interactive Web Pages**](./references/interactive-page.md): KaTeX math, beautiful diagrams, and interactive state widgets.
- [**Editorial Illustrations**](./references/illustrations.md): Hand-drawn character illustrations (Xiaohei) for intuitive conceptual anchoring.
- [**3Blue1Brown Animations**](./references/3b1b.md): Mathematical vector simulations and optimization dynamics rendered via Manim.
- [**Audio & Voiceover**](./references/audio.md): Studio narration using Gemini TTS (`Orus` voice).

---

## 3. Serving & Presenting to User

1. **Serve Locally**: Serve the interactive HTML artifact (e.g. `python3 -m http.server 8080 --directory <dir>`).
2. **Respond in Chat**:
   - Point the user to the generated Antigravity artifact.
   - Provide the clickable link to the interactive HTML page (`http://localhost:8080/...`).
   - Summarize the single most non-obvious mathematical or architectural intuition.

