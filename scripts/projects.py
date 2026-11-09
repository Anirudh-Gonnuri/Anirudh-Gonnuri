"""Generate assets/projects/*.svg: one card per featured project.

Each card wears its own project's colours, taken from that project's code or logo,
so the grid reads as six different things rather than one template.

Each card is its own image because a README can only link a whole image. Cards sit
two to a row at 50% width with no whitespace between them, so the gutter is drawn
as transparent margin inside the SVG. That keeps the outer edges of the grid flush
with the full-width panels above and below it.
"""

from collections.abc import Callable
from dataclasses import dataclass

import theme as t
from ova import wordmark
from panel import arrow, write_asset
from text import outline, text_path

CARD_WIDTH = 628
CARD_HEIGHT = 344
GUTTER = 12
ROW_GAP = 14
CANVAS_WIDTH = CARD_WIDTH + GUTTER
CANVAS_HEIGHT = CARD_HEIGHT + ROW_GAP

PADDING = 40
ICON_CENTER_Y = 66
ICON_SIZE = 52
TITLE_Y = 150
BODY_Y = 196
BODY_LINE_HEIGHT = 36
STACK_Y = CARD_HEIGHT - 34


@dataclass(frozen=True)
class Palette:
    title: str
    body: str
    faint: str
    accent: str
    ground_start: str
    ground_end: str
    glow: str | None
    border: str | None


OVA = Palette(
    t.OVA_INK, t.OVA_INK, t.OVA_INK_MUTED, t.OVA_MAGENTA,
    t.OVA_TILE_START, t.OVA_TILE_END, None, None,
)
CORTEX_BLUE = "#4c82f5"
CORTEX_GOLD = "#d4b366"
CORTEX = Palette(t.TEXT, "#c3cce2", CORTEX_GOLD, CORTEX_BLUE, "#1a2346", "#0b1121", "#135bec", "#2c3a6b")
GO_CYAN = "#00add8"
STREAM = Palette(t.TEXT, "#b5d3dc", "#6cc9e0", GO_CYAN, "#0d3340", "#08161b", GO_CYAN, "#1a4a59")
NURDLE_GREEN = "#57a654"
NURDLE_GOLD = "#f9b72f"
NURDLE_GREY = "#98989b"
NURDLE = Palette(t.TEXT, "#bdbfbd", NURDLE_GREY, NURDLE_GREEN, "#181a18", "#0a0a0a", NURDLE_GREEN, "#2b2e2b")
AMPED_AMBER = "#f5b52a"
AMPED_CYAN = "#34b1e6"
AMPED_NAVY = "#252238"
AMPED = Palette(t.TEXT, "#c9c5da", AMPED_CYAN, AMPED_AMBER, "#332e4f", "#191729", AMPED_AMBER, "#433d63")
ORCHID = "#e8a4ec"
MONITOR = Palette(t.TEXT, "#d0bfd3", "#c29ac7", ORCHID, "#34203a", "#180f1c", "#b15fc0", "#4b3052")

Glyph = Callable[[], str]


def _cortex_bars() -> str:
    return (
        f'<g fill="none" stroke="{CORTEX_BLUE}" stroke-width="2.5">'
        '<rect x="2" y="32" width="11" height="18" rx="2.5"/>'
        '<rect x="20" y="18" width="11" height="32" rx="2.5"/></g>'
        f'<rect x="38" y="2" width="12" height="49" rx="3" fill="{CORTEX_GOLD}"/>'
    )


def _streams() -> str:
    return (
        f'<path d="M1 11H51M1 26H51M1 41H51" stroke="{GO_CYAN}" stroke-width="2.5" stroke-linecap="round"/>'
        f'<g fill="{t.TEXT}"><circle cx="36" cy="11" r="5.5"/><circle cx="15" cy="26" r="5.5"/>'
        '<circle cx="42" cy="41" r="5.5"/></g>'
    )


def _nurdle_logo() -> str:
    # Redrawn from the geometry of Nurdle's 1052px logo: an N under three result dots.
    left, top, height = 190, 50, 959
    scale = ICON_SIZE / height
    dots = "".join(
        f'<circle cx="{cx}" cy="140" r="90" fill="{colour}"/>'
        for cx, colour in ((272, NURDLE_GREEN), (527, NURDLE_GOLD), (782, NURDLE_GREY))
    )
    letter = (
        '<polygon fill="#fff" points="190,292 342,292 697,738 697,292 864,292 '
        '864,1009 714,1009 357,561 357,1009 190,1009"/>'
    )
    return f'<g transform="scale({scale:.5f}) translate({-left} {-top})">{dots}{letter}</g>'


def _multimeter() -> str:
    # A small nod to the character in Amped Adventures' icon.
    return (
        f'<path d="M10 14H3V7M42 26H49V40" fill="none" stroke="{AMPED_CYAN}" stroke-width="2.5" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
        f'<rect x="10" y="3" width="32" height="46" rx="7" fill="{AMPED_AMBER}"/>'
        f'<rect x="15" y="8" width="22" height="14" rx="2.5" fill="{AMPED_NAVY}"/>'
        f'<path d="M19 12.5L23 14.5M33 12.5L29 14.5M22 18Q26 20.5 30 18" fill="none" stroke="{AMPED_AMBER}" '
        'stroke-width="1.8" stroke-linecap="round"/>'
        f'<circle cx="21" cy="35" r="7" fill="#d98a14" stroke="{AMPED_NAVY}" stroke-width="2"/>'
        f'<circle cx="35" cy="30" r="3" fill="#e5483a"/><circle cx="35" cy="40" r="3" fill="{AMPED_NAVY}"/>'
    )


def _pulse() -> str:
    return (
        f'<path d="M1 28H14L21 8L31 46L37 28H51" fill="none" stroke="{ORCHID}" stroke-width="2.5" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
    )


@dataclass(frozen=True)
class Project:
    slug: str
    title: str
    description: tuple[str, str] | tuple[str, str, str]
    stack: tuple[str, ...]
    palette: Palette
    glyph: Glyph | None = None
    url: str | None = None
    badge: str = "PRIVATE"


def _repo(name: str) -> str:
    return f"https://github.com/Anirudh-Gonnuri/{name}"


PROJECTS = (
    Project(
        "ova",
        "Ova",
        ("Cycle tracking built for PCOS, treating", "irregular cycles as the norm, with ML", "predictions behind it."),
        ("FLUTTER", "FASTAPI", "SUPABASE"),
        OVA,
        badge="TEAM PROJECT",
    ),
    Project(
        "cortexedu",
        "CortexEdu",
        ("Tracks classroom participation in real time,", "analyses performance patterns and", "automates attendance marking."),
        ("FLUTTER", "NODE.JS", "FIREBASE"),
        CORTEX,
        glyph=_cortex_bars,
        badge="TEAM PROJECT",
    ),
    Project(
        "streamflow",
        "StreamFlow",
        ("A Kafka-inspired streaming system in Go,", "built around concurrency and real-time", "data processing."),
        ("GO", "CONCURRENCY", "STREAMING"),
        STREAM,
        glyph=_streams,
        url=_repo("StreamFlow"),
        badge="VIEW CODE",
    ),
    Project(
        "nurdle",
        "Nurdle",
        ("A daily number-guessing game: crack the", "3-digit code in 6 tries, or battle friends", "in real-time multiplayer."),
        ("JAVASCRIPT", "FIREBASE"),
        NURDLE,
        glyph=_nurdle_logo,
        url=_repo("Nurdle"),
        badge="VIEW CODE",
    ),
    Project(
        "amped-adventures",
        "Amped Adventures",
        ("A 2D puzzle-platformer built on electronics", "puzzles and signal-driven interactions."),
        ("GODOT 4", "GDSCRIPT"),
        AMPED,
        glyph=_multimeter,
        url=_repo("Amped-Adventures"),
        badge="VIEW CODE",
    ),
    Project(
        "ova-monitor",
        "Ova Monitor",
        ("Watches Ova's ML models in production:", "live accuracy against baseline, with alerts", "for drift and outages."),
        ("SPRING BOOT", "ANGULAR", "POSTGRESQL"),
        MONITOR,
        glyph=_pulse,
    ),
)


def badge(project: Project) -> str:
    colours = project.palette
    right = CARD_WIDTH - PADDING
    size = 16
    if project.url:
        arrow_x = right - 14
        label = outline(
            project.badge, x=arrow_x - 12, y=ICON_CENTER_Y + 5.6, size=size,
            family="mono", weight=500, tracking=0.08, anchor="end",
        )
        return f'<path fill="{colours.accent}" d="{label.d}"/>' + arrow(arrow_x, ICON_CENTER_Y - 7, colours.accent, 14)

    height = 36
    padding = 16
    width = outline(project.badge, x=0, y=0, size=size, family="mono", weight=500, tracking=0.08).width
    x = right - width - 2 * padding
    return (
        f'<rect x="{x:.1f}" y="{ICON_CENTER_Y - height / 2}" width="{width + 2 * padding:.1f}" height="{height}" '
        f'rx="{height / 2}" fill="none" stroke="{colours.faint}" stroke-opacity="0.6"/>'
        + text_path(
            project.badge, fill=colours.faint, x=x + padding, y=ICON_CENTER_Y + 5.6, size=size,
            family="mono", weight=500, tracking=0.08,
        )
    )


def icon(project: Project) -> str:
    if project.glyph is None:
        return wordmark(left=PADDING, center_y=ICON_CENTER_Y, width=104)
    return f'<g transform="translate({PADDING} {ICON_CENTER_Y - ICON_SIZE / 2})">{project.glyph()}</g>'


def description(project: Project) -> str:
    limit = CARD_WIDTH - 2 * PADDING
    parts: list[str] = []
    for index, line in enumerate(project.description):
        shaped = outline(line, x=PADDING, y=BODY_Y + index * BODY_LINE_HEIGHT, size=25)
        if shaped.width > limit:
            raise ValueError(f"{project.slug}: description line overflows: {line!r}")
        parts.append(f'<path fill="{project.palette.body}" d="{shaped.d}"/>')
    return "".join(parts)


def card_defs(colours: Palette) -> str:
    defs = (
        '<linearGradient id="ground" x1="0" y1="0" x2="1" y2="1">'
        f'<stop stop-color="{colours.ground_start}"/><stop offset="1" stop-color="{colours.ground_end}"/></linearGradient>'
        f'<clipPath id="card"><rect width="{CARD_WIDTH}" height="{CARD_HEIGHT}" rx="{t.PANEL_RADIUS}"/></clipPath>'
    )
    if colours.glow:
        defs += (
            f'<radialGradient id="glow"><stop stop-color="{colours.glow}" stop-opacity="0.34"/>'
            f'<stop offset="0.5" stop-color="{colours.glow}" stop-opacity="0.12"/>'
            f'<stop offset="1" stop-color="{colours.glow}" stop-opacity="0"/></radialGradient>'
        )
    return defs


def card_ground(colours: Palette) -> str:
    layers = [f'<rect width="{CARD_WIDTH}" height="{CARD_HEIGHT}" fill="url(#ground)"/>']
    if colours.glow:
        layers.append(f'<circle cx="{CARD_WIDTH - 40}" cy="30" r="340" fill="url(#glow)"/>')
    ground = f'<g clip-path="url(#card)">{"".join(layers)}</g>'
    if colours.border:
        ground += (
            f'<rect x="0.5" y="0.5" width="{CARD_WIDTH - 1}" height="{CARD_HEIGHT - 1}" rx="{t.PANEL_RADIUS}" '
            f'fill="none" stroke="{colours.border}"/>'
        )
    return ground


def build(project: Project, offset: int) -> str:
    colours = project.palette
    title = text_path(project.title, fill=colours.title, x=PADDING, y=TITLE_Y, size=42, weight=600, tracking=-0.02)
    stack = text_path(
        "  /  ".join(project.stack), fill=colours.faint, x=PADDING, y=STACK_Y, size=18,
        family="mono", weight=500, tracking=0.06,
    )
    label = f"{project.title}: {' '.join(project.description)} Built with {', '.join(project.stack)}."
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS_WIDTH} {CANVAS_HEIGHT}" width="{CANVAS_WIDTH}" height="{CANVAS_HEIGHT}" role="img" aria-label="{label}">
<title>{label}</title>
<defs>{card_defs(colours)}</defs>
<g transform="translate({offset} 0)">
{card_ground(colours)}
{icon(project)}
{badge(project)}
{title}
{description(project)}
{stack}
</g>
</svg>
"""


def main() -> None:
    for index, project in enumerate(PROJECTS):
        # Left-column cards keep their margin on the right, and the reverse.
        offset = 0 if index % 2 == 0 else GUTTER
        write_asset(f"projects/{project.slug}.svg", build(project, offset))


if __name__ == "__main__":
    main()
