"""Generate assets/ova.svg: the callout that points visitors at Ova.

The panel is Ova's app icon stretched into a banner: the same pink-to-peach ground
with the magenta wordmark on it. It is the only light panel on a dark profile, so
it pops by contrast alone. The letters ripple gently, one after another, then rest.
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
# Where the letters sit inside the traced 410px icon.
WORDMARK_LEFT, WORDMARK_RIGHT = 70, 341
WORDMARK_TOP, WORDMARK_BOTTOM = 158, 255

WORDMARK_WIDTH = 236
DIVIDER_X = t.PANEL_PADDING + WORDMARK_WIDTH + 48
COPY_X = DIVIDER_X + 48


def wordmark() -> str:
    data = json.loads(WORDMARK.read_text(encoding="utf-8"))
    scale = WORDMARK_WIDTH / (WORDMARK_RIGHT - WORDMARK_LEFT)
    x = t.PANEL_PADDING - WORDMARK_LEFT * scale
    y = HEIGHT / 2 - (WORDMARK_TOP + WORDMARK_BOTTOM) / 2 * scale
    letters = "".join(
        f'<path class="letter" style="animation-delay:{index * 0.22:.2f}s" fill-rule="evenodd" d="{d}"/>'
        for index, d in enumerate(data["letters"])
    )
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({scale:.4f})" fill="{t.OVA_MAGENTA}">{letters}</g>'


def status_pill(right: float, center_y: float) -> str:
    height = 42
    padding = 20
    size = 16
    tracking = 0.08
    label_width = outline(SITE_LABEL, x=0, y=0, size=size, family="mono", weight=600, tracking=tracking).width
    width = padding + 10 + 12 + label_width + padding
    x = right - width
    y = center_y - height / 2
    dot_x = x + padding + 4
    label = outline(
        SITE_LABEL, x=x + padding + 22, y=center_y + 5.6, size=size, family="mono", weight=600, tracking=tracking
    )
    return "".join(
        (
            f'<rect x="{x:.1f}" y="{y}" width="{width:.1f}" height="{height}" rx="{height / 2}" fill="{t.OVA_MAGENTA}"/>',
            f'<circle class="pulse" cx="{dot_x:.1f}" cy="{center_y}" r="4" fill="{t.OVA_TILE_START}"/>',
            f'<path fill="#fff" d="{label.d}"/>',
        )
    )


def copy_block() -> str:
    right = t.PANEL_WIDTH - t.PANEL_PADDING
    first = outline(DESCRIPTION[0], x=COPY_X, y=146, size=33, weight=500, tracking=-0.01)
    second = outline(DESCRIPTION[1], x=COPY_X, y=190, size=33, weight=500, tracking=-0.01)
    if COPY_X + max(first.width, second.width) > right:
        raise ValueError("The description overflows the panel.")
    return "".join(
        (
            text_path(EYEBROW, fill=t.OVA_INK_MUTED, x=COPY_X, y=87, size=19, family="mono", weight=500, tracking=0.08),
            status_pill(right, 80),
            f'<path fill="{t.OVA_INK}" d="{first.d}"/>',
            f'<path fill="{t.OVA_INK}" d="{second.d}"/>',
        )
    )


def build() -> str:
    width = t.PANEL_WIDTH
    glow_x = t.PANEL_PADDING + WORDMARK_WIDTH / 2
    glow_y = HEIGHT / 2
    label = f"Ova: {' '.join(DESCRIPTION)} {SITE_LABEL.capitalize()}."
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {HEIGHT}" width="{width}" height="{HEIGHT}" role="img" aria-label="{label}">
<title>{label}</title>
<style>
.letter{{animation:ripple 6s ease-in-out infinite}}
.glow{{animation:breathe 6s ease-in-out infinite alternate}}
.pulse{{animation:fade 2.4s ease-in-out infinite alternate}}
@keyframes ripple{{0%,50%,100%{{transform:translateY(0)}}18%{{transform:translateY(-16px)}}}}
@keyframes breathe{{to{{opacity:.5}}}}
@keyframes fade{{to{{opacity:.4}}}}
@media (prefers-reduced-motion:reduce){{.letter,.glow,.pulse{{animation:none}}}}
</style>
<defs>
<linearGradient id="ground" x1="0" y1="0.15" x2="1" y2="0"><stop stop-color="{t.OVA_TILE_START}"/><stop offset="1" stop-color="{t.OVA_TILE_END}"/></linearGradient>
<radialGradient id="glow"><stop stop-color="#fff" stop-opacity="0.7"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.25"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<clipPath id="panel"><rect width="{width}" height="{HEIGHT}" rx="{t.PANEL_RADIUS}"/></clipPath>
</defs>
<g clip-path="url(#panel)">
<rect width="{width}" height="{HEIGHT}" fill="url(#ground)"/>
<circle class="glow" cx="{glow_x}" cy="{glow_y}" r="280" fill="url(#glow)"/>
{wordmark()}
<line x1="{DIVIDER_X}" y1="64" x2="{DIVIDER_X}" y2="{HEIGHT - 64}" stroke="{t.OVA_MAGENTA}" stroke-opacity="0.22" stroke-width="1.5"/>
{copy_block()}
</g>
</svg>
"""


def main() -> None:
    t.ASSETS.mkdir(exist_ok=True)
    path = t.ASSETS / "ova.svg"
    path.write_text(build(), encoding="utf-8", newline="\n")
    print(f"wrote {path} ({path.stat().st_size / 1024:.1f} KiB)")


if __name__ == "__main__":
    main()
