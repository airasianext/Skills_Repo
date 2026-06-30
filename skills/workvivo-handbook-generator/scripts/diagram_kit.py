"""
diagram_kit.py — Reusable diagram + cover generator for Workvivo handbook articles.

Palette: Gemini blue/purple/indigo (matches the handbook series cover gradient).
All functions return an SVG string; pass it to save_png() to render a PNG file
sized for Workvivo image blocks.

Usage pattern (see SKILL.md for the full workflow):

    from diagram_kit import *

    save_png(linear_flow(
        title="GETTING UP AND RUNNING",
        steps=[
            ("Install", ["Node.js + npm", "install -g gemini-cli"]),
            ("Authenticate", ["Type gemini", "Sign in via browser"]),
            ("Configure", ["Set PROJECT ID", "Update PATH"]),
            ("Verify", ["gemini --version", "Ready from any folder"], True),
        ],
        caption="Settings persist in ~/.gemini/settings.json across sessions."
    ), "my_diagram.png")

    save_png(cover(
        title_lines=["The Gemini CLI Handbook"],
        subtitle="AI at Your Command Line",
        motif="terminal",
    ), "cover_1190x250.png", width=1190, height=250)

All user-supplied text is automatically XML-escaped — safe to pass strings
containing &, <, >, quotes, etc.
"""

import math
import cairosvg

# ---------------------------------------------------------------------------
# PALETTE — do not deviate. This is what makes every handbook in the series
# look like it belongs to the same family.
# ---------------------------------------------------------------------------
INK = "#1b1340"            # deep indigo — hub nodes, "final state" cards
PAPER = "#ffffff"
BLUE = "#1a73e8"
BLUE_D = "#1452b0"
BLUE_SOFT = "#e3edfd"
BLUE_BRD = "#9bc0f5"
PURPLE = "#7c3aa6"
PURPLE_D = "#5e2a82"
PURPLE_SOFT = "#efe4f6"
PURPLE_BRD = "#c9a9dd"
MUT = "#7d7596"            # muted label gray-purple (section eyebrows)
SOFT = "#4a4368"           # body / sub text
LINE = "#d9d1ea"           # connector lines, dashed dividers
ACCENT_LIGHT = "#b89bff"   # small accent text on dark INK backgrounds

SANS = "font-family='DejaVu Sans, sans-serif'"
MONO_ATTR = 'font-family="DejaVu Sans Mono, monospace"'

# Alternate blue/purple fill so consecutive cards in a grid don't look identical
PALETTE_CYCLE = [
    (BLUE_SOFT, BLUE_BRD, BLUE_D),
    (PURPLE_SOFT, PURPLE_BRD, PURPLE_D),
]


def _esc(text) -> str:
    """Escape special XML characters so labels with &, <, >, quotes don't break SVG parsing."""
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&apos;"))


def save_png(svg_string: str, path: str, width: int = 1520, height: int = None):
    """Render an SVG string to a PNG file at the given path."""
    kwargs = {"output_width": width}
    if height:
        kwargs["output_height"] = height
    cairosvg.svg2png(bytestring=svg_string.encode(), write_to=path, **kwargs)
    print(f"wrote {path}")


# ---------------------------------------------------------------------------
# COMPONENT 1: Linear flow (A -> B -> C -> D)
# Use for: setup sequences, pipelines, step-by-step processes. 3-5 steps ideal.
# ---------------------------------------------------------------------------
def linear_flow(title, steps, caption=None, width=820, card_h=100):
    """
    steps: list of (label, [line1, line2]) or (label, [lines], is_final_dark_node)
    Set the third tuple element True to force a step to render as a dark
    "destination reached" card instead of the alternating blue/purple.
    """
    n = len(steps)
    pad = 20
    gap = 14
    cw = (width - pad * 2 - gap * (n - 1)) // n
    h = card_h + (130 if caption else 90)

    cards = ""
    for i, step in enumerate(steps):
        label = _esc(step[0])
        lines = [_esc(l) for l in step[1][:3]]
        is_dark = step[2] if len(step) > 2 else False
        x = pad + i * (cw + gap)
        y = 64
        cx = x + cw // 2

        if is_dark:
            fill, txt, sub, stroke = INK, PAPER, ACCENT_LIGHT, ""
        else:
            fill, brd, txt = PALETTE_CYCLE[i % 2]
            sub = SOFT
            stroke = f'stroke="{brd}" stroke-width="1.5"'

        cards += f'<rect x="{x}" y="{y}" width="{cw}" height="{card_h}" rx="12" fill="{fill}" {stroke}/>\n'
        cards += f'<text x="{cx}" y="{y+34}" text-anchor="middle" font-size="14" font-weight="bold" fill="{txt}">{label}</text>\n'
        for li, line in enumerate(lines):
            cards += f'<text x="{cx}" y="{y+56+li*18}" text-anchor="middle" font-size="11.5" fill="{sub}">{line}</text>\n'

        if i < n - 1:
            ax = x + cw + 2
            ay = y + card_h // 2
            col = BLUE if i % 2 == 0 else PURPLE
            cards += (f'<line x1="{ax}" y1="{ay}" x2="{ax+gap-2}" y2="{ay}" '
                      f'stroke="{col}" stroke-width="2" marker-end="url(#flow_arrow)"/>\n')

    caption_svg = ""
    if caption:
        caption_svg = (f'<text x="{width//2}" y="{h-22}" text-anchor="middle" font-size="13" '
                        f'fill="{SOFT}" font-style="italic">{_esc(caption)}</text>\n')

    return (f'<svg viewBox="0 0 {width} {h}" xmlns="http://www.w3.org/2000/svg" {SANS}>\n'
            f'<rect width="{width}" height="{h}" fill="{PAPER}"/>\n'
            f'<defs><marker id="flow_arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">'
            f'<path d="M0,0 L8,5 L0,10 Z" fill="{BLUE_BRD}"/></marker></defs>\n'
            f'<text x="{width//2}" y="36" text-anchor="middle" font-size="14" font-weight="bold" '
            f'fill="{MUT}" letter-spacing="3">{_esc(title)}</text>\n'
            + cards + caption_svg + '</svg>')


# ---------------------------------------------------------------------------
# COMPONENT 2: Hub and spoke (central concept + 3-6 related items)
# Use for: "X connects to these specialized things", architecture overviews
# ---------------------------------------------------------------------------
def hub_and_spoke(hub_label_lines, spokes, title=None, width=760, height=380):
    """
    hub_label_lines: 1-3 short lines shown inside the central dark circle
    spokes: list of (title, subtitle) — 4 or 6 items recommended for clean symmetry
    """
    cx, cy = width // 2, height // 2 + 10
    n = len(spokes)
    r_line = min(width, height) * 0.36
    node_w, node_h = 200, 64

    # For 4 spokes, offset 45deg so nodes land in corners (diamond layout)
    # rather than directly left/right of the hub, which causes label collision.
    start_angle = -45 if n == 4 else -90
    angles = [(start_angle + i * (360 / n)) for i in range(n)]

    lines_svg = ""
    nodes_svg = ""
    for i, (angle, (s_title, s_sub)) in enumerate(zip(angles, spokes)):
        rad = math.radians(angle)
        nx = cx + r_line * math.cos(rad)
        ny = cy + r_line * math.sin(rad)
        fill, brd, txt = PALETTE_CYCLE[i % 2]
        lines_svg += f'<line x1="{cx}" y1="{cy}" x2="{nx:.0f}" y2="{ny:.0f}" stroke="{LINE}" stroke-width="2"/>\n'
        nx0 = nx - node_w / 2
        ny0 = ny - node_h / 2
        nodes_svg += (
            f'<rect x="{nx0:.0f}" y="{ny0:.0f}" width="{node_w}" height="{node_h}" rx="12" '
            f'fill="{fill}" stroke="{brd}" stroke-width="1.5"/>\n'
            f'<text x="{nx:.0f}" y="{ny-4:.0f}" text-anchor="middle" font-size="13" font-weight="bold" fill="{txt}">{_esc(s_title)}</text>\n'
            f'<text x="{nx:.0f}" y="{ny+14:.0f}" text-anchor="middle" font-size="11" fill="{SOFT}">{_esc(s_sub)}</text>\n'
        )

    hub_lines_svg = ""
    base_y = cy - (len(hub_label_lines) - 1) * 9
    for i, line in enumerate(hub_label_lines):
        hub_lines_svg += (f'<text x="{cx}" y="{base_y + i*18}" text-anchor="middle" font-size="14" '
                           f'font-weight="bold" fill="{PAPER}">{_esc(line)}</text>\n')

    title_svg = ""
    if title:
        title_svg = (f'<text x="{width//2}" y="32" text-anchor="middle" font-size="14" font-weight="bold" '
                      f'fill="{MUT}" letter-spacing="3">{_esc(title)}</text>\n')

    return (f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" {SANS}>\n'
            f'<rect width="{width}" height="{height}" fill="{PAPER}"/>\n'
            + title_svg + lines_svg + nodes_svg +
            f'<circle cx="{cx}" cy="{cy}" r="56" fill="{INK}"/>\n'
            + hub_lines_svg + '</svg>')


# ---------------------------------------------------------------------------
# COMPONENT 3: Comparison cards (vague vs specific, problem vs solution)
# Use for: contrasting two approaches side by side
# ---------------------------------------------------------------------------
def comparison(left_label, left_lines, left_icon, right_label, right_lines, right_icon,
               width=760, height=300):
    """
    left_icon / right_icon: '!' (warning, renders purple) or 'check' (renders blue).
    Convention: left = problem/negative (purple), right = solution/positive (blue).
    """
    card_w = (width - 72) // 2
    right_x = 38 + card_w

    def icon(cx_icon, kind):
        if kind == '!':
            return (f'<circle cx="{cx_icon}" cy="76" r="13" fill="{PURPLE_SOFT}"/>'
                     f'<text x="{cx_icon}" y="82" text-anchor="middle" font-size="16" font-weight="bold" fill="{PURPLE_D}">!</text>')
        return (f'<circle cx="{cx_icon}" cy="76" r="13" fill="#cfe1fb"/>'
                f'<path d="M{cx_icon-6} 76 l4 4 l8 -9" fill="none" stroke="{BLUE_D}" '
                f'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>')

    icon_l = icon(34 + card_w - 30, left_icon)
    icon_r = icon(right_x + card_w - 30, right_icon)

    left_lines_svg = "".join(
        f'<text x="58" y="{128+i*22}" font-size="12.5" fill="{SOFT}">{_esc(ln)}</text>\n'
        for i, ln in enumerate(left_lines)
    )
    right_lines_svg = "".join(
        f'<text x="{right_x+24}" y="{128+i*22}" font-size="12.5" fill="{SOFT}">{_esc(ln)}</text>\n'
        for i, ln in enumerate(right_lines)
    )

    return f'''<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" {SANS}>
<rect width="{width}" height="{height}" fill="{PAPER}"/>
<rect x="34" y="44" width="{card_w}" height="{height-78}" rx="14" fill="{PURPLE_SOFT}" stroke="{PURPLE_BRD}" stroke-width="1.5"/>
<text x="58" y="82" font-size="14" font-weight="bold" fill="{PURPLE_D}">{_esc(left_label)}</text>
{icon_l}
<line x1="58" y1="96" x2="{34+card_w-24}" y2="96" stroke="{PURPLE_BRD}" stroke-width="1" stroke-dasharray="4 3"/>
{left_lines_svg}
<rect x="{right_x}" y="44" width="{card_w}" height="{height-78}" rx="14" fill="{BLUE_SOFT}" stroke="{BLUE_BRD}" stroke-width="1.5"/>
<text x="{right_x+24}" y="82" font-size="14" font-weight="bold" fill="{BLUE_D}">{_esc(right_label)}</text>
{icon_r}
<line x1="{right_x+24}" y1="96" x2="{right_x+card_w-24}" y2="96" stroke="{BLUE_BRD}" stroke-width="1" stroke-dasharray="4 3"/>
{right_lines_svg}
</svg>'''


# ---------------------------------------------------------------------------
# COMPONENT 4: Grid of cards (2x2, 2x3, 3x3) — for "N things" lists
# Use for: feature lists, frameworks, output types, business use cases
# ---------------------------------------------------------------------------
def card_grid(title, items, cols=2, width=760, card_h=110):
    """
    items: list of (heading, subtitle) tuples. Use a clean multiple of cols
    (4 items/2 cols, 6 items/3 cols, 9 items/3 cols) for a tidy grid.
    """
    n = len(items)
    rows = (n + cols - 1) // cols
    pad = 32
    gap = 16
    cw = (width - pad * 2 - gap * (cols - 1)) // cols
    height = 64 + rows * card_h + (rows - 1) * gap + 20

    cards = ""
    for i, (heading, sub) in enumerate(items):
        col = i % cols
        row = i // cols
        x = pad + col * (cw + gap)
        y = 64 + row * (card_h + gap)
        cx = x + cw // 2
        fill, brd, txt = PALETTE_CYCLE[i % 2]
        cards += (
            f'<rect x="{x}" y="{y}" width="{cw}" height="{card_h}" rx="12" fill="{fill}" stroke="{brd}" stroke-width="1.5"/>\n'
            f'<text x="{cx}" y="{y+card_h//2-6}" text-anchor="middle" font-size="15" font-weight="bold" fill="{txt}">{_esc(heading)}</text>\n'
            f'<text x="{cx}" y="{y+card_h//2+16}" text-anchor="middle" font-size="11.5" fill="{SOFT}">{_esc(sub)}</text>\n'
        )

    return (f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" {SANS}>\n'
            f'<rect width="{width}" height="{height}" fill="{PAPER}"/>\n'
            f'<text x="{width//2}" y="40" text-anchor="middle" font-size="14" font-weight="bold" '
            f'fill="{MUT}" letter-spacing="3">{_esc(title)}</text>\n'
            + cards + '</svg>')


# ---------------------------------------------------------------------------
# COMPONENT 5: Circular loop (Draft -> Test -> Analyze -> Refine -> back to Draft)
# Use for: iterative cycles, feedback loops, refinement processes. 3-5 nodes ideal.
# ---------------------------------------------------------------------------
def circular_loop(center_lines, nodes, title=None, width=760, height=400):
    """
    nodes: list of (title, [subtitle_line1, subtitle_line2])
    center_lines: 2-3 short lines for the hub circle (3rd line renders smaller/accent)
    """
    cx, cy = width // 2, height // 2 + 6
    n = len(nodes)
    r = min(width, height) * 0.35
    nw, nh = 158, 76

    node_svgs = ""
    arrows = ""
    for i, (n_title, sub_lines) in enumerate(nodes):
        angle = i * (360 / n)
        rad = math.radians(angle - 90)
        nx = cx + r * math.cos(rad) - nw / 2
        ny = cy + r * math.sin(rad) - nh / 2
        ncx = nx + nw / 2
        ncy = ny + nh / 2
        fill, brd, txt = PALETTE_CYCLE[i % 2]
        node_svgs += f'<rect x="{nx:.0f}" y="{ny:.0f}" width="{nw}" height="{nh}" rx="12" fill="{fill}" stroke="{brd}" stroke-width="1.5"/>\n'
        node_svgs += f'<text x="{ncx:.0f}" y="{ncy-10:.0f}" text-anchor="middle" font-size="14" font-weight="bold" fill="{txt}">{_esc(n_title)}</text>\n'
        for li, line in enumerate(sub_lines[:2]):
            node_svgs += f'<text x="{ncx:.0f}" y="{ncy+8+li*18:.0f}" text-anchor="middle" font-size="11" fill="{SOFT}">{_esc(line)}</text>\n'

        next_angle = angle + (360 / n)
        nr2 = math.radians(next_angle - 90)
        cp_angle = math.radians(angle + (360 / n) / 2 - 90)
        cpx = cx + (r + 40) * math.cos(cp_angle)
        cpy = cy + (r + 40) * math.sin(cp_angle)
        x1 = cx + r * math.cos(rad)
        y1 = cy + r * math.sin(rad)
        x2 = cx + r * math.cos(nr2)
        y2 = cy + r * math.sin(nr2)
        arrows += (f'<path d="M {x1:.0f} {y1:.0f} Q {cpx:.0f} {cpy:.0f} {x2:.0f} {y2:.0f}" '
                   f'fill="none" stroke="{BLUE_BRD}" stroke-width="2" marker-end="url(#loop_arrow)"/>\n')

    center_svg = ""
    base_y = cy - (len(center_lines) - 1) * 9
    for i, line in enumerate(center_lines):
        color = PAPER if i < 2 else ACCENT_LIGHT
        size = 13 if i < 2 else 10
        center_svg += (f'<text x="{cx}" y="{base_y+i*18}" text-anchor="middle" font-size="{size}" '
                        f'font-weight="bold" fill="{color}">{_esc(line)}</text>\n')

    title_svg = ""
    if title:
        title_svg = (f'<text x="{width//2}" y="32" text-anchor="middle" font-size="14" font-weight="bold" '
                      f'fill="{MUT}" letter-spacing="3">{_esc(title)}</text>\n')

    return (f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" {SANS}>\n'
            f'<rect width="{width}" height="{height}" fill="{PAPER}"/>\n'
            f'<defs><marker id="loop_arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">'
            f'<path d="M0,0 L8,5 L0,10 Z" fill="{BLUE_BRD}"/></marker></defs>\n'
            + title_svg + arrows + node_svgs +
            f'<circle cx="{cx}" cy="{cy}" r="56" fill="{INK}"/>\n'
            + center_svg + '</svg>')


# ---------------------------------------------------------------------------
# COVER GENERATOR — 1190x250, the standard Workvivo page-cover dimension
# ---------------------------------------------------------------------------
def cover(title_lines, subtitle, motif="spark"):
    """
    title_lines: 1-2 lines for the main title (keep each under ~28 chars to fit)
    subtitle: italic line beneath the title
    motif: 'spark' (4-point star nodes, general/default), 'document' (file
           rectangles, for content/research tools), 'terminal' (mono
           command-line snippet, for CLI/dev tools), 'network' (hub + dots,
           for architecture/protocol topics) — pick whichever fits best.
    """
    title_svg = ""
    if len(title_lines) == 1:
        y_start = 118
        line_gap = 52
        subtitle_y = 202
    else:
        y_start = 110
        line_gap = 52
        subtitle_y = y_start + line_gap + 36

    for i, line in enumerate(title_lines[:2]):
        title_svg += f'<text x="70" y="{y_start + i*line_gap}" font-size="44" font-weight="bold" fill="#ffffff">{_esc(line)}</text>\n'

    motif_svg = _cover_motif(motif)

    return f'''<svg viewBox="0 0 1190 250" xmlns="http://www.w3.org/2000/svg" {SANS}>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#1b1340"/><stop offset="0.45" stop-color="#3b2a7a"/>
<stop offset="0.75" stop-color="#7c3aa6"/><stop offset="1" stop-color="#b14a9a"/>
</linearGradient>
<linearGradient id="sp" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#4796e3"/><stop offset="0.5" stop-color="#9b72cb"/>
<stop offset="1" stop-color="#e88aa8"/>
</linearGradient>
<radialGradient id="gl" cx="0.8" cy="0.35" r="0.65">
<stop offset="0" stop-color="#8a5cff" stop-opacity="0.45"/>
<stop offset="1" stop-color="#8a5cff" stop-opacity="0"/>
</radialGradient>
</defs>
<rect width="1190" height="250" fill="url(#bg)"/>
<rect width="1190" height="250" fill="url(#gl)"/>
{motif_svg}
{title_svg}
<text x="70" y="{subtitle_y}" font-size="18" fill="#e6dcff" font-style="italic">{_esc(subtitle)}</text>
</svg>'''


def _cover_motif(motif):
    if motif == "network":
        return '''<g opacity="0.55" stroke="url(#sp)" stroke-width="1.3" fill="none">
<circle cx="980" cy="125" r="40"/>
<circle cx="860" cy="68" r="18"/><circle cx="1100" cy="72" r="18"/>
<circle cx="850" cy="190" r="18"/><circle cx="1105" cy="185" r="18"/>
<circle cx="980" cy="44" r="14"/>
<line x1="980" y1="125" x2="860" y2="68"/>
<line x1="980" y1="125" x2="1100" y2="72"/>
<line x1="980" y1="125" x2="850" y2="190"/>
<line x1="980" y1="125" x2="1105" y2="185"/>
<line x1="980" y1="125" x2="980" y2="44"/>
</g>'''
    if motif == "document":
        return '''<g opacity="0.55" stroke="url(#sp)" stroke-width="1.4" fill="none">
<rect x="900" y="54" width="118" height="148" rx="14"/>
<rect x="916" y="70" width="86" height="12" rx="4"/>
<rect x="916" y="90" width="70" height="8" rx="3"/>
<rect x="916" y="104" width="80" height="8" rx="3"/>
<line x1="916" y1="140" x2="986" y2="140"/>
<rect x="916" y="152" width="86" height="8" rx="3"/>
</g>'''
    if motif == "terminal":
        return f'''<g opacity="0.5" stroke="url(#sp)" stroke-width="1.3" fill="none">
<rect x="888" y="44" width="272" height="162" rx="14"/>
</g>
<text x="910" y="80" {MONO_ATTR} font-size="12" fill="#9bc0f5" opacity="0.7">$ ready</text>
<text x="910" y="100" {MONO_ATTR} font-size="12" fill="#c9a9dd" opacity="0.6">  Authenticated</text>'''
    # default: 'spark'
    return '''<g opacity="0.55" stroke="url(#sp)" stroke-width="1.4" fill="none">
<circle cx="980" cy="125" r="46" opacity="0.55"/>
<line x1="980" y1="125" x2="880" y2="62"/><line x1="980" y1="125" x2="1090" y2="70"/>
<line x1="980" y1="125" x2="885" y2="200"/><line x1="980" y1="125" x2="1095" y2="195"/>
</g>
<g fill="url(#sp)">
<circle cx="880" cy="62" r="7"/><circle cx="1090" cy="70" r="7"/>
<circle cx="885" cy="200" r="7"/><circle cx="1095" cy="195" r="7"/>
</g>'''
