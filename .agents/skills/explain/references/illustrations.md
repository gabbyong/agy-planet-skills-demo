# Illustrations

When explaining technical concepts, use hand-drawn visual metaphors to give readers memorable cognitive anchors. Each illustration should capture a single mechanism, state transition, or friction point.

Always write your prompts to generate 16:9 horizontal images on a pure solid white background with minimalist black hand-drawn ink lines. Use sparse handwritten English annotations with restrained accent colors: orange for flow/pathways, red for bottlenecks or warnings, and blue for secondary notes.

The central recurring character is Xiaohei: a cute, chubby round bean-shaped solid black character with simple round white dot eyes, thin stick limbs, often standing on a small wooden stool. Xiaohei must actively operate the mechanism—turning valves, holding shields, or aiming pointers—never standing as a passive mascot.

Always identify 2–3 key conceptual turning points and generate your illustrations in parallel using `generate_image`. You can pass one of the reference images in `resources/examples/` to `ImagePaths` for visual calibration:

- `resources/examples/01-comparison.jpg`: Side-by-side comparison with label badges and shields.
- `resources/examples/02-reservoir.jpg`: Physical reservoir mechanism with active valve dispensing.
- `resources/examples/03-mechanism.jpg`: Multi-target arrows showing internal component interactions.

Here is a standard prompt recipe:

```text
Generate a 16:9 horizontal minimalist hand-drawn illustration with all annotations in English.

Character:
Cute, chubby round bean-shaped solid black character with two simple round white dot eyes and tiny stick limbs, standing on a small wooden stool.

Scene ({Concept Topic}):
On a pure solid white background (#ffffff), {Detailed scene: character actively operating machine/tool, labeled parts, arrows, and target effect}.

Annotations (English handwritten notes):
- Main object label: "{Label 1}"
- Flow/arrow label: "{Label 2}"
- Result badge: "{Label 3}"

Style:
Pure white background, clean black hand-drawn pen linework with organic wobble, generous empty white space, sparse red, orange, and blue handwritten English annotations. Clean, cute, whimsical product sketch.
```

Copy generated images to your output directory and embed them directly under the corresponding section in markdown using `![Caption](image_name.jpg)`.
