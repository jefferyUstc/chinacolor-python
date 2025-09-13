from __future__ import annotations

from typing import Dict, List, Optional

from .palettes import get_palette, find_palette
from .cmap import get_cmap


_RECOMMENDED: Dict[str, Dict[str, List[str]]] = {
    # ids refer to element names in palette_list.json; code will validate existence
    "paper": {
        "categorical": ["qual15", "qual18", "qual10"],
        "sequential": ["seq12", "seq11"],
        "diverging": ["div10", "div13"],
    },
    "mineral": {
        "categorical": ["qual14", "qual18"],
        "sequential": ["seq09", "seq05"],
        "diverging": ["div10", "div14"],
    },
    "ink": {
        "categorical": ["qual11", "qual17"],
        "sequential": ["seq05", "seq03"],
        "diverging": ["div12", "div15"],
    },
    "bronze": {
        "categorical": ["qual12", "qual16"],
        "sequential": ["seq10", "seq07"],
        "diverging": ["div03", "div08"],
    },
    "dunhuang": {
        "categorical": ["qual13", "qual19"],
        "sequential": ["seq08", "seq06"],
        "diverging": ["div13", "div18"],
    },
}


def recommended_palettes_for_theme(name: str) -> Dict[str, List[str]]:
    name = name.lower()
    if name not in _RECOMMENDED:
        raise KeyError(f"Unknown theme: {name}")
    # filter by actual existence in palette_list
    rec = _RECOMMENDED[name]
    out: Dict[str, List[str]] = {}
    for kind, ids in rec.items():
        actual: List[str] = []
        for pid in ids:
            try:
                find_palette(pid)
                actual.append(pid)
            except Exception:
                continue
        out[kind] = actual
    return out


def pick_palette_for_theme(name: str, kind: str = "categorical", n: Optional[int] = None, direction: int = 1) -> List[str]:
    rec = recommended_palettes_for_theme(name)
    ids = rec.get(kind)
    if not ids:
        raise ValueError(f"No recommended palettes for theme={name} kind={kind}")
    return get_palette(ids[0], n=n, direction=direction)


def pick_cmap_for_theme(name: str, kind: str = "sequential", direction: int = 1):
    """Return a matplotlib Colormap recommended for a theme.

    kind: 'sequential' or 'diverging'.
    """
    rec = recommended_palettes_for_theme(name)
    if kind not in ("sequential", "diverging"):
        raise ValueError("kind must be 'sequential' or 'diverging'")
    ids = rec.get(kind)
    if not ids:
        raise ValueError(f"No recommended {kind} palettes for theme={name}")
    return get_cmap(ids[0], direction=direction)
