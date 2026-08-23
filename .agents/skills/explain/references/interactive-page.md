# Interactive Page Reference

When creating an interactive web explanation, write the content in a temporary markdown file outside the repo (such as `/tmp/content.md`) and compile it into a self-contained HTML page using `scripts/render.py`.

```bash
uv run --with markdown-it-py --with mdit-py-plugins --with pygments python .agents/skills/explain/scripts/render.py /tmp/content.md -o /tmp/YYYY-MM-DD-explanation-<topic>.html
```

---

## What Good Looks Like

### 1. Intuition Grounded in Concrete Numbers
- The reader builds an immediate, durable mental model because abstract mechanisms are grounded in a worked numerical example (e.g. forward pass logits $\rightarrow$ softmax $\rightarrow$ loss $\rightarrow$ analytical gradient) before generalizing to large-scale abstractions.
- Explanations read like a chapter from Martin Kleppmann and *The Elements of Style*: authoritative, entity-dense, active-voiced, and focused on mechanical realities.

### 2. Rhythmic, Uncluttered Reading Flow
- The page flows seamlessly from title to subtitle, through the table of contents, and into the narrative without arbitrary horizontal rules or awkward visual clusters.
- Visual elements (Xiaohei editorial sketches, architecture diagrams, code listings) serve as natural pauses in the exposition—each visual asset directly illustrates the preceding thought and is unpacked by the subsequent paragraph, never competing for attention in adjacent stacks.

### 3. Living, Interactive Visualizations & Equations
- Architecture and data-flow diagrams are not static images; readers can explore, pan, and zoom into complex topologies rendered via `lukilabs/beautiful-mermaid`.
- Mathematical formulas render crisply in KaTeX, preserving mathematical rigor across both inline notation and multi-line derivations.

### 4. Active Retention & Self-Correction
- Readers can actively test their grasp of subtle mechanics through self-contained interactive diagnostic questions that provide immediate corrective insight.

---

## Custom HTML & Components

If you want to add custom HTML (such as self-check quizzes), embed declarative markup directly:

**Self-Check Quiz (`.quiz-container`):**
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

