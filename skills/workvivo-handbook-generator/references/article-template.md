# Article Template & Tone Guide

This is the house style for the Workvivo handbook series. Every article so far
(Gemini Enterprise, NotebookLM, Gemini CLI, Prompt Engineering, Antigravity,
Code Assist, Agent Architecture, MCP Server) follows this exact skeleton.
Match it closely — consistency across the series matters more than novelty
in any single article.

## Full skeleton

```markdown
# [Title]: [Subtitle]

*[One-sentence italic dek — what the reader will walk away with]*

**The Enablement Team**  ·  [N] min read  ·  [optional series tag]

---

[Opening paragraph: state the problem/gap in plain terms. 2-4 sentences.]

[Second paragraph: introduce the solution/tool/concept as the answer to that gap.]

Here's what we'll cover:

- **[Section topic]** — [one-line description]
- **[Section topic]** — [one-line description]
- **[Section topic]** — [one-line description]
- ... (4-7 bullets matching the H2 sections below)

> [Pull quote: the single most important conceptual point of the whole article,
> stated once, memorably, in one or two sentences.]

---

## 1 · [Section Title]

**[Bold lead-in sentence stating the core point of this section.]** [Supporting
prose, 2-4 sentences.]

[IMAGE: diagram_filename.png]
*[Italic caption — one sentence explaining what the diagram shows and why it matters.]*

[More prose, or a bulleted breakdown if listing discrete items:]

- **[Item]** — [description]
- **[Item]** — [description]

> [Optional secondary pull quote or "try this" / "quick check" callout —
> use sparingly, roughly one per 2-3 sections, not in every section.]

---

## 2 · [Section Title]

... (repeat pattern)

---

## The takeaways

> **In one line:** [Single sentence synthesizing the entire article's advice.]

- ✅ **[Action]** — [brief elaboration]
- ✅ **[Action]** — [brief elaboration]
- ✅ **[Action]** — [brief elaboration]
- ✅ **[Action]** — [brief elaboration]
- ✅ **[Action]** — [brief elaboration]
- ✅ **[Action]** — [brief elaboration]

[One closing sentence — warm, forward-looking, not salesy.]

*Accelerate your day-to-day: leveraging AI as a team.*

---

`#HashTag1`  ·  `#HashTag2`  ·  `#HashTag3`  ·  `#HashTag4`  ·  `#HashTag5`
```

## Tone rules

**Warm, not rude.** The very first draft of this series was rejected for being
"rude" — it used phrases like "let's be honest," "stop treating," language that
talks down to the reader or frames them as the problem. Never do this. Address
the reader as a competent colleague who just hasn't seen this workflow yet.

**No second person scolding.** Avoid "you're probably doing this wrong" framing.
Prefer "here's how to get more out of X" framing.

**Bold lead-ins, not headers-as-sentences.** Open paragraphs with a bolded
clause that states the point, then continue in normal prose:
`**The shift from asking to engineering is the whole game.** Most people...`
This is different from a header — it's inline emphasis at the start of a
paragraph, used 1-2 times per major section.

**Pull quotes carry the emotional/conceptual weight.** Every blockquote should
be quotable on its own, stripped of the surrounding context. If it only makes
sense with the paragraph before it, it's not pull-quote material — make it a
sentence in the prose instead.

**Checklists at the end only.** Don't bullet-point every section — most
sections should be prose with maybe one supporting bulleted breakdown. The
checklist format is reserved for "The takeaways" at the very end.

**Code blocks are illustrative, not exhaustive.** Even for technical source
material, keep code examples short (5-15 lines) and focused on the one thing
being taught. If the source has long code walkthroughs, summarize the
mechanism in prose and show only the most illustrative snippet.

## Image placement conventions

- One `[IMAGE: ...]` marker per major section maximum, never two in a row
- Always followed immediately by an italic caption line
- Place the marker after the prose that sets up what the diagram shows, not
  before — the reader should know what they're about to look at
- 3-5 diagrams total per article (plus the cover) is the right range; fewer
  than 3 feels sparse for an 800+ word article, more than 5 fragments the
  reading experience

## Mapping to Workvivo blocks

| Markdown element | Workvivo block |
|---|---|
| `# Title` | Page title (used once) |
| `## Heading` | H2 heading block |
| `> quote` | Quote block |
| `` ```code``` `` | Code block |
| `` `inline` `` | Inline code |
| `- bullet` | Bulleted list |
| `[IMAGE: x.png]` + caption | Image block (manual swap — Workvivo doesn't auto-render this syntax, it's a placeholder for the person assembling the page) |
| `---` | Divider |
| `*italic*` | Italic text |
| `**bold**` | Bold text |

## Length guidance

Target 150-220 lines of Markdown source (roughly 1,400-2,200 words). This
maps to a 6-9 minute read, which is the range every article in the series
has used in its byline. If source material would naturally produce more,
cut sections rather than compress every section — pick the 5-7 most
important ideas and go deep on those instead of shallow on everything.
