from __future__ import annotations

from typing import Iterable, List, Optional, Union

import matplotlib.pyplot as plt

from .palettes import get_palette
from .dataset import load_chinacolor


def plot_palette(
    identifier: Union[int, str, Iterable[str]],
    n: Optional[int] = None,
    direction: int = 1,
    name: Optional[str] = None,
    show_text: bool = False,
):
    """Visualize a single palette (built-in or custom colors).

    - If identifier is int/str: uses built-in palette
    - If identifier is iterable of hex: treated as custom palette
    """
    if isinstance(identifier, (int, str)):
        colors = get_palette(identifier, n=n, direction=direction)
        title = name or str(identifier)
    else:
        colors = list(identifier)
        title = name or "custom palette"

    m = len(colors)
    fig, ax = plt.subplots(figsize=(max(6, m * 0.5), 1.2))
    for i, hx in enumerate(colors):
        ax.barh(0, 1, left=i, color=hx, edgecolor="#222222")
        if show_text:
            ax.text(i + 0.5, 0, hx, va="center", ha="center", fontsize=8, color="white")
    ax.set_xlim(0, m)
    ax.set_ylim(-0.5, 0.5)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_title(title)
    plt.tight_layout()
    return ax


def plot_palettes(identifiers: Iterable[Union[int, str]], direction: int = 1):
    """Visualize multiple built-in palettes stacked vertically."""
    identifiers = list(identifiers)
    rows = len(identifiers)
    heights = [1.0] * rows
    fig, axes = plt.subplots(rows, 1, figsize=(10, max(2, 0.8 * rows)))
    if rows == 1:
        axes = [axes]
    for ax, ident in zip(axes, identifiers):
        colors = get_palette(ident, n=None, direction=direction)
        m = len(colors)
        for i, hx in enumerate(colors):
            ax.barh(0, 1, left=i, color=hx, edgecolor="#222222")
        ax.set_xlim(0, m)
        ax.set_ylim(-0.5, 0.5)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_title(str(ident), loc="left")
    plt.tight_layout()
    return axes


def plot_color_grid(show_group: bool = False):
    """Plot 384 traditional colors in a 24x16 grid using CSV metadata if available.

    Uses group_id (1..96), subgroup_id (1..4) to place colors into a grid with
    24 rows (solar terms) and 16 columns (4 groups x 4 subgroups).
    """
    colors = load_chinacolor()

    # Compute positions
    tiles = []
    for c in colors:
        g = c.get("group") if c.get("group") is not None else c.get("group_id")
        sg = c.get("subgroup") if c.get("subgroup") is not None else c.get("subgroup_id")
        if g is None or sg is None:
            continue
        row = (g - 1) // 4  # 0..23
        col_block = (g - 1) % 4  # 0..3
        col = col_block * 4 + (sg - 1)  # 0..15
        tiles.append({
            "row": 24 - row,  # invert for visual top-down
            "col": col + 1,
            "hex": c.get("hex"),
            "color_id": c.get("color_id"),
            "group": g,
            "subgroup": sg,
            "RGB_R": c.get("RGB_R"),
            "RGB_G": c.get("RGB_G"),
            "RGB_B": c.get("RGB_B"),
        })

    fig, ax = plt.subplots(figsize=(16, 24))
    for t in tiles:
        x = t["col"]
        y = t["row"]
        ax.add_patch(plt.Rectangle((x - 1, y - 1), 1, 1, facecolor=t["hex"], edgecolor="#222", linewidth=0.2))
        # compute luminance
        r, g, b = t.get("RGB_R"), t.get("RGB_G"), t.get("RGB_B")
        if r is None or g is None or b is None:
            # fallback: approximate from hex via matplotlib
            import matplotlib.colors as mc
            rr, gg, bb = mc.to_rgb(t["hex"])  # 0..1 floats
        else:
            rr, gg, bb = float(r), float(g), float(b)
        lum = 0.299 * rr + 0.587 * gg + 0.114 * bb
        txt_color = "black" if lum > 0.5 else "white"
        ax.text(x - 0.5, y - 0.5, str(t["color_id"]), color=txt_color, ha="center", va="center", fontsize=6)

    if show_group:
        # draw group boxes (4x1 spanning subgroups) for each group and group id label
        drawn = set()
        for t in tiles:
            g = t["group"]
            if g in drawn:
                continue
            drawn.add(g)
            row = (g - 1) // 4
            col_block = (g - 1) % 4
            x0 = col_block * 4
            y0 = 24 - row - 1
            ax.add_patch(plt.Rectangle((x0, y0), 4, 1, fill=False, edgecolor="#888", linewidth=0.6))
            # group id inside left side of box
            ax.text(x0 + 0.15, y0 + 0.5, str(g), va="center", ha="left", fontsize=6, color="#666")

    ax.set_xlim(0, 16)
    ax.set_ylim(0, 24)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("384 Traditional Chinese Colors")
    ax.set_aspect("equal")
    plt.tight_layout()
    return ax
