"""Generate assets/linkedin.svg: a slim full-width button.

A README can only make a whole image clickable, so each link needs its own image.
"""

import theme as t
from panel import dark_panel, write_asset
from text import outline, text_path

HEIGHT = 104
CENTER_Y = HEIGHT / 2

HANDLE = "in/anirudh-gonnuri"


def badge(x: float) -> str:
    size = 44
    mark = outline("in", x=x + 10, y=CENTER_Y + 10, size=29, weight=700, tracking=-0.02)
    return (
        f'<rect x="{x}" y="{CENTER_Y - size / 2}" width="{size}" height="{size}" rx="10" fill="{t.ACCENT}"/>'
        f'<path fill="{t.BACKGROUND}" d="{mark.d}"/>'
    )


def arrow(x: float, y: float) -> str:
    """A north-east arrow whose bounding box starts at ``(x, y)``."""
    size = 15
    return (
        f'<path d="M{x} {y + size}L{x + size} {y}M{x + 3} {y}H{x + size}V{y + size - 3}" fill="none" '
        f'stroke="{t.ACCENT}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def build() -> str:
    left = t.PANEL_PADDING
    right = t.PANEL_WIDTH - t.PANEL_PADDING
    arrow_x = right - 15
    handle = outline(HANDLE, x=arrow_x - 22, y=CENTER_Y + 7, size=20, family="mono", tracking=0.02, anchor="end")
    body = "".join(
        (
            badge(left),
            text_path("Connect on LinkedIn", fill=t.TEXT, x=left + 66, y=CENTER_Y + 10, size=29, weight=500, tracking=-0.01),
            f'<path fill="{t.TEXT_MUTED}" d="{handle.d}"/>',
            arrow(arrow_x, CENTER_Y - 7.5),
        )
    )
    return dark_panel("Connect with Anirudh Gonnuri on LinkedIn", HEIGHT, body)


if __name__ == "__main__":
    write_asset("linkedin.svg", build())
