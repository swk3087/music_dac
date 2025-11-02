"""
Shared UI style definitions for the Music DAC application.
"""

from PyQt6.QtGui import QFont

import config


BASE_STYLESHEET = f"""
    * {{
        color: {config.COLOR_TEXT};
        font-family: 'Inter', 'Noto Sans KR', 'Segoe UI', sans-serif;
    }}

    QWidget {{
        background-color: transparent;
    }}

    QLabel[role="title"] {{
        font-size: 185%;
        font-weight: 800;
        letter-spacing: 0.6px;
    }}

    QLabel[role="subtitle"] {{
        font-size: 120%;
        color: {config.COLOR_TEXT_SECONDARY};
        font-weight: 500;
    }}

    QLabel[role="caption"] {{
        font-size: 90%;
        color: rgba(255, 255, 255, 0.55);
    }}

    QScrollArea {{
        background: transparent;
        border: none;
    }}

    QFrame#card {{
        background-color: rgba(15, 18, 26, 0.9);
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }}

    QFrame#section {{
        background-color: rgba(255, 255, 255, 0.03);
        border-radius: 18px;
        border: 1px solid rgba(255, 255, 255, 0.04);
    }}

    QPushButton {{
        border: none;
        font-weight: 600;
        letter-spacing: 0.2px;
        padding: 0.9em 1.25em;
        text-align: left;
        font-size: 110%;
    }}

    QPushButton[variant="primary"] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {config.COLOR_PRIMARY},
            stop:1 {config.COLOR_SECONDARY});
        color: {config.COLOR_TEXT};
        border-radius: 18px;
        font-size: 115%;
    }}

    QPushButton[variant="primary"]:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {config.COLOR_SECONDARY},
            stop:1 {config.COLOR_PRIMARY});
    }}

    QPushButton[variant="accent"] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {config.COLOR_ACCENT},
            stop:1 #7EF0FF);
        color: #0E1117;
        border-radius: 18px;
        font-size: 115%;
        font-weight: 700;
    }}

    QPushButton[variant="accent"]:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #7EF0FF,
            stop:1 {config.COLOR_ACCENT});
    }}

    QPushButton[variant="surface"] {{
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        color: {config.COLOR_TEXT};
        font-size: 110%;
    }}

    QPushButton[variant="surface"]:hover {{
        background-color: rgba(255, 255, 255, 0.09);
        border-color: rgba(255, 255, 255, 0.15);
    }}

    QPushButton[variant="ghost"] {{
        background-color: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        color: {config.COLOR_TEXT_SECONDARY};
        font-size: 105%;
        font-weight: 600;
        text-align: center;
        padding: 0.8em 1.2em;
    }}

    QPushButton[variant="ghost"]:hover {{
        background-color: rgba(255, 255, 255, 0.2);
        border-color: rgba(255, 255, 255, 0.25);
        color: #101218;
    }}

    QPushButton[variant="ghost"]:pressed {{
        background-color: rgba(255, 255, 255, 0.18);
        color: #101218;
    }}

    QPushButton[variant="roundAccent"] {{
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.9,
            stop:0 {config.COLOR_ACCENT},
            stop:1 rgba(102, 255, 224, 0.2));
        color: #0E1117;
        border-radius: 26px;
        font-size: 240%;
        min-width: 6.6em;
        min-height: 6.6em;
        text-align: center;
        padding: 0;
    }}

    QPushButton[variant="roundAccent"]:hover {{
        background: qradialgradient(cx:0.5, cy:0.5, radius:1,
            stop:0 #7EF0FF,
            stop:1 rgba(102, 255, 224, 0.35));
    }}

    QPushButton[variant="roundSurface"] {{
        background-color: rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        color: {config.COLOR_TEXT};
        font-size: 180%;
        min-width: 5.4em;
        min-height: 5.4em;
        text-align: center;
        padding: 0;
    }}

    QPushButton[variant="roundSurface"]:hover {{
        background-color: rgba(255, 255, 255, 0.18);
    }}

    QLineEdit#searchField,
    QLineEdit#aiSearchField {{
        background-color: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 1em 1.2em;
        font-size: 110%;
        color: {config.COLOR_TEXT};
    }}

    QLineEdit#searchField:focus,
    QLineEdit#aiSearchField:focus {{
        border-color: {config.COLOR_ACCENT};
        background-color: rgba(255, 255, 255, 0.1);
    }}

    QListWidget#resultsList {{
        background-color: rgba(15, 18, 26, 0.85);
        border-radius: 18px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 12px;
        font-size: 100%;
    }}

    QListWidget#resultsList::item {{
        padding: 14px 12px;
        margin: 2px 0;
        border-radius: 12px;
    }}

    QListWidget#resultsList::item:hover {{
        background-color: rgba(255, 255, 255, 0.06);
    }}

    QListWidget#resultsList::item:selected {{
        background-color: rgba(29, 185, 84, 0.6);
        border: 1px solid rgba(29, 185, 84, 0.9);
    }}

    QSlider::groove:horizontal {{
        height: 8px;
        background-color: rgba(255, 255, 255, 0.08);
        border-radius: 4px;
    }}

    QSlider::handle:horizontal {{
        background-color: {config.COLOR_ACCENT};
        border: none;
        width: 18px;
        margin: -6px 0;
        border-radius: 9px;
    }}

    QSlider::sub-page:horizontal {{
        background-color: {config.COLOR_PRIMARY};
        border-radius: 4px;
    }}
"""

# Responsive scaling defaults
RESPONSIVE_BASE_WIDTH = 640
RESPONSIVE_BASE_HEIGHT = 480
RESPONSIVE_MIN_SCALE = 0.35
RESPONSIVE_MAX_SCALE = 1.1


def compute_responsive_scale(
    width,
    height,
    base_width=RESPONSIVE_BASE_WIDTH,
    base_height=RESPONSIVE_BASE_HEIGHT,
    min_scale=RESPONSIVE_MIN_SCALE,
    max_scale=RESPONSIVE_MAX_SCALE,
):
    """Calculate a clamped scale factor based on available size."""
    width = max(int(width), 1)
    height = max(int(height), 1)

    width_scale = width / float(base_width)
    height_scale = height / float(base_height)

    aspect_scale = min(width_scale, height_scale)
    return max(min_scale, min(max_scale, aspect_scale))


def apply_font_scaling(scaling_items, scale):
    """
    Apply responsive font sizes to a list of widgets.

    Each item in scaling_items should be a tuple of (widget, base_pt, min_pt).
    """
    if not scaling_items:
        return []

    applied_sizes = []

    for widget, base_pt, min_pt in scaling_items:
        if widget is None:
            applied_sizes.append(None)
            continue

        font = QFont(widget.font())
        target_pt = max(min_pt, int(round(base_pt * scale)))
        font.setPointSize(target_pt)
        widget.setFont(font)
        applied_sizes.append(target_pt)

    return applied_sizes


def scale_padding(
    base_vertical,
    base_horizontal,
    scale,
    min_vertical=6,
    min_horizontal=10,
    max_vertical=None,
    max_horizontal=None,
):
    """Scale padding values and clamp to provided min/max bounds."""
    vertical = int(round(base_vertical * scale))
    horizontal = int(round(base_horizontal * scale))

    if max_vertical is not None:
        vertical = min(vertical, max_vertical)
    if max_horizontal is not None:
        horizontal = min(horizontal, max_horizontal)

    vertical = max(min_vertical, vertical)
    horizontal = max(min_horizontal, horizontal)

    return vertical, horizontal
