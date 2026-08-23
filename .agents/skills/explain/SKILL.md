---
name: explain
description: Use this when the user asks for a rich explanation, visual guide, or interactive deep dive of a concept, codebase, algorithm, or product.
---

# Explain

When explaining a complex concept, system, or product, aim to provide a self-contained interactive artifact written in the clear, engaging, and entity-dense style of Martin Kleppmann and The Elements of Style.

Weave your explanation progressively from low-fidelity mental models to high-fidelity numerical rigor, supported by hand-drawn editorial illustrations, mathematical animations, and interactive widgets.

---

## Media & Modalities Reference

- [**Interactive Web Pages**](./references/interactive-page.md): Markdown-to-HTML pipeline with KaTeX math, `lukilabs/beautiful-mermaid` interactive diagrams, and diagnostic quizzes.
- [**Editorial Illustrations**](./references/illustrations.md): Hand-drawn character illustrations (Xiaohei) as cognitive anchors.
- [**Audio & Voiceover**](./references/audio.md): Studio narration using Gemini TTS (`Orus` voice).
- [**3Blue1Brown Animations**](./references/3b1b.md): Mathematical vector animations and neural network simulations via Manim.

---

## Workflow

1. **Identify Cognitive Anchors**: Find 1–3 key mechanisms or state transitions that benefit most from visual explanation. Use illustrations or animations where appropriate. Generate hand-drawn Xiaohei illustrations following [illustrations](./references/illustrations.md) or mathematical vector animations following [3b1b](./references/3b1b.md).

2. **Draft the Markdown**: Write the explanation in a Markdown document (e.g. `/tmp/content.md`), weaving together text, LaTeX math, code blocks, embedded images, videos, and declarative widgets following [interactive-page](./references/interactive-page.md).

3. **Generate Voiceover (Optional)**: If narration is requested, produce studio audio following [audio](./references/audio.md) using the `Orus` voice model and sync it to the video or page.

4. **Compile and Serve**: Compile the markdown into a self-contained HTML page using `scripts/render.py` and serve it on a local HTTP port.

5. **Follow Up in Chat**: Provide the clickable localhost URL in your response, ask diagnostic questions to gauge understanding, and suggest concrete next steps.

