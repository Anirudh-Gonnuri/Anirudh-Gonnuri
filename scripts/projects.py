"""Generate assets/projects/*.svg: one card per featured project.

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
TITLE_Y = 150
BODY_Y = 196
BODY_LINE_HEIGHT = 36
STACK_Y = CARD_HEIGHT - 34

Glyph = Callable[[str], str]


def _bars(colour: str) -> str:
    return (
        f'<g fill="none" stroke="{colour}" stroke-width="2.5">'
        '<rect x="2" y="32" width="11" height="18" rx="2.5"/>'
        '<rect x="20" y="18" width="11" height="32" rx="2.5"/></g>'
        f'<rect x="38" y="2" width="12" height="49" rx="3" fill="{colour}"/>'
    )


def _streams(colour: str) -> str:
    return (
        f'<path d="M1 11H51M1 26H51M1 41H51" stroke="{colour}" stroke-width="2.5" stroke-linecap="round"/>'
        f'<g fill="{colour}"><circle cx="36" cy="11" r="5.5"/><circle cx="15" cy="26" r="5.5"/>'
        '<circle cx="42" cy="41" r="5.5"/></g>'
    )


def _digits(colour: str) -> str:
    return (
        f'<g fill="none" stroke="{colour}" stroke-width="2.5">'
        '<rect x="2" y="16" width="13" height="20" rx="3"/>'
        '<rect x="37" y="16" width="13" height="20" rx="3"/></g>'
        f'<rect x="18.25" y="14.75" width="15.5" height="22.5" rx="4" fill="{colour}"/>'
    )


def _signal(colour: str) -> str:
    return (
        f'<path d="M1 40H11V12H25V40H39V12H51" fill="none" stroke="{colour}" stroke-width="2.5" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
    )


def _pulse(colour: str) -> str:
    return (
        f'<path d="M1 28H14L21 8L31 46L37 28H51" fill="none" stroke="{colour}" stroke-width="2.5" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
    )


@dataclass(frozen=True)
class Palette:
    title: str
    body: str
    faint: str
    accent: str


DARK = Palette(t.TEXT, t.TEXT_MUTED, t.TEXT_FAINT, t.ACCENT)
OVA = Palette(t.OVA_INK, t.OVA_INK, t.OVA_INK_MUTED, t.OVA_MAGENTA)


@dataclass(frozen=True)
class Project:
    slug: str
    title: str
    description: tuple[str, str] | tuple[str, str, str]
    stack: tuple[str, ...]
    glyph: Glyph | None = None
    url: str | None = None
    badge: str = "PRIVATE"
    palette: Palette = DARK


def _repo(name: str) -> str:
    return f"https://github.com/Anirudh-Gonnuri/{name}"


PROJECTS = (
    Project(
        "ova",
        "Ova",
        ("Cycle tracking built for PCOS, treating", "irregular cycles as the norm, with ML", "predictions behind it."),
        ("FLUTTER", "FASTAPI", "SUPABASE"),
        badge="TEAM PROJECT",
        palette=OVA,
    ),
    Project(
        "cortexedu",
        "CortexEdu",
        ("Tracks classroom participation in real time,", "analyses performance patterns and", "automates attendance marking."),
        ("FLUTTER", "NODE.JS", "FIREBASE"),
        glyph=_bars,
        badge="TEAM PROJECT",
    ),
    Project(
        "streamflow",
        "StreamFlow",
        ("A Kafka-inspired streaming system in Go,", "built around concurrency and real-time", "data processing."),
        ("GO", "CONCURRENCY", "STREAMING"),
        glyph=_streams,
        url=_repo("StreamFlow"),
        badge="VIEW CODE",
    ),
    Project(
        "nurdle",
        "Nurdle",
        ("A daily number-guessing game: crack the", "3-digit code in 6 tries, or battle friends", "in real-time multiplayer."),
        ("JAVASCRIPT", "FIREBASE"),
        glyph=_digits,
        url=_repo("Nurdle"),
        badge="VIEW CODE",
    ),
    Project(
        "amped-adventures",
        "Amped Adventures",
        ("A 2D puzzle-platformer built on electronics", "puzzles and signal-driven interactions."),
        ("GODOT 4", "GDSCRIPT"),
        glyph=_signal,
        url=_repo("Amped-Adventures"),
        badge="VIEW CODE",
    ),
    Project(
        "ova-monitor",
        "Ova Monitor",
        ("Watches Ova's ML models in production:", "live accuracy against baseline, with alerts", "for drift and outages."),
        ("SPRING BOOT", "ANGULAR", "POSTGRESQL"),
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
        f'rx="{height / 2}" fill="none" stroke="{colours.faint}" stroke-opacity="0.55"/>'
        + text_path(
            project.badge, fill=colours.faint, x=x + padding, y=ICON_CENTER_Y + 5.6, size=size,
            family="mono", weight=500, tracking=0.08,
        )
    )


def icon(project: Project) -> str:
    if project.glyph is None:
        return wordmark(left=PADDING, center_y=ICON_CENTER_Y, width=104)
    return f'<g transform="translate({PADDING} {ICON_CENTER_Y - 26})">{project.glyph(project.palette.accent)}</g>'


def description(project: Project) -> str:
    limit = CARD_WIDTH - 2 * PADDING
    parts: list[str] = []
    for index, line in enumerate(project.description):
        shaped = outline(line, x=PADDING, y=BODY_Y + index * BODY_LINE_HEIGHT, size=25)
        if shaped.width > limit:
            raise ValueError(f"{project.slug}: description line overflows: {line!r}")
        parts.append(f'<path fill="{project.palette.body}" d="{shaped.d}"/>')
    return "".join(parts)


def card_ground(project: Project) -> tuple[str, str]:
    """Return the ``<defs>`` content and the card's background rectangle."""
    geometry = f'width="{CARD_WIDTH}" height="{CARD_HEIGHT}" rx="{t.PANEL_RADIUS}"'
    if project.palette is OVA:
        defs = (
            '<linearGradient id="ground" x1="0" y1="0.15" x2="1" y2="0">'
            f'<stop stop-color="{t.OVA_TILE_START}"/><stop offset="1" stop-color="{t.OVA_TILE_END}"/></linearGradient>'
        )
        return defs, f'<rect {geometry} fill="url(#ground)"/>'
    return (
        "",
        f'<rect x="0.5" y="0.5" width="{CARD_WIDTH - 1}" height="{CARD_HEIGHT - 1}" rx="{t.PANEL_RADIUS}" '
        f'fill="{t.BACKGROUND}" stroke="{t.BORDER}"/>',
    )


def build(project: Project, offset: int) -> str:
    colours = project.palette
    defs, ground = card_ground(project)
    title = text_path(project.title, fill=colours.title, x=PADDING, y=TITLE_Y, size=42, weight=600, tracking=-0.02)
    stack = text_path(
        "  /  ".join(project.stack), fill=colours.faint, x=PADDING, y=STACK_Y, size=18,
        family="mono", weight=500, tracking=0.06,
    )
    label = f"{project.title}: {' '.join(project.description)} Built with {', '.join(project.stack)}."
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS_WIDTH} {CANVAS_HEIGHT}" width="{CANVAS_WIDTH}" height="{CANVAS_HEIGHT}" role="img" aria-label="{label}">
<title>{label}</title>
<defs>{defs}</defs>
<g transform="translate({offset} 0)">
{ground}
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
