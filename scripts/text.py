"""Convert text to SVG path data.

GitHub serves README images through a proxy and blocks external resources inside
SVGs, so a web font would silently fall back to a system font. Outlining the text
makes it render identically everywhere and keeps files far smaller than embedding
a font. HarfBuzz does the shaping so kerning is preserved.
"""

from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

from theme import FONTS

FONT_FILES = {
    "sans": FONTS / "Geist-Variable.ttf",
    "mono": FONTS / "GeistMono-Variable.ttf",
}

Family = Literal["sans", "mono"]
Anchor = Literal["start", "end"]


@dataclass(frozen=True)
class Outline:
    """Path data for a run of text, plus its advance width in SVG units."""

    d: str
    width: float


@lru_cache
def _font(family: Family, weight: int) -> hb.Font:
    blob = hb.Blob.from_file_path(str(FONT_FILES[family]))
    font = hb.Font(hb.Face(blob))
    font.set_variations({"wght": weight})
    return font


def _format_number(value: float) -> str:
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


def outline(
    text: str,
    *,
    x: float,
    y: float,
    size: float,
    family: Family = "sans",
    weight: int = 400,
    tracking: float = 0,
    anchor: Anchor = "start",
) -> Outline:
    """Shape ``text`` with its baseline at ``(x, y)``.

    ``tracking`` is extra space between glyphs, in em.
    """
    font = _font(family, weight)
    scale = size / font.face.upem

    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(font, buffer)

    extra = tracking * size
    glyphs = list(zip(buffer.glyph_infos, buffer.glyph_positions))
    width = sum(pos.x_advance * scale + extra for _, pos in glyphs) - extra
    cursor = x - width if anchor == "end" else x

    commands: list[str] = []
    for info, pos in glyphs:
        pen = SVGPathPen(None, ntos=_format_number)
        origin_x = cursor + pos.x_offset * scale
        origin_y = y - pos.y_offset * scale
        font.draw_glyph_with_pen(
            info.codepoint,
            TransformPen(pen, (scale, 0, 0, -scale, origin_x, origin_y)),
        )
        commands.append(pen.getCommands())
        cursor += pos.x_advance * scale + extra

    return Outline(d="".join(commands), width=width)


def text_path(text: str, *, fill: str, **kwargs) -> str:
    """Return a ready-to-embed ``<path>`` element for ``text``."""
    return f'<path fill="{fill}" d="{outline(text, **kwargs).d}"/>'
