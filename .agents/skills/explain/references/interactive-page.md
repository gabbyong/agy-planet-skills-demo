# Interactive Page Reference

When creating an interactive web explanation, write the content in a temporary markdown file outside the repo (such as `/tmp/content.md`) and compile it into a self-contained HTML page using `scripts/render.py`.

```bash
uv run --with markdown-it-py --with pygments python .agents/skills/explain/scripts/render.py /tmp/content.md -o /tmp/YYYY-MM-DD-explanation-<topic>.html
```

Write in the clear, engaging, entity-dense style of Martin Kleppmann and The Elements of Style. For algorithms and mathematical systems, always trace a single concrete numerical calculation forward and backward before discussing high-level abstractions.

Weave your explanation progressively using text, equations (`\(...\)` inline, `$$...$$` display), embedded illustrations, syntax-highlighted code blocks, and declarative HTML components.

`scripts/render.py` provides clean Notion/Zen styling out of the box with KaTeX math rendering, syntax highlighting, and an automatically generated Table of Contents from `##` headings. It also supports two declarative components with zero custom JavaScript required:

1. **Tabbed Inspector (`.tabs-container`):**
```html
<div class="tabs-container">
  <div class="tabs-header">Inspector Title</div>
  <div class="tab-buttons">
    <button class="btn btn-primary">Tab A</button>
    <button class="btn">Tab B</button>
  </div>
  <div class="tab-panel active">Content A</div>
  <div class="tab-panel">Content B</div>
</div>
```

2. **Self-Check Quiz (`.quiz-container`):**
```html
<div class="quiz-container">
  <div class="quiz-question">
    <div class="quiz-q-text">1. Question prompt here</div>
    <div class="quiz-options">
      <button class="quiz-opt" data-correct="true">Correct answer</button>
      <button class="quiz-opt" data-correct="false">Distractor</button>
    </div>
    <div class="quiz-feedback"></div>
  </div>
</div>
```

Always ensure the background HTTP server is running (`python3 -m http.server <port> --directory /tmp`) and output the clickable localhost link in your chat response. Use your chat response to ask diagnostic questions and suggest concrete next steps.
