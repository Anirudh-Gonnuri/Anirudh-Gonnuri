"""Generate assets/hero.svg: the profile banner.

The artwork is a small isometric structure with one lit block hovering over the
empty slot it belongs in: a profile that is always mid-build.
"""

from math import cos, radians, sin

import theme as t
from text import outline, text_path

HEIGHT = 420

NAME = "Anirudh Gonnuri"
EYEBROW = "GENERAL BUILDER  /  BENGALURU"
TAGLINE = ("I build whatever the problem needs:", "apps, backends, games and automations.")

# Column heights, back to front. Rows run along +x and columns along +y.
HEIGHTS = (
    (3, 4, 2, 3, 1),
    (4, 2, 3, 1, 2),
    (2, 3, 1, 1, 1),
    (3, 1, 1, 1, 1),
    (1, 2, 1, 1, 1),
)
SLOT = (2, 2)
# A few blocks carry the colours of the projects below.
TINTED_TOPS = {
    (0, 3): "#00add8",
    (3, 0): "#f9b72f",
    (1, 0): "#c77dd1",
    (4, 1): "#57a654",
}
HOVER_Z = 3.1

UNIT = 38
ORIGIN_X = 985
ORIGIN_Y = 180
COS_30 = cos(radians(30))
SIN_30 = sin(radians(30))

Point3 = tuple[float, float, float]


def project(x: float, y: float, z: float) -> tuple[float, float]:
    return (
        ORIGIN_X + (x - y) * COS_30 * UNIT,
        ORIGIN_Y + (x + y) * SIN_30 * UNIT - z * UNIT,
    )


def points(corners: list[Point3]) -> str:
    return " ".join(f"{sx:.1f},{sy:.1f}" for sx, sy in (project(*c) for c in corners))


def polygon(corners: list[Point3], fill: str, stroke: str, width: float = 1.2) -> str:
    return (
        f'<polygon points="{points(corners)}" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="{width}" stroke-linejoin="round"/>'
    )


def seam(start: Point3, end: Point3) -> str:
    (x1, y1), (x2, y2) = project(*start), project(*end)
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{t.FACE_SEAM}" stroke-width="1"/>'
    )


def cuboid(x: int, y: int, z0: float, z1: float, top: str, left: str, right: str, edge: str) -> str:
    """Draw the three camera-facing sides of a cuboid on one grid cell."""
    x1, y1 = x + 1, y + 1
    return "".join(
        (
            polygon([(x, y1, z0), (x1, y1, z0), (x1, y1, z1), (x, y1, z1)], left, edge),
            polygon([(x1, y, z0), (x1, y1, z0), (x1, y1, z1), (x1, y, z1)], right, edge),
            polygon([(x, y, z1), (x1, y, z1), (x1, y1, z1), (x, y1, z1)], top, edge),
        )
    )


def column(x: int, y: int, height: int) -> str:
    top = TINTED_TOPS.get((x, y), t.FACE_TOP)
    parts = [cuboid(x, y, 0, height, top, t.FACE_LEFT, t.FACE_RIGHT, t.FACE_EDGE)]
    x1, y1 = x + 1, y + 1
    for z in range(1, height):
        parts.append(seam((x, y1, z), (x1, y1, z)))
        parts.append(seam((x1, y, z), (x1, y1, z)))
    return "".join(parts)


def slot_outline(x: int, y: int, z: int) -> str:
    corners = [(x + 0.14, y + 0.14, z), (x + 0.86, y + 0.14, z), (x + 0.86, y + 0.86, z), (x + 0.14, y + 0.86, z)]
    return (
        f'<polygon points="{points(corners)}" fill="none" stroke="{t.ACCENT}" '
        'stroke-width="1.4" stroke-dasharray="5 4" opacity="0.75"/>'
    )


def structure() -> str:
    # Painter's algorithm: cells further from the camera are drawn first.
    cells = sorted(
        ((x, y) for x in range(len(HEIGHTS)) for y in range(len(HEIGHTS[x]))),
        key=lambda cell: cell[0] + cell[1],
    )
    parts: list[str] = []
    for x, y in cells:
        height = HEIGHTS[x][y]
        parts.append(column(x, y, height))
        if (x, y) == SLOT:
            parts.append(slot_outline(x, y, height))
            block = cuboid(
                x, y, HOVER_Z, HOVER_Z + 1,
                t.ACCENT, t.ACCENT_SHADE_LIGHT, t.ACCENT_SHADE_DARK, t.ACCENT,
            )
            parts.append(f'<g class="hover">{block}</g>')
    return "".join(parts)


def copy_block() -> str:
    left = t.PANEL_PADDING
    label_x = left + 24
    name = outline(NAME, x=left, y=208, size=88, weight=600, tracking=-0.03)
    if left + name.width > project(0, 5, 0)[0] - 24:
        raise ValueError("The name collides with the artwork.")
    return "".join(
        (
            f'<rect x="{left}" y="97" width="11" height="11" fill="{t.ACCENT}"/>',
            text_path(EYEBROW, fill=t.TEXT_MUTED, x=label_x, y=109, size=19, family="mono", weight=500, tracking=0.08),
            f'<path fill="{t.TEXT}" d="{name.d}"/>',
            text_path(TAGLINE[0], fill=t.TEXT_MUTED, x=left, y=268, size=29, tracking=-0.01),
            text_path(TAGLINE[1], fill=t.TEXT_MUTED, x=left, y=308, size=29, tracking=-0.01),
        )
    )


def build() -> str:
    width = t.PANEL_WIDTH
    halo_x, halo_y = project(SLOT[0] + 0.5, SLOT[1] + 0.5, HOVER_Z + 0.5)
    label = f"{NAME}. General builder based in Bengaluru. {' '.join(TAGLINE)}"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {HEIGHT}" width="{width}" height="{HEIGHT}" role="img" aria-label="{label}">
<title>{label}</title>
<style>
.hover{{animation:hover 5s ease-in-out infinite alternate}}
.halo{{animation:halo 5s ease-in-out infinite alternate}}
@keyframes hover{{to{{transform:translateY(-12px)}}}}
@keyframes halo{{to{{opacity:.55}}}}
@media (prefers-reduced-motion:reduce){{.hover,.halo{{animation:none}}}}
</style>
<defs>
<pattern id="dots" width="26" height="26" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.1" fill="{t.DOT}"/></pattern>
<linearGradient id="fade"><stop offset="0.42" stop-color="#000"/><stop offset="0.8" stop-color="#fff"/></linearGradient>
<mask id="dots-mask"><rect width="{width}" height="{HEIGHT}" fill="url(#fade)"/></mask>
<radialGradient id="glow"><stop stop-color="{t.ACCENT}" stop-opacity="0.15"/><stop offset="1" stop-color="{t.ACCENT}" stop-opacity="0"/></radialGradient>
<clipPath id="panel"><rect width="{width}" height="{HEIGHT}" rx="{t.PANEL_RADIUS}"/></clipPath>
</defs>
<g clip-path="url(#panel)">
<rect width="{width}" height="{HEIGHT}" fill="{t.BACKGROUND}"/>
<rect width="{width}" height="{HEIGHT}" fill="url(#dots)" mask="url(#dots-mask)"/>
<circle class="halo" cx="{halo_x:.1f}" cy="{halo_y:.1f}" r="190" fill="url(#glow)"/>
{structure()}
{copy_block()}
</g>
<rect x="0.5" y="0.5" width="{width - 1}" height="{HEIGHT - 1}" rx="{t.PANEL_RADIUS}" fill="none" stroke="{t.BORDER}"/>
</svg>
"""


def main() -> None:
    t.ASSETS.mkdir(exist_ok=True)
    path = t.ASSETS / "hero.svg"
    path.write_text(build(), encoding="utf-8", newline="\n")
    print(f"wrote {path} ({path.stat().st_size / 1024:.1f} KiB)")


if __name__ == "__main__":
    main()
