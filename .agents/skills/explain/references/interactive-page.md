# Interactive Page Reference

When creating an interactive web explanation, the outcome should be a clean, self-contained single-page document saved in a temporary folder outside the repo and served locally, giving the user real conceptual context before diving into code.

> [!TIP]
> **Markdown-First Workflow:** You can simply write the explanation content in a Markdown file (e.g. `/tmp/content.md`), and compile it into a fully styled HTML page using the skill's build script:
> ```bash
> uv run --with markdown-it-py --with pygments python .agents/skills/explain/scripts/render.py /tmp/content.md -o /tmp/YYYY-MM-DD-explanation-<topic>.html
> ```
> This gives you clean default styles out of the box (Notion/Zen aesthetic, KaTeX math rendering, syntax-highlighted code blocks, and an automatically generated Table of Contents from `##` headings). You can customize or override any defaults in `scripts/render.py`, `resources/styles.css`, or `resources/template.html`.

---

## What Good Looks Like

- **Editorial Style**: Written in the clear, engaging, authoritative style of Martin Kleppmann. Explanations should be entity-dense, succinct, and conversational.
- **Context Over Just "Pretty Diagrams"**: Every visualizer must connect its moving parts to the real-world problem domain. Don't just display abstract numbers—explain what the inputs, weights, and outputs actually represent in the system (e.g. how a Sobel kernel detects house number edges vs. a blur filter smoothing camera glare).
- **Exploratory Openers**: Every interactive widget must have a preceding prose paragraph explaining *what* the component demonstrates, what real-world effect each control produces, and *how* to interact with it.
- **Notion / Japanese Scandi Zen Aesthetic (Provided Out of the Box)**:
  - Warm off-white canvas (`#fdfdfc`), deep charcoal typography (`#2e2e2c`), and soft subtle panel backgrounds (`#f7f6f3`).
  - Rely on natural whitespace and typographic hierarchy rather than boxy card borders, dark zinc gradients, or horizontal divider lines (`---`).
  - Avoid decorative emojis (like sparkles or fire). Keep headings clean and editorial.
- **Table of Contents**: Automatically generated from `##` headings as a horizontally centered card with cleanly left-aligned navigation links.
- **Interactive Component**: A responsive JavaScript visualizer (e.g. step-by-step matrix slider, filter presets, stride/padding controls, and click-to-inspect cells) with live calculation breakdowns.
- **Next Steps & Quiz**: Conclude with an interactive knowledge-check quiz (immediate feedback on click) and 2–3 concrete next steps to go deeper.

---

## Serving & Delivery Checklist

1. **Save Location**: Save the self-contained HTML file in a temporary folder outside the repo (e.g. `/tmp`) using a predictable naming pattern like `YYYY-MM-DD-explanation-<topic>.html`.
2. **Serve via `uv`**: Launch a background HTTP server using `uv run python3 -m http.server <port> --directory <dir>` if not already running.
3. **Provide Clickable Link**: Always output a clickable `http://localhost:<port>/<filename>.html` URL directly in your response so the user can open it in their browser.
4. **Visual Verification**: Verify page rendering with a quick Playwright screenshot before presenting.
