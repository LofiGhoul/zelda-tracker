"""Zelda-inspired look: dark forest and gold, parchment text, serif headings, and a
colour scheme per game. Original styling only; no game artwork or logos."""

from __future__ import annotations

import math

# per game: (background top, background bottom, card, accent)
PALETTES = {
    "default": ("#14251c", "#0b140f", "#1a2d22", "#7fbf6a"),   # Hyrule forest
    "oot3d":   ("#14251c", "#0b140f", "#1a2d22", "#7fbf6a"),   # Kokiri green
    "mm3d":    ("#1d1530", "#0e0a18", "#251c3a", "#b48ae8"),   # Termina moon
    "ladx":    ("#10262a", "#081416", "#15313a", "#6cc8c0"),   # Koholint sea
    "oos":     ("#2a1a10", "#150d07", "#33210f", "#e3994a"),   # autumn Holodrum
    "ooa":     ("#121c30", "#090e19", "#18243c", "#86a9f0"),   # Labrynna time
    "tmc":     ("#1a2614", "#0d140a", "#22321a", "#b8d35a"),   # Minish cap
    "albw":    ("#2a1418", "#150a0c", "#341a1f", "#e57a86"),   # Lorule
    "alttp":   ("#141a30", "#0a0d19", "#1b2340", "#e3604f"),   # Hyrule Castle
    "tp":      ("#1e1c14", "#0e0d09", "#28251a", "#5fd0c0"),   # twilight
}

GOLD = "#d9b45e"
GOLD_LIGHT = "#f2d98e"
PARCHMENT = "#efe5cb"
PARCHMENT_DIM = "#b9ad8f"
HEART_RED = (0.88, 0.26, 0.24)

SERIF = '"Cinzel", "Cormorant Garamond", "Noto Serif", "DejaVu Serif", serif'

BASE_CSS = f"""
window.zelda {{
  --window-bg-color: var(--z-bg-bottom);
  --view-bg-color: var(--z-bg-bottom);
  --headerbar-bg-color: var(--z-bg-top);
  --headerbar-fg-color: {PARCHMENT};
  --card-bg-color: var(--z-card);
  --card-fg-color: {PARCHMENT};
  --window-fg-color: {PARCHMENT};
  --view-fg-color: {PARCHMENT};
  --accent-bg-color: {GOLD};
  --accent-fg-color: #1a1408;
  --accent-color: {GOLD_LIGHT};
  --popover-bg-color: var(--z-card);
  --dialog-bg-color: var(--z-card);
  background-image: radial-gradient(ellipse at top, var(--z-bg-top), var(--z-bg-bottom) 75%);
  color: {PARCHMENT};
}}
window.zelda headerbar {{
  background: linear-gradient(to bottom, var(--z-bg-top), shade(var(--z-bg-top), 0.8));
  border-bottom: 1px solid alpha({GOLD}, .45);
  box-shadow: 0 1px 0 alpha(black, .5);
}}
window.zelda headerbar .title {{
  font-family: {SERIF}; font-weight: 700; letter-spacing: 1px; color: {GOLD_LIGHT};
}}
window.zelda headerbar .subtitle {{ color: {PARCHMENT_DIM}; }}
window.zelda scrolledwindow, window.zelda viewport, window.zelda stack {{ background: transparent; }}

/* gold-framed cards and lists */
window.zelda .card, window.zelda list.boxed-list {{
  background-color: alpha(var(--z-card), .92);
  border: 1px solid alpha({GOLD}, .38);
  border-radius: 10px;
  box-shadow: inset 0 0 0 1px alpha(black, .35), 0 3px 10px alpha(black, .35);
}}
window.zelda list.boxed-list > row {{ background: transparent; }}
window.zelda list.boxed-list > row:not(:last-child) {{ border-bottom: 1px solid alpha({GOLD}, .14); }}
window.zelda list.boxed-list > row:hover {{ background: alpha({GOLD}, .06); }}
window.zelda row .title {{ color: {PARCHMENT}; }}
window.zelda row .subtitle {{ color: {PARCHMENT_DIM}; }}
window.zelda row.got-row .title {{ color: alpha({PARCHMENT}, .55); text-decoration-line: line-through; text-decoration-color: alpha({GOLD}, .45); }}

/* section titles: serif gold with a little ornament */
window.zelda preferencesgroup label.heading, window.zelda .z-heading {{
  font-family: {SERIF}; font-size: 15px; font-weight: 700; letter-spacing: .8px; color: {GOLD_LIGHT};
}}
window.zelda .z-display {{ font-family: {SERIF}; }}

/* summary plaque */
.z-plaque {{
  background-image: linear-gradient(to bottom, alpha(var(--z-accent), .10), alpha(var(--z-card), .95) 60%);
}}
.hero-count {{ font-family: {SERIF}; font-size: 52px; font-weight: 800; color: {GOLD_LIGHT};
               text-shadow: 0 2px 0 alpha(black, .6); font-feature-settings: "tnum"; }}
.hero-total {{ font-family: {SERIF}; font-size: 22px; font-weight: 700; color: {GOLD}; }}
.z-game-title {{ font-family: {SERIF}; font-size: 20px; font-weight: 700; color: {PARCHMENT}; letter-spacing: .6px; }}
.z-kicker {{ font-size: 11px; font-weight: 700; letter-spacing: 2px; color: var(--z-accent); }}
.dim-label {{ color: {PARCHMENT_DIM}; opacity: 1; }}

/* medallion icons for sections */
.cat-icon {{ border-radius: 999px; min-width: 38px; min-height: 38px;
            background: radial-gradient(circle, alpha(var(--z-accent), .35), alpha(var(--z-accent), .12));
            color: var(--z-accent); border: 2px solid alpha({GOLD}, .7);
            box-shadow: inset 0 0 0 1px alpha(black, .5); }}
.cat-icon.done {{ background: radial-gradient(circle, {GOLD_LIGHT}, {GOLD}); color: #2a1e08;
                  border-color: {GOLD_LIGHT}; }}

/* row status: gold seal when done, empty socket when missing */
.piece-icon {{ border-radius: 999px; min-width: 30px; min-height: 30px; }}
.piece-icon.got {{ background: radial-gradient(circle, {GOLD_LIGHT}, {GOLD}); color: #2a1e08;
                   box-shadow: 0 0 6px alpha({GOLD}, .5); }}
.piece-icon.maybe {{ background: alpha(#e0a040, .25); color: #f0c060; border: 1px dashed alpha(#f0c060, .7); }}
.piece-icon.missing {{ background: alpha(black, .35); color: alpha({GOLD}, .45); border: 1px solid alpha({GOLD}, .35); }}
image.not-owned {{ opacity: .25; filter: grayscale(1); }}

.region-chip {{ border-radius: 999px; padding: 2px 10px; font-size: 12px; font-weight: 700;
               color: {GOLD_LIGHT}; border: 1px solid alpha({GOLD}, .5); background: alpha(black, .25); }}
.region-chip.done {{ background: {GOLD}; color: #2a1e08; border-color: {GOLD_LIGHT}; }}
.step-num {{ border-radius: 999px; min-width: 22px; min-height: 22px; font-size: 12px; font-weight: 800;
            background: alpha({GOLD}, .2); color: {GOLD_LIGHT}; border: 1px solid alpha({GOLD}, .55); }}

/* gold progress bars, green when complete */
progressbar trough {{ background: alpha(black, .45); border: 1px solid alpha({GOLD}, .25); }}
progressbar progress {{ background-image: linear-gradient(to right, shade({GOLD}, .8), {GOLD_LIGHT}); border: none; }}
progressbar.thin trough, progressbar.thin progress {{ min-height: 6px; border-radius: 99px; }}
progressbar.big trough, progressbar.big progress {{ min-height: 12px; border-radius: 99px; }}
progressbar.done progress {{ background-image: linear-gradient(to right, shade(var(--z-accent), .8), var(--z-accent)); }}

/* slot tabs and filters */
window.zelda togglegroup {{ background: alpha(black, .35); border: 1px solid alpha({GOLD}, .3); }}
window.zelda togglegroup toggle:checked {{ background: {GOLD}; color: #1a1408; }}
window.zelda togglegroup toggle {{ color: {PARCHMENT}; font-weight: 700; }}
window.zelda button.suggested-action {{ background: linear-gradient(to bottom, {GOLD_LIGHT}, {GOLD}); color: #1a1408;
                                        border: 1px solid shade({GOLD}, .7); font-family: {SERIF}; font-weight: 700; }}
window.zelda button.suggested-action label {{ color: #1a1408; }}
window.zelda statuspage .title {{ font-family: {SERIF}; color: {GOLD_LIGHT}; }}
window.zelda toast {{ background: var(--z-card); color: {PARCHMENT}; border: 1px solid alpha({GOLD}, .5); }}
.z-game-list label {{ color: {PARCHMENT_DIM}; }}
.z-game-list .z-game-name {{ font-family: {SERIF}; color: {PARCHMENT}; font-weight: 700; }}
.z-swatch {{ border-radius: 999px; min-width: 10px; min-height: 10px; }}
.z-badge {{ border-radius: 8px; min-width: 50px; min-height: 30px; padding: 0 4px;
           border: 1px solid alpha({GOLD}, .6); box-shadow: inset 0 0 0 1px alpha(black, .4); }}
.z-badge label {{ font-family: {SERIF}; font-size: 11px; font-weight: 800; color: #14100a; }}
window.zelda button.z-secondary {{ background: alpha(black, .3); color: {GOLD_LIGHT};
                                   border: 1px solid alpha({GOLD}, .6); font-family: {SERIF}; font-weight: 700; }}
window.zelda button.z-secondary:hover {{ background: alpha({GOLD}, .15); }}
"""


def palette_css() -> str:
    out = []
    for gid, (top, bottom, card, accent) in PALETTES.items():
        sel = "window.zelda" if gid == "default" else f"window.zelda.game-{gid}"
        out.append(f"{sel} {{ --z-bg-top: {top}; --z-bg-bottom: {bottom}; --z-card: {card}; --z-accent: {accent}; }}")
        out.append(f".z-swatch.game-{gid} {{ background: {accent}; }}")
        out.append(f".z-badge.game-{gid} {{ background: linear-gradient(to bottom, shade({accent}, 1.15), shade({accent}, .8)); }}")
    return "\n".join(out)


def css(extra: str = "") -> str:
    return palette_css() + "\n" + BASE_CSS + "\n" + extra


def hex_rgb(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def draw_ornament(cr, w: float, h: float, accent: str = GOLD) -> None:
    """A thin gold rule with a diamond in the middle and small diamonds at the ends."""
    r, g, b = hex_rgb(GOLD)
    mid, y = w / 2, h / 2
    cr.set_line_width(1)
    for x0, x1 in ((8, mid - 14), (mid + 14, w - 8)):
        grad_alpha = 0.7
        cr.set_source_rgba(r, g, b, grad_alpha)
        cr.move_to(x0, y + .5)
        cr.line_to(x1, y + .5)
        cr.stroke()

    def diamond(cx, s, fill):
        cr.move_to(cx, y - s)
        cr.line_to(cx + s, y)
        cr.line_to(cx, y + s)
        cr.line_to(cx - s, y)
        cr.close_path()
        if fill:
            ar, ag, ab = hex_rgb(accent)
            cr.set_source_rgb(ar, ag, ab)
            cr.fill_preserve()
        cr.set_source_rgb(r, g, b)
        cr.stroke()

    diamond(mid, 6, True)
    diamond(8, 3, False)
    diamond(w - 8, 3, False)


def draw_gem(cr, x: float, y: float, w: float, h: float, color: str) -> None:
    """An elongated hexagonal gem (a generic jewel shape) with a light facet."""
    r, g, b = hex_rgb(color)
    pts = [(x + w / 2, y), (x + w, y + h * .25), (x + w, y + h * .75), (x + w / 2, y + h),
           (x, y + h * .75), (x, y + h * .25)]
    cr.move_to(*pts[0])
    for p in pts[1:]:
        cr.line_to(*p)
    cr.close_path()
    cr.set_source_rgb(r, g, b)
    cr.fill_preserve()
    cr.set_source_rgba(0, 0, 0, .5)
    cr.set_line_width(1)
    cr.stroke()
    cr.move_to(x + w / 2, y + h * .12)
    cr.line_to(x + w * .82, y + h * .3)
    cr.line_to(x + w / 2, y + h * .45)
    cr.line_to(x + w * .18, y + h * .3)
    cr.close_path()
    cr.set_source_rgba(1, 1, 1, .35)
    cr.fill()


def heart_path(cr, x, y, s):
    cr.move_to(x + s / 2, y + s * 0.92)
    cr.curve_to(x - s * 0.05, y + s * 0.5, x + s * 0.02, y + s * 0.02, x + s * 0.27, y + s * 0.06)
    cr.curve_to(x + s * 0.4, y + s * 0.08, x + s * 0.48, y + s * 0.18, x + s / 2, y + s * 0.26)
    cr.curve_to(x + s * 0.52, y + s * 0.18, x + s * 0.6, y + s * 0.08, x + s * 0.73, y + s * 0.06)
    cr.curve_to(x + s * 0.98, y + s * 0.02, x + s * 1.05, y + s * 0.5, x + s / 2, y + s * 0.92)
    cr.close_path()


def draw_heart(cr, x, y, s, fill: float) -> None:
    """A heart container: dark socket, red fill clockwise by `fill`, gold rim, shine."""
    heart_path(cr, x, y, s)
    cr.set_source_rgba(0.12, 0.04, 0.04, 0.85)
    cr.fill()
    if fill > 0:
        cr.save()
        heart_path(cr, x, y, s)
        cr.clip()
        cr.move_to(x + s / 2, y + s / 2)
        cr.arc(x + s / 2, y + s / 2, s, -math.pi / 2, -math.pi / 2 + 2 * math.pi * fill)
        cr.close_path()
        cr.set_source_rgb(*HEART_RED)
        cr.fill()
        cr.restore()
        cr.save()
        heart_path(cr, x, y, s)
        cr.clip()
        cr.arc(x + s * .32, y + s * .28, s * .12, 0, 2 * math.pi)
        cr.set_source_rgba(1, 1, 1, .45 if fill >= 1 else .25)
        cr.fill()
        cr.restore()
    heart_path(cr, x, y, s)
    gr, gg, gb = hex_rgb(GOLD)
    cr.set_source_rgba(gr, gg, gb, .9)
    cr.set_line_width(1.3)
    cr.stroke()
