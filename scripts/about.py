"""Generate assets/about.svg: where things stand, in three columns."""

from dataclasses import dataclass

import theme as t
from panel import dark_panel, write_asset
from text import outline, text_path

HEIGHT = 256

EYEBROW_Y = 72
TITLE_Y = 122
DETAIL_Y = 162
DETAIL_LINE_HEIGHT = 30
COLUMN_GAP = 48


@dataclass(frozen=True)
class Column:
    eyebrow: str
    title: str
    detail: tuple[str, ...]
    x: int
    width: int
    highlighted: bool = False


COLUMNS = (
    Column(
        "STUDYING",
        "MCA",
        ("CHRIST (Deemed to be University),", "Central Campus, Bengaluru"),
        x=t.PANEL_PADDING,
        width=372,
    ),
    Column(
        "NEXT",
        "DataNeurus",
        ("Joining in January 2027",),
        x=540,
        width=280,
        highlighted=True,
    ),
    Column(
        "CURRENTLY",
        "Ova and Atrium",
        ("A cycle-tracking app, and a", "hub for my automations"),
        x=868,
        width=340,
    ),
)


def render_column(column: Column) -> str:
    colour = t.ACCENT if column.highlighted else t.TEXT_FAINT
    detail = [
        outline(line, x=column.x, y=DETAIL_Y + index * DETAIL_LINE_HEIGHT, size=22)
        for index, line in enumerate(column.detail)
    ]
    if max(line.width for line in detail) > column.width:
        raise ValueError(f"The {column.eyebrow} column overflows.")
    return "".join(
        (
            text_path(column.eyebrow, fill=colour, x=column.x, y=EYEBROW_Y, size=17, family="mono", weight=500, tracking=0.08),
            text_path(column.title, fill=t.TEXT, x=column.x, y=TITLE_Y, size=38, weight=500, tracking=-0.02),
            *(f'<path fill="{t.TEXT_MUTED}" d="{line.d}"/>' for line in detail),
        )
    )


def divider(x: float) -> str:
    return f'<line x1="{x}" y1="56" x2="{x}" y2="{HEIGHT - 56}" stroke="{t.BORDER}"/>'


def build() -> str:
    dividers = "".join(divider(column.x - COLUMN_GAP / 2) for column in COLUMNS[1:])
    columns = "".join(render_column(column) for column in COLUMNS)
    label = " ".join(
        f"{column.eyebrow.capitalize()}: {column.title}, {' '.join(column.detail)}." for column in COLUMNS
    )
    return dark_panel(label, HEIGHT, dividers + columns)


if __name__ == "__main__":
    write_asset("about.svg", build())
