"""Builds assets/card-dark.svg and assets/card-light.svg.

Edit the CONTENT section, then run from the repo root:
    pip install fonttools
    python scripts/build_card.py
"""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

# ───────────── CONTENT (edit me) ─────────────
NAME = "Amaan Sheikh"
SUBTITLE = "just a guy who builds things that help people (hopefully)"
ABOUT = (
    "hey, i'm amaan! right now i'm building ai tools for lawyers at "
    "oneauris and running ub forge, a crew of 250+ student builders. "
    "before that i was at ibm and catchu. outside of code i'm usually "
    "side questing, whether that's playing volleyball, finding new food "
    "spots, watching or making films with friends, or trying to find "
    "places i can travel to with money i don't have."
)
# ─────────────────────────────────────────────

THEMES = {
    "dark":  dict(fg="#F0F6FC", body="#C9D1D9", sub="#8B949E", line="#30363D"),
    "light": dict(fg="#1F2328", body="#31373D", sub="#59636E", line="#D1D9E0"),
}
ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = Path(__file__).resolve().parent / "fonts"
FONTS = {
    "serif_i": "playfair-display-latin-400-italic.woff",
    "mono": "jetbrains-mono-latin-400-normal.woff",
    "sans": "inter-latin-400-normal.woff",
}
_cache = {}

def _font(key):
    if key not in _cache:
        f = TTFont(FONT_DIR / FONTS[key])
        _cache[key] = (f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm)
    return _cache[key]

def width(key, s, px, track=0.0):
    gs, cmap, upm = _font(key)
    w = sum(gs[cmap.get(ord(c), cmap[ord("?")])].width + track * upm for c in s)
    return (w - track * upm) * px / upm

def text(key, s, px, x, y, fill, track=0.0):
    gs, cmap, upm = _font(key)
    scale, cx, parts = px / upm, 0, []
    for ch in s:
        g = cmap.get(ord(ch), cmap[ord("?")])
        pen = SVGPathPen(gs)
        gs[g].draw(pen)
        if pen.getCommands():
            parts.append((cx, pen.getCommands()))
        cx += gs[g].width + track * upm
    paths = "".join(
        f'<path transform="translate({x + p * scale:.2f} {y}) scale({scale:.5f} {-scale:.5f})" d="{d}"/>'
        for p, d in parts
    )
    return f'<g fill="{fill}">{paths}</g>'

def wrap(s, key, px, max_w):
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}".strip()
        if width(key, trial, px) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    return lines + [cur]

def build(t):
    W, PAD, BODY_PX, LEAD = 840, 48, 16, 28
    lines = wrap(ABOUT, "sans", BODY_PX, W - 2 * PAD - 30)
    body_top = 168
    H = body_top + (len(lines) - 1) * LEAD + 48
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{NAME}. {ABOUT}">',
         f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="none" stroke="{t["line"]}"/>',
         text("serif_i", NAME, 40, PAD, 84, t["fg"]),
         text("mono", SUBTITLE, 12, PAD + 2, 114, t["sub"], track=0.05)]
    for i, line in enumerate(lines):
        s.append(text("sans", line, BODY_PX, PAD, body_top + i * LEAD, t["body"]))
    s.append("</svg>")
    return "".join(s)

if __name__ == "__main__":
    for name, theme in THEMES.items():
        out = ROOT / "assets" / f"card-{name}.svg"
        out.write_text(build(theme))
        print("wrote", out.relative_to(ROOT))
