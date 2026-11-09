"""Trace Ova's app icon into per-letter vector paths.

Ova's logo only exists as a 410px PNG. Tracing gives a sharp wordmark and one path
per letter, which is what lets the panel animate the letters independently.

This is a one-off authoring step, because the source lives in a private repo: the
output is committed and the panel generator only reads that.

Usage: python scripts/trace_ova_logo.py path/to/ova_icon.png
"""

import json
import sys
from pathlib import Path

import numpy as np
import potrace
from PIL import Image

from theme import ROOT

OUTPUT = ROOT / "scripts" / "data" / "ova_wordmark.json"
UPSCALE = 6
MIN_SPECK_AREA = 200


def number(value: float) -> str:
    text = f"{value / UPSCALE:.2f}".rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


def to_path(curve) -> str:
    start = curve.start_point
    parts = [f"M{number(start.x)} {number(start.y)}"]
    for segment in curve.segments:
        end = segment.end_point
        if segment.is_corner:
            corner = segment.c
            parts.append(f"L{number(corner.x)} {number(corner.y)}L{number(end.x)} {number(end.y)}")
        else:
            first, second = segment.c1, segment.c2
            parts.append(
                f"C{number(first.x)} {number(first.y)} {number(second.x)} {number(second.y)} "
                f"{number(end.x)} {number(end.y)}"
            )
    return "".join(parts) + "Z"


def bounds(curve) -> tuple[float, float, float, float]:
    xs = [curve.start_point.x]
    ys = [curve.start_point.y]
    for segment in curve.segments:
        anchor = segment.c if segment.is_corner else segment.end_point
        xs += [anchor.x, segment.end_point.x]
        ys += [anchor.y, segment.end_point.y]
    return min(xs), min(ys), max(xs), max(ys)


def wordmark_mask(image: Image.Image) -> np.ndarray:
    # The tile is pale and the wordmark is saturated, so green separates them cleanly.
    enlarged = image.convert("RGB").resize(
        (image.width * UPSCALE, image.height * UPSCALE), Image.Resampling.LANCZOS
    )
    green = np.asarray(enlarged)[:, :, 1].astype(float)
    return green < (green.min() + green.max()) / 2


def group_letters(curves: list) -> list[str]:
    """Attach each counter (hole) to the letter that encloses it, left to right."""
    boxed = sorted(((bounds(c), c) for c in curves), key=lambda item: item[0][0])
    letters: list[tuple[tuple[float, float, float, float], list]] = []
    for box, curve in boxed:
        center_x, center_y = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        for outer, members in letters:
            if outer[0] < center_x < outer[2] and outer[1] < center_y < outer[3]:
                members.append(curve)
                break
        else:
            letters.append((box, [curve]))
    letters.sort(key=lambda item: item[0][0])
    return ["".join(to_path(c) for c in members) for _, members in letters]


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    image = Image.open(Path(sys.argv[1]))
    # potracer traces False regions as the shape, so the mask has to be inverted.
    curves = list(
        potrace.Bitmap(~wordmark_mask(image)).trace(
            turdsize=MIN_SPECK_AREA, alphamax=1.1, opticurve=True, opttolerance=0.6
        )
    )
    letters = group_letters(curves)
    if len(letters) != 3:
        sys.exit(f"Expected the three letters o, v, a but found {len(letters)} shapes.")

    OUTPUT.parent.mkdir(exist_ok=True)
    payload = {"size": image.width, "letters": letters}
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT}: {len(curves)} curves in {len(letters)} letters")


if __name__ == "__main__":
    main()
