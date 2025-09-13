from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Union


def ctc_palette(
    type: str = "built_in",
    palette_name: Optional[Union[int, str]] = None,
    n: Optional[int] = None,
    direction: int = 1,
    color_pick: Optional[Dict] = None,
    show_colors: bool = False,
    palette_title: Optional[str] = None,
) -> List[str]:
    """Python-style entry to generate palettes similar to R's ctc_palette().

    - type='built_in': use built-in palettes (seq/div/qual); identify by index/element name/CN/EN
      - controls: palette_name, n, direction
    - type='custom': use color_pick (from create_color_pick) to select by group/subgroup/ids
      - controls: color_pick, n, direction
    - show_colors: preview the palette via a simple bar plot
    - palette_title: title of the preview when show_colors=True
    Returns list of hex colors.
    """
    from .palettes import get_palette, custom_palette_pick

    type = str(type).lower()
    if type not in ("built_in", "custom"):
        raise ValueError("type must be 'built_in' or 'custom'")

    if type == "built_in":
        if palette_name is None:
            raise ValueError("When type='built_in', 'palette_name' must be provided")
        colors = get_palette(palette_name, n=n, direction=direction)
        # Build a rich default title if not provided: [index element] CN EN
        if palette_title is None:
            try:
                from .dataset import load_palette_list
                pl_map, order = load_palette_list()
                key = None
                idx = None
                if isinstance(palette_name, int):
                    if 1 <= palette_name <= len(order):
                        key = order[palette_name - 1]
                        idx = palette_name
                elif isinstance(palette_name, str):
                    # exact element match
                    if palette_name in pl_map:
                        key = palette_name
                        idx = order.index(key) + 1
                    else:
                        # match by CN/EN names (case-insensitive)
                        low = palette_name.lower()
                        for i, k in enumerate(order):
                            p = pl_map[k]
                            if str(p.get("palette_name","")) .lower() == low or str(p.get("palette_name_e","")) .lower() == low:
                                key = k
                                idx = i + 1
                                break
                if key:
                    p = pl_map[key]
                    cn = p.get("palette_name", "") or ""
                    en = p.get("palette_name_e", "") or ""
                    title = f"[{idx:02d} {key}] {cn} {en}".strip()
                else:
                    title = str(palette_name)
            except Exception:
                title = str(palette_name)
        else:
            title = palette_title
    else:
        if color_pick is None:
            raise ValueError("When type='custom', 'color_pick' must be provided (see create_color_pick())")
        colors = custom_palette_pick(color_pick, n=n, direction=direction)
        title = palette_title or "unnamed palette"

    if show_colors:
        from .plotting import plot_palette as _plot
        _plot(colors, name=title, show_text=True)

    return colors
