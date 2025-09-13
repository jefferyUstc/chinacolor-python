from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from importlib.resources import files


_PACKAGE_DATA_DIR = "data"
_FALLBACK_DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def _read_text_from_package(filename: str) -> Optional[str]:
    try:
        p = files("chinacolor").joinpath(_PACKAGE_DATA_DIR, filename)
        with p.open("r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def _read_text_fallback(filename: str) -> Optional[str]:
    p = _FALLBACK_DATA_DIR / filename
    if p.exists():
        return p.read_text(encoding="utf-8")
    return None


def _load_text(filename: str) -> Optional[str]:
    text = _read_text_from_package(filename)
    if text is None:
        text = _read_text_fallback(filename)
    return text


def _load_json(filename: str) -> Any:
    text = _load_text(filename)
    if text is None:
        raise FileNotFoundError(f"Could not find data file: {filename}")
    return json.loads(text)


def load_chinacolor() -> List[Dict[str, Any]]:
    """Load 384 colors with maximum metadata.

    Priority:
      1) CSV (rich metadata: group_id/subgroup_id/RGB/HSV/LAB/LUV/HSL/...)
      2) JSON fallback (name/hex/CMYK; we synthesize color_id)
    """
    # Try CSV first
    csv_text = _load_text("chinacolor.csv")
    if csv_text is not None:
        # We avoid pandas; parse CSV minimally
        import csv
        from io import StringIO

        reader = csv.DictReader(StringIO(csv_text))
        rows: List[Dict[str, Any]] = []
        for row in reader:
            # Normalize key cases and types
            def _int(v, default=None):
                try:
                    return int(float(v)) if v not in (None, "") else default
                except Exception:
                    return default

            def _float(v, default=None):
                try:
                    return float(v) if v not in (None, "") else default
                except Exception:
                    return default

            r = {k.strip(): v for k, v in row.items()}
            r["color_id"] = _int(r.get("color_id"))
            r["group_id"] = _int(r.get("group_id"))
            r["subgroup_id"] = _int(r.get("subgroup_id"))
            # Ensure hex starts with '#'
            hx = r.get("hex")
            if hx and not hx.startswith("#"):
                r["hex"] = "#" + hx
            # Promote convenience alias used by R functions
            r.setdefault("group", r.get("group_id"))
            r.setdefault("subgroup", r.get("subgroup_id"))
            # Numeric channels (optional)
            for key in ("RGB_R", "RGB_G", "RGB_B"):
                if key in r:
                    r[key] = _float(r.get(key))
            rows.append(r)
        # Sort by color_id if present
        rows.sort(key=lambda d: d.get("color_id") or 10**9)
        return rows

    # JSON fallback
    data = _load_json("chinacolor.json")
    result: List[Dict[str, Any]] = []
    for i, item in enumerate(data, start=1):
        d = dict(item)
        d.setdefault("color_id", i)
        result.append(d)
    return result


def load_palette_list() -> Tuple[Dict[str, Any], List[str]]:
    data = _load_json("palette_list.json")
    keys = list(data.keys())
    return data, keys
