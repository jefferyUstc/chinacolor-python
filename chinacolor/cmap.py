from __future__ import annotations

from typing import Optional

import numpy as np
from matplotlib.colors import LinearSegmentedColormap, ListedColormap

from .palettes import find_palette, get_palette


def get_cmap(identifier, n: Optional[int] = None, direction: int = 1):
    """Return a matplotlib colormap for a built-in palette.

    - Sequential/diverging -> LinearSegmentedColormap (256 levels)
    - Qualitative -> ListedColormap

    If n is provided and palette is qualitative, return ListedColormap of length n.
    If n is provided for sequential/diverging, n is ignored in colormap construction
    (since colormap is continuous); use it when sampling.
    """
    p = find_palette(identifier)
    ptype = p.get("type", "qualitative")
    colors = get_palette(identifier, n=None, direction=direction)
    if ptype in ("sequential", "diverging"):
        return LinearSegmentedColormap.from_list(str(identifier), colors, N=256)
    else:
        # qualitative
        if n is None:
            return ListedColormap(colors, name=str(identifier))
        else:
            sampled = get_palette(identifier, n=n, direction=direction)
            return ListedColormap(sampled, name=f"{identifier}_{n}")

