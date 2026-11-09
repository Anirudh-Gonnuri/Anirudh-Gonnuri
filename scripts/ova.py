"""Generate assets/ova.svg: the callout that points visitors at Ova.

This is the only solid-accent panel on the profile, so it is the first thing the
eye lands on after the banner. The ring is a cycle drawn with uneven ticks, because
Ova treats irregularity as the default rather than the exception.
"""

from math import cos, radians, sin

import theme as t
from text import outline, text_path

HEIGHT = 280

EYEBROW = "NOW BUILDING  /  TEAM PROJECT"
NAME = "Ova"
DESCRIPTION = (
    "A PCOS-focused cycle tracker that treats",
    "irregularity as the default, not the exception.",
)

# Replace with the domain once the site is live, and link the image in README.md.
SITE_LABEL = "SITE COMING SOON"

RING_CENTER = (1088, 140)
RING_INNER_RADIUS = 74
# One tick per day of a cycle. The uneven lengths are the point of the drawing.
TICK_LENGTHS = (
    18, 34, 12, 26, 42, 16, 22, 38, 14, 30, 20, 46, 12, 24,
    36, 18, 28, 14, 40, 22, 16, 32, 44, 12, 26, 20, 34, 16,
)


def ring() -> str:
    cx, cy = RING_CENTER
    ticks: list[str] = []
    for index, length in enumerate(TICK_LENGTHS):
        angle = radians(index * 360 / len(TICK_LENGTHS) - 90)
        inner, outer = RING_INNER_RADIUS, RING_INNER_RADIUS + length
        ticks.append(
            f'<line x1="{cx + inner * cos(angle):.1f}" y1="{cy + inner * sin(angle):.1f}" '
            f'x2="{cx + outer * cos(angle):.1f}" y2="{cy + outer * sin(angle):.1f}"/>'
        )
    return (
        f'<g class="ring" stroke="{t.ON_ACCENT}" stroke-width="5" stroke-linecap="round">'
        f'{"".join(ticks)}</g>'
        f'<circle cx="{cx}" cy="{cy}" r="9" fill="{t.ON_ACCENT}"/>'
    )


def status_pill(x: float, baseline: float) -> str:
    height = 46
    y = baseline - height
    padding = 22
    dot_x = x + padding + 5
    text_x = dot_x + 18
    label = outline(
        SITE_LABEL, x=text_x, y=y + 30, size=18, family="mono", weight=600, tracking=0.08
    )
    width = text_x + label.width + padding - x
    return "".join(
        (
            f'<rect x="{x:.1f}" y="{y}" width="{width:.1f}" height="{height}" '
            f'rx="{height / 2}" fill="{t.ON_ACCENT}"/>',
            f'<circle class="pulse" cx="{dot_x:.1f}" cy="{y + height / 2}" r="5" fill="{t.ACCENT}"/>',
            f'<path fill="{t.ACCENT}" d="{label.d}"/>',
        )
    )


def copy_block() -> str:
    left = t.PANEL_PADDING
    baseline = 148
    name = outline(NAME, x=left, y=baseline, size=104, weight=600, tracking=-0.03)
    return "".join(
        (
            text_path(EYEBROW, fill=t.ON_ACCENT_MUTED, x=left, y=48, size=19, family="mono", weight=600, tracking=0.08),
            f'<path fill="{t.ON_ACCENT}" d="{name.d}"/>',
            status_pill(left + name.width + 30, baseline),
            text_path(DESCRIPTION[0], fill=t.ON_ACCENT, x=left, y=200, size=29, weight=500, tracking=-0.01),
            text_path(DESCRIPTION[1], fill=t.ON_ACCENT, x=left, y=240, size=29, weight=500, tracking=-0.01),
        )
    )


def build() -> str:
    width = t.PANEL_WIDTH
    cx, cy = RING_CENTER
    label = f"{NAME}: {' '.join(DESCRIPTION)} {SITE_LABEL.capitalize()}."
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {HEIGHT}" width="{width}" height="{HEIGHT}" role="img" aria-label="{label}">
<title>{label}</title>
<style>
.ring{{transform-origin:{cx}px {cy}px;animation:turn 90s linear infinite}}
.pulse{{animation:pulse 1.8s ease-in-out infinite alternate}}
@keyframes turn{{to{{transform:rotate(360deg)}}}}
@keyframes pulse{{to{{opacity:.3}}}}
@media (prefers-reduced-motion:reduce){{.ring,.pulse{{animation:none}}}}
</style>
<rect width="{width}" height="{HEIGHT}" rx="{t.PANEL_RADIUS}" fill="{t.ACCENT}"/>
{ring()}
{copy_block()}
</svg>
"""


def main() -> None:
    t.ASSETS.mkdir(exist_ok=True)
    path = t.ASSETS / "ova.svg"
    path.write_text(build(), encoding="utf-8", newline="\n")
    print(f"wrote {path} ({path.stat().st_size / 1024:.1f} KiB)")


if __name__ == "__main__":
    main()
