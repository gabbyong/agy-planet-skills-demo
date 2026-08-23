#!/usr/bin/env python3
"""
render.py - Compiles a Markdown document into a standalone interactive HTML page.

Usage:
    uv run --with markdown-it-py --with pygments python .agents/skills/explain/scripts/render.py input.md -o output.html
"""

import os
import sys
import argparse
from pathlib import Path
import re
from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter

SKILL_DIR = Path(__file__).resolve().parent.parent
RESOURCES_DIR = SKILL_DIR / "resources"


def highlight_code(code: str, name: str, attrs: dict) -> str:
    lang = name.strip() if name else "text"
    try:
        lexer = get_lexer_by_name(lang)
    except Exception:
        lexer = TextLexer()
    formatter = HtmlFormatter(nowrap=True, style="friendly")
    highlighted = highlight(code, lexer, formatter)
    return f'<pre><code class="language-{lang}">{highlighted}</code></pre>'


def slugify(text: str) -> str:
    cleaned = "".join(c.lower() if c.isalnum() or c in " -_" else "" for c in text)
    return "-".join(cleaned.split())


def render_markdown(md_text: str, title: str) -> str:
    # 1. Normalize LaTeX delimiters \( ... \) -> $ ... $ and \[ ... \] -> $$ ... $$
    normalized_md = re.sub(r'\\\((.*?)\\\)', r'$\1$', md_text, flags=re.DOTALL)
    normalized_md = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', normalized_md, flags=re.DOTALL)

    # 2. Extract H2 headings for default Table of Contents
    h2_items = []
    for line in normalized_md.splitlines():
        if line.startswith("## "):
            h2_title = line[3:].strip()
            slug = slugify(h2_title)
            h2_items.append((h2_title, slug))

    toc_html = ""
    if len(h2_items) >= 2:
        list_items = "".join(f'<li><a href="#{slug}">{h2_title}</a></li>' for h2_title, slug in h2_items)
        toc_html = f'''<div class="toc-wrapper">
  <div class="toc-card">
    <div class="toc-title">Table of Contents</div>
    <ul class="toc-list">
      {list_items}
    </ul>
  </div>
</div>'''

    # 3. Parse markdown with syntax highlighting, tables, and dollarmath
    md = (
        MarkdownIt("commonmark", {
            "html": True,
            "highlight": highlight_code
        })
        .enable("table")
        .enable("strikethrough")
        .use(dollarmath_plugin, allow_space=True, allow_digits=True, double_inline=True)
    )

    rendered_body = md.render(normalized_md)

    # 3. Add IDs to <h2> tags so TOC anchors work
    for h2_title, slug in h2_items:
        rendered_body = rendered_body.replace(f"<h2>{h2_title}</h2>", f'<h2 id="{slug}">{h2_title}</h2>', 1)

    # Insert TOC directly after Title (h1) and Subtitle (first p)
    if toc_html and "<div class=\"toc-wrapper\"" not in rendered_body:
        h1_end = rendered_body.find("</h1>")
        if h1_end != -1:
            first_p_end = rendered_body.find("</p>", h1_end)
            if first_p_end != -1:
                # Add subtitle class to first paragraph if not present
                first_p_start = rendered_body.find("<p>", h1_end)
                if first_p_start != -1 and first_p_start < first_p_end:
                    rendered_body = (
                        rendered_body[:first_p_start]
                        + '<p class="subtitle">'
                        + rendered_body[first_p_start + 3:first_p_end + 4]
                        + "\n" + toc_html + "\n"
                        + rendered_body[first_p_end + 4:]
                    )
                else:
                    insert_pos = first_p_end + 4
                    rendered_body = rendered_body[:insert_pos] + "\n" + toc_html + "\n" + rendered_body[insert_pos:]
            else:
                insert_pos = h1_end + 5
                rendered_body = rendered_body[:insert_pos] + "\n" + toc_html + "\n" + rendered_body[insert_pos:]
        else:
            first_h2_idx = rendered_body.find("<h2")
            if first_h2_idx != -1:
                rendered_body = rendered_body[:first_h2_idx] + toc_html + "\n" + rendered_body[first_h2_idx:]
            else:
                rendered_body = toc_html + "\n" + rendered_body

    # 4. Load template & styles from resources
    template_path = RESOURCES_DIR / "template.html"
    styles_path = RESOURCES_DIR / "styles.css"

    template = template_path.read_text(encoding="utf-8")
    styles = styles_path.read_text(encoding="utf-8")

    # 5. Inject content into template
    return (
        template
        .replace("{{TITLE}}", title)
        .replace("{{STYLES}}", styles)
        .replace("{{CONTENT}}", rendered_body)
    )


def main():
    parser = argparse.ArgumentParser(description="Render markdown to interactive HTML explanation page.")
    parser.add_argument("input", help="Path to input markdown file")
    parser.add_argument("--output", "-o", required=True, help="Path to output HTML file")
    parser.add_argument("--title", "-t", default=None, help="Page title (optional)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    md_content = input_path.read_text(encoding="utf-8")
    title = args.title or input_path.stem.replace("-", " ").replace("_", " ").title()

    html_output = render_markdown(md_content, title=title)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_output, encoding="utf-8")

    print(f"Successfully generated HTML: {output_path}")


if __name__ == "__main__":
    main()
