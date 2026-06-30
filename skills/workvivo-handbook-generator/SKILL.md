---
name: workvivo-handbook-generator
description: Generate Medium-style handbook articles for Workvivo Pages from any source document (product guides, tool docs, technical READMEs, feature announcements). Produces a Markdown article, a 1190x250 cover image, and 3-5 topic diagrams, all in a consistent Gemini blue/purple/indigo visual palette that matches an existing handbook series. Use this skill whenever the user asks to "convert this into a Workvivo article/handbook," "make this into a Medium-style guide," "do the same [conversion] as before," or references turning a doc/README/guide into an internal handbook with diagrams. Also trigger when the user uploads a technical or product document and asks for it to be turned into something publishable on an internal comms/intranet platform. This skill produces internal enablement content (HR/comms tone), not developer documentation — keep code examples minimal and illustrative even for technical source material, unless the user explicitly asks for a developer-audience deep dive.
---

# Workvivo Handbook Generator

Converts a raw source document (tool guide, README, product doc, feature writeup) into a polished Workvivo Page: a Medium-style Markdown article + a cover image + a handful of custom diagrams, all sharing one consistent visual identity across however many handbooks the user builds over time.

This skill exists because Workvivo Pages use a block-based editor (headings, quotes, code blocks, image blocks) — it does NOT render custom CSS, custom fonts, or inline SVG. So the visual identity has to come from PNG images (cover + diagrams) plus careful use of Markdown structures that map onto Workvivo's actual blocks (blockquotes → Quote block, fenced code → Code block, etc).

## Before starting: confirm the audience

**Always ask (or infer from context) who will read this before writing.** The single biggest failure mode in this skill is matching the technical depth of the source document instead of the target audience. A raw developer README dropped in unmodified produces an unreadable article for a general audience.

Use `ask_user_input_v0` if it's not already clear from the conversation:
- Pure business/non-technical audience → strip almost all code, explain concepts with analogies
- Mixed audience (engineers + PMs + SREs, as is common for AI tooling) → keep 1-3 short illustrative code blocks max, explain mechanisms in plain English first, code second
- Pure developer audience doing a hands-on setup → fuller code blocks and command sequences are appropriate

When in doubt, default to mixed/light-technical — it's the safer failure mode and matches most of this skill's actual usage so far (AI developer toolkit articles for engineers, PMs, and SREs).

**The conversion is NOT 1:1.** A 300-line setup tutorial with line-by-line code walkthroughs should usually become a ~150-line conceptual article with 2-3 small code snippets — not a markdown-ified copy of the original. Synthesize and re-explain; don't transcribe.

## Workflow

### Step 1 — Read the source and identify the shape

Read the full source document. Identify:
- The core problem/concept being explained (this becomes the article's opening hook)
- 4-7 natural sections (these become H2 headings)
- 3-5 places where a diagram would clarify a structure, flow, comparison, or set of options better than prose
- Any genuinely necessary code/commands (keep only what's illustrative, cut the rest)

### Step 2 — Pick a title, subtitle, and cover motif

Title format: `# The [Subject] Handbook: [Short Subtitle]` or a more narrative title if the subject calls for it (e.g. "A Practical Guide to X"). Keep it short enough to fit two lines on the cover at 44px.

Cover motif — pick the one that fits the subject (see `scripts/diagram_kit.py` `cover()` docstring for all four):
- `spark` — general/default, AI assistant topics
- `terminal` — CLI tools, developer command-line topics
- `document` — content/research/writing tools
- `network` — architecture, protocols, multi-agent/multi-system topics

### Step 3 — Write the article in Medium style

Follow `references/article-template.md` for the exact structure and tone conventions. In short:
- Dek (italic one-liner) + byline + read time under the title
- A "here's what we'll cover" bullet list early on
- Pull quotes (blockquote `>`) at natural pauses — roughly one per 2-3 sections
- Bold lead-in phrases opening key paragraphs
- `[IMAGE: filename.png]` markers with an italic caption line beneath, placed where each diagram supports the surrounding text
- A closing "The takeaways" section: one summary pull-quote + a checklist of 5-6 items
- Hashtag footer line

Read `references/article-template.md` now if you haven't already — it has the full annotated structure and a tone checklist.

### Step 4 — Build the diagrams

Use `scripts/diagram_kit.py` — do NOT hand-write SVG from scratch. It has five reusable components, each suited to a different kind of content:

| Component | Use for |
|---|---|
| `linear_flow()` | Setup sequences, pipelines, ordered steps (3-5 steps) |
| `hub_and_spoke()` | A central thing connected to several related things (4 or 6 spokes) |
| `comparison()` | Two contrasting approaches side by side (vague/specific, problem/solution) |
| `card_grid()` | A flat list of N things — features, types, frameworks (clean multiple of cols) |
| `circular_loop()` | An iterative/cyclical process (3-5 stages) |

Import it directly:
```python
import sys
sys.path.insert(0, "/path/to/skill/scripts")
from diagram_kit import *

save_png(linear_flow(
    title="SECTION TITLE IN CAPS",
    steps=[("Step 1", ["detail line 1", "detail line 2"]), ...],
    caption="One italic sentence explaining the takeaway."
), "/mnt/user-data/outputs/topic_diagram_name.png")
```

All functions auto-escape special characters (`&`, `<`, `>`, quotes) — pass plain text directly, no manual escaping needed.

Pick 3-5 diagrams total per article — never more than one per major section, and never two in a row without prose between them (a wall of diagrams is as bad as a wall of code).

### Step 5 — Build the cover

```python
save_png(cover(
    title_lines=["The X Handbook"],   # or ["Line 1", "Line 2"] if it doesn't fit on one
    subtitle="Short italic subtitle",
    motif="spark",  # or terminal / document / network — see Step 2
), "/mnt/user-data/outputs/xyz_cover_1190x250.png", width=1190, height=250)
```

### Step 6 — Save and present

Save the Markdown file and all PNGs to `/mnt/user-data/outputs/`. Use a consistent filename prefix per article (e.g. `mcps_` for an MCP server article) so files are easy to identify together. Call `present_files` with the Markdown file first, then the cover, then the diagrams in the order they appear in the article.

### Step 7 — Explain the Workvivo assembly step

Always close with a short note (not a big block) on how to assemble in Workvivo: set the cover, paste the Markdown into the body, swap each `[IMAGE: ...]` marker for an Image block with the matching PNG and its caption.

## Common mistakes to avoid

- **Don't match source complexity 1:1.** Re-derive the explanation for the target audience; don't transcribe.
- **Don't skip the audience check.** This is the #1 cause of articles that "aren't even understandable" — ask before writing if it's unclear.
- **Don't write more than ~180-220 lines of Markdown.** If the source material is huge, pick the 5-7 most important sections rather than covering everything.
- **Don't hand-write SVG.** Always use `diagram_kit.py` — it guarantees palette consistency across the whole series and has escaping built in.
- **Don't use more than one H1.** Workvivo articles get exactly one title; everything else is H2/H3.
- **Don't forget the takeaways section.** Every article in this series ends with a one-line summary quote + checklist — it's part of the house style now.
