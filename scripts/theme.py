"""Design tokens shared by every generated panel.

The palette is deliberately neutral with a single accent, so the accent keeps
its meaning: it marks the one thing on a panel worth looking at first.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONTS = ROOT / "scripts" / "fonts"

# Surfaces
BACKGROUND = "#0b0b0d"
BORDER = "#222226"
DOT = "#34343a"

# Text
TEXT = "#f2f2f3"
TEXT_MUTED = "#a2a2a9"
TEXT_FAINT = "#6e6e76"

# Accent
ACCENT = "#c8f25a"
ACCENT_SHADE_LIGHT = "#94b83b"
ACCENT_SHADE_DARK = "#6a8626"
ON_ACCENT = "#0b0b0d"
ON_ACCENT_MUTED = "#37450f"

# Isometric block faces
FACE_TOP = "#1d1d21"
FACE_LEFT = "#131316"
FACE_RIGHT = "#0f0f12"
FACE_EDGE = "#3a3a41"
FACE_SEAM = "#26262b"

# Panel geometry
PANEL_WIDTH = 1280
PANEL_RADIUS = 20
PANEL_PADDING = 72
