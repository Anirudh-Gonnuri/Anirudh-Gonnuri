"""The dark card shared by the static panels, and the code that writes them to disk."""

import theme as t


def dark_panel(label: str, height: int, body: str) -> str:
    """Wrap ``body`` in a full-width dark card. ``label`` is the accessible description."""
    width = t.PANEL_WIDTH
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{label}">
<title>{label}</title>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="{t.PANEL_RADIUS}" fill="{t.BACKGROUND}" stroke="{t.BORDER}"/>
{body}
</svg>
"""


def write_asset(name: str, svg: str) -> None:
    t.ASSETS.mkdir(exist_ok=True)
    path = t.ASSETS / name
    path.write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {path} ({path.stat().st_size / 1024:.1f} KiB)")
