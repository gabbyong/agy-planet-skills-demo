---
name: skill-creator
description: Use this skill when you want to design, evaluate, or refine an agent skill. Encodes best practices for outcome-oriented authoring and eval-driven iteration.
---

# Skill Creator

When authoring or refining a skill, your goal is to help future agents achieve high-quality outcomes consistently without constraining them with rigid micro-rules. 

Focus on describing **what good looks like** and establishing a fast feedback loop to iterate from failures.

---

## 1. Core Authoring Principles

1. **Trigger on User Intent, Not Jargon**: The frontmatter `description` is the primary trigger mechanism. Write it to match how users actually phrase requests, and explicitly declare boundaries.

   *Eg. Instead of "A utility module for 2D convolution visualization", use "Use this when the user asks to visualize, explain, or understand datasets, algorithms, or code changes."*

2. **Active Directives Over Passive Information**: Models follow direct instructions much better than passive suggestions.

   *Eg. Instead of "Notion light mode is recommended", use "Use the Notion/Zen light palette (`#fdfdfc` canvas, `#2e2e2c` text, `#f7f6f3` panels)."*

3. **Grade Outcomes, Not Paths**: Describe the target state and the quality criteria for success, giving the model flexibility in how it gets there.

   *Eg. Instead of prescribing every terminal command, specify: "The final deliverable must be a clean, self-contained HTML page served on a local HTTP port and verified via screenshot."*

4. **Progressive Disclosure (`SKILL.md` + `references/`)**: Keep `SKILL.md` lean (under 40 lines) outlining core philosophy and intent. Move specialized format templates, design specs, or code boilerplates into `references/`.

5. **Learn from Failures as Insights**: When an agent produces a poor output, understand *why* (e.g. vague visual standard, ambiguous trigger) and clarify the outcome standard rather than adding narrow, reactive "never do X" rules.

---

## 2. The 3-Dimensional Quality Checklist

Before considering a skill complete, test it against these three criteria:

| Dimension | What to Verify | Example Verification |
| :--- | :--- | :--- |
| **1. Functional Outcome** | Does the output compile, render, or execute cleanly? | Verified with Playwright screenshot or terminal run. |
| **2. Style & Preferences** | Does it honor the user's aesthetic and layout rules? | Zen light mode, no decorative emojis, no arbitrary `---` lines. |
| **3. Token Efficiency** | Did it reach the solution with minimal thrashing? | Clean execution without repetitive polling or unnecessary bash retries. |

---

## 3. Standard Directory Structure

```
.agents/skills/<skill-name>/
├── SKILL.md                          # Main intent, user-intent trigger, and outcome criteria
└── references/                       # Domain templates, UI design tokens, or specific schemas
    ├── standard-template.md
    └── advanced-patterns.md
```
