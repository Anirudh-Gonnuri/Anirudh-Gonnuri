"""Generate assets/activity.svg and assets/languages.svg from live GitHub data.

Requires GH_TOKEN. Private contributions and repositories are only counted when the
token can see them, and only ever appear as totals.
"""

import os
import statistics
import sys
from datetime import date, timedelta

import theme as t
from github_data import Language, Stats, fetch
from panel import dark_panel, write_asset
from text import outline, text_path

ACTIVITY_HEIGHT = 426
LANGUAGES_HEIGHT = 288
TOP_LANGUAGES = 8

# One hue, brightening with magnitude: on a dark card, more is lighter.
HEAT_RAMP = ("#17171b", "#4d1b33", "#8a2c55", "#c73b72", t.ACCENT)

GRID_WIDTH = t.PANEL_WIDTH - 2 * t.PANEL_PADDING
GRID_TOP = 228
GRID_ROWS = 7
CELL_SIZE = 18
CELL_RADIUS = 4


def heat_levels(counts: list[int]) -> tuple[float, float, float] | None:
    """Return quartile cut points of the non-zero days.

    Quartiles rather than a linear scale, so one unusually large day cannot wash
    out the rest of the year.
    """
    active = [count for count in counts if count > 0]
    if not active:
        return None
    if len(active) == 1:
        return (active[0], active[0], active[0])
    first, second, third = statistics.quantiles(active, n=4, method="inclusive")
    return (first, second, third)


def heat_level(count: int, cuts: tuple[float, float, float] | None) -> int:
    if count == 0 or cuts is None:
        return 0
    return 1 + sum(count > cut for cut in cuts)


def _sunday_on_or_before(day: date) -> date:
    return day - timedelta(days=(day.weekday() + 1) % 7)


def _heatmap(days: tuple[tuple[date, int], ...]) -> str:
    start = _sunday_on_or_before(days[0][0])
    columns = (days[-1][0] - start).days // 7 + 1
    pitch = (GRID_WIDTH - CELL_SIZE) / (columns - 1)
    row_pitch = CELL_SIZE + (pitch - CELL_SIZE)
    cuts = heat_levels([count for _, count in days])

    parts: list[str] = []
    month_columns: list[tuple[int, date]] = []
    for day, count in days:
        offset = (day - start).days
        column, row = offset // 7, offset % 7
        x = t.PANEL_PADDING + column * pitch
        y = GRID_TOP + row * row_pitch
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
            f'rx="{CELL_RADIUS}" fill="{HEAT_RAMP[heat_level(count, cuts)]}"/>'
        )
        if day.day == 1:
            month_columns.append((column, day))

    for column, day in month_columns:
        # A label needs room before the next month or the panel's edge.
        if column <= columns - 3:
            parts.append(
                text_path(
                    day.strftime("%b").upper(), fill=t.TEXT_FAINT,
                    x=t.PANEL_PADDING + column * pitch, y=GRID_TOP - 14,
                    size=15, family="mono", weight=500, tracking=0.06,
                )
            )
    return "".join(parts)


def _legend(right: float, baseline: float) -> str:
    size, gap = 16, 5
    more = outline("MORE", x=right, y=baseline, size=15, family="mono", weight=500, tracking=0.06, anchor="end")
    swatches_right = right - more.width - 12
    swatches_left = swatches_right - len(HEAT_RAMP) * size - (len(HEAT_RAMP) - 1) * gap
    swatches = "".join(
        f'<rect x="{swatches_left + index * (size + gap):.1f}" y="{baseline - 14}" width="{size}" '
        f'height="{size}" rx="3.5" fill="{colour}"/>'
        for index, colour in enumerate(HEAT_RAMP)
    )
    less = outline(
        "LESS", x=swatches_left - 12, y=baseline, size=15, family="mono", weight=500, tracking=0.06, anchor="end"
    )
    return f'<path fill="{t.TEXT_FAINT}" d="{less.d}{more.d}"/>{swatches}'


def _eyebrow(text: str) -> str:
    return text_path(text, fill=t.TEXT_MUTED, x=t.PANEL_PADDING, y=64, size=17, family="mono", weight=500, tracking=0.08)


def activity(stats: Stats) -> str:
    tiles = (
        (f"{stats.total_contributions:,}", "CONTRIBUTIONS"),
        (f"{stats.busiest_day:,}", "BUSIEST DAY"),
        (f"{stats.repositories:,}", "REPOSITORIES"),
        (f"{len(stats.languages):,}", "LANGUAGES"),
    )
    column = GRID_WIDTH / len(tiles)
    kpis = "".join(
        text_path(value, fill=t.TEXT, x=t.PANEL_PADDING + index * column, y=138, size=56, weight=500, tracking=-0.02)
        + text_path(
            label, fill=t.TEXT_MUTED, x=t.PANEL_PADDING + index * column, y=170,
            size=16, family="mono", weight=500, tracking=0.08,
        )
        for index, (value, label) in enumerate(tiles)
    )
    body = "".join(
        (
            _eyebrow("LAST 12 MONTHS"),
            _legend(t.PANEL_WIDTH - t.PANEL_PADDING, 64),
            kpis,
            _heatmap(stats.days),
        )
    )
    label = (
        f"Contribution heatmap for the last 12 months: {stats.total_contributions:,} contributions, "
        f"busiest day {stats.busiest_day}, across {stats.repositories} repositories "
        f"and {len(stats.languages)} languages."
    )
    return dark_panel(label, ACTIVITY_HEIGHT, body)


def _language_row(language: Language, x: float, y: float, column_width: float, largest: float) -> str:
    name_width, value_width = 138, 76
    track_x = x + name_width
    track_width = column_width - name_width - value_width
    bar_height = 10
    bar_y = y - bar_height + 1
    bar_width = max(track_width * language.share / largest, bar_height)
    value = outline(
        f"{language.share * 100:.0f}%", x=x + column_width, y=y + 3, size=20,
        family="mono", tracking=0.02, anchor="end",
    )
    return "".join(
        (
            text_path(language.name, fill=t.TEXT, x=x, y=y + 3, size=23),
            f'<rect x="{track_x}" y="{bar_y}" width="{track_width}" height="{bar_height}" rx="5" fill="{HEAT_RAMP[0]}"/>',
            f'<rect x="{track_x}" y="{bar_y}" width="{bar_width:.1f}" height="{bar_height}" rx="5" fill="{language.colour or t.ACCENT}"/>',
            f'<path fill="{t.TEXT_MUTED}" d="{value.d}"/>',
        )
    )


def languages(stats: Stats) -> str:
    top = stats.languages[:TOP_LANGUAGES]
    gutter = 72
    column_width = (GRID_WIDTH - gutter) / 2
    per_column = (len(top) + 1) // 2
    largest = top[0].share
    rows = "".join(
        _language_row(
            language,
            t.PANEL_PADDING + (index // per_column) * (column_width + gutter),
            126 + (index % per_column) * 40,
            column_width,
            largest,
        )
        for index, language in enumerate(top)
    )
    label = "Languages by code size, excluding notebooks and markup: " + ", ".join(
        f"{language.name} {language.share * 100:.0f}%" for language in top
    )
    return dark_panel(label, LANGUAGES_HEIGHT, _eyebrow("LANGUAGES  /  BY CODE SIZE, EXCLUDING NOTEBOOKS AND MARKUP") + rows)


def main() -> None:
    token = os.environ.get("GH_TOKEN")
    if not token:
        sys.exit("GH_TOKEN is not set.")
    stats = fetch(token)
    if not stats.days or not stats.languages:
        sys.exit("GitHub returned no data, so the existing panels were left alone.")
    write_asset("activity.svg", activity(stats))
    write_asset("languages.svg", languages(stats))


if __name__ == "__main__":
    main()
