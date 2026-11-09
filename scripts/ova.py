"""Generate assets/ova.svg: the callout that points visitors at Ova.

Ova's own app icon carries the panel. It is the only warm, light object on an
otherwise dark profile, so it draws the eye without needing to shout. The letters
of the wordmark ripple gently, one after another, and then rest.
"""

import json

import theme as t
from text import outline, text_path

HEIGHT = 264

EYEBROW = "NOW BUILDING  /  TEAM PROJECT"
DESCRIPTION = (
    "A PCOS-focused cycle tracker that treats",
    "irregularity as the default, not the exception.",
)

# Replace with the domain once the site is live, and link the image in README.md.
SITE_LABEL = "SITE COMING SOON"

WORDMARK = t.ROOT / "scripts" / "data" / "ova_wordmark.json"

TILE_SIZE = 176
TILE_RADIUS = 40
TILE_X = t.PANEL_PADDING
TILE_Y = (HEIGHT - TILE_SIZE) / 2
COPY_X = TILE_X + TILE_SIZE + 48


def logo_tile() -> str:
    wordmark = json.loads(WORDMARK.read_text(encoding="utf-8"))
    scale = TILE_SIZE / wordmark["size"]
    letters = "".join(
        f'<path class="letter" style="animation-delay:{index * 0.22:.2f}s" fill-rule="evenodd" d="{d}"/>'
        for index, d in enumerate(wordmark["letters"])
    )
    return (
        f'<rect x="{TILE_X}" y="{TILE_Y}" width="{TILE_SIZE}" height="{TILE_SIZE}" '
        f'rx="{TILE_RADIUS}" fill="url(#tile)"/>'
        f'<g transform="translate({TILE_X} {TILE_Y}) scale({scale:.4f})" fill="{t.OVA_MAGENTA}">{letters}</g>'
    )


def status_pill(right: float, center_y: float) -> str:
    height = 42
    padding = 20
    size = 16
    tracking = 0.08
    label_width = outline(SITE_LABEL, x=0, y=0, size=size, family="mono", weight=500, tracking=tracking).width
    width = padding + 10 + 12 + label_width + padding
    x = right - width
    y = center_y - height / 2
    dot_x = x + padding + 4
    label = outline(
        SITE_LABEL, x=x + padding + 22, y=center_y + 5.6, size=size, family="mono", weight=500, tracking=tracking
    )
    return "".join(
        (
            f'<rect x="{x:.1f}" y="{y}" width="{width:.1f}" height="{height}" rx="{height / 2}" '
            f'fill="none" stroke="{t.ACCENT}" stroke-opacity="0.4"/>',
            f'<circle class="pulse" cx="{dot_x:.1f}" cy="{center_y}" r="4" fill="{t.ACCENT}"/>',
            f'<path fill="{t.ACCENT}" d="{label.d}"/>',
        )
    )


def copy_block() -> str:
    right = t.PANEL_WIDTH - t.PANEL_PADDING
    first = outline(DESCRIPTION[0], x=COPY_X, y=146, size=33, tracking=-0.01)
    second = outline(DESCRIPTION[1], x=COPY_X, y=190, size=33, tracking=-0.01)
    if COPY_X + max(first.width, second.width) > right:
        raise ValueError("The description overflows the panel.")
    return "".join(
        (
            text_path(EYEBROW, fill=t.TEXT_MUTED, x=COPY_X, y=87, size=19, family="mono", weight=500, tracking=0.08),
            status_pill(right, 80),
            f'<path fill="{t.TEXT}" d="{first.d}"/>',
            f'<path fill="{t.TEXT}" d="{second.d}"/>',
        )
    )


def build() -> str:
    width = t.PANEL_WIDTH
    glow_x = TILE_X + TILE_SIZE / 2
    glow_y = HEIGHT / 2
    label = f"Ova: {' '.join(DESCRIPTION)} {SITE_LABEL.capitalize()}."
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {HEIGHT}" width="{width}" height="{HEIGHT}" role="img" aria-label="{label}">
<title>{label}</title>
<style>
.letter{{animation:ripple 6s ease-in-out infinite}}
.glow{{animation:breathe 6s ease-in-out infinite alternate}}
.pulse{{animation:fade 2.4s ease-in-out infinite alternate}}
@keyframes ripple{{0%,50%,100%{{transform:translateY(0)}}18%{{transform:translateY(-16px)}}}}
@keyframes breathe{{to{{opacity:.55}}}}
@keyframes fade{{to{{opacity:.35}}}}
@media (prefers-reduced-motion:reduce){{.letter,.glow,.pulse{{animation:none}}}}
</style>
<defs>
<linearGradient id="tile" x1="0" y1="0.15" x2="1" y2="0"><stop stop-color="{t.OVA_TILE_START}"/><stop offset="1" stop-color="{t.OVA_TILE_END}"/></linearGradient>
<radialGradient id="glow"><stop stop-color="{t.ACCENT}" stop-opacity="0.18"/><stop offset="0.45" stop-color="{t.ACCENT}" stop-opacity="0.07"/><stop offset="1" stop-color="{t.ACCENT}" stop-opacity="0"/></radialGradient>
<clipPath id="panel"><rect width="{width}" height="{HEIGHT}" rx="{t.PANEL_RADIUS}"/></clipPath>
</defs>
<g clip-path="url(#panel)">
<rect width="{width}" height="{HEIGHT}" fill="{t.BACKGROUND}"/>
<circle class="glow" cx="{glow_x}" cy="{glow_y}" r="300" fill="url(#glow)"/>
{logo_tile()}
{copy_block()}
</g>
<rect x="0.5" y="0.5" width="{width - 1}" height="{HEIGHT - 1}" rx="{t.PANEL_RADIUS}" fill="none" stroke="{t.BORDER}"/>
</svg>
"""


def main() -> None:
    t.ASSETS.mkdir(exist_ok=True)
    path = t.ASSETS / "ova.svg"
    path.write_text(build(), encoding="utf-8", newline="\n")
    print(f"wrote {path} ({path.stat().st_size / 1024:.1f} KiB)")


if __name__ == "__main__":
    main()
