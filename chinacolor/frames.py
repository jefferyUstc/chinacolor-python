from __future__ import annotations

from typing import Any, Dict, List

from .dataset import load_chinacolor
from .palettes import list_palettes as _list_palettes


def _require_pandas():
    try:
        import pandas as pd  # noqa: F401
    except Exception as e:
        raise RuntimeError(
            "pandas is required for this function. Install with `pip install pandas` or `pip install chinacolor[pandas]`."
        ) from e


def colors_df():
    """Return all 384 colors as a pandas DataFrame with rich metadata.

    Columns include at least: color_id, name, hex, group_id, subgroup_id, solar_term_c, solar_term_e,
    and may include numeric channels such as RGB_R/G/B, HSV_*, LAB_*, LUV_*, HSL_* when available.
    """
    _require_pandas()
    import pandas as pd

    data = load_chinacolor()
    # Normalize minimal columns
    for d in data:
        if "group_id" not in d and "group" in d:
            d["group_id"] = d.get("group")
        if "subgroup_id" not in d and "subgroup" in d:
            d["subgroup_id"] = d.get("subgroup")
    return pd.DataFrame.from_records(data)


def palettes_df():
    """Return palette metadata as a pandas DataFrame."""
    _require_pandas()
    import pandas as pd

    rows: List[Dict[str, Any]] = _list_palettes()
    return pd.DataFrame.from_records(rows)


def list_colors():
    """Alias of colors_df() for API familiarity with the R package."""
    return colors_df()

