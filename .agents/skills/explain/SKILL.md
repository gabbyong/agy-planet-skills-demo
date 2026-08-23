---
name: explain
description: Use this when the user asks for a rich explanation, visual guide, or interactive deep dive of a concept, codebase, algorithm, or product.
---

# Explain

When explaining a complex concept, system, or product, aim to provide a self-contained interactive artifact written in the clear, engaging, and entity-dense style of Martin Kleppmann and The Elements of Style.

Weave your explanation progressively from low-fidelity mental models to high-fidelity numerical rigor, supported by hand-drawn editorial illustrations and interactive widgets.

Here is the standard workflow:

1. **Identify Cognitive Anchors**: Find 2–3 key mechanisms or state transitions that benefit most from visual explanation. Generate hand-drawn illustrations in parallel following [illustrations](./references/illustrations.md).

2. **Draft the Markdown**: Write the explanation in a Markdown document (e.g. `/tmp/content.md`), weaving together text, LaTeX math, code blocks, embedded images, and declarative widgets following [interactive-page](./references/interactive-page.md).

3. **Compile and Serve**: Compile the markdown into a self-contained HTML page using `scripts/render.py` and serve it on a local HTTP port.

4. **Follow Up in Chat**: Provide the clickable localhost URL in your response, ask diagnostic questions to gauge understanding, and suggest concrete next steps.
