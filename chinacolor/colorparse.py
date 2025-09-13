from __future__ import annotations

import re
from typing import Iterable, List


def _hex6(h: str) -> str:
    h = h.strip()
    if not h.startswith("#"):
        h = "#" + h
    if re.fullmatch(r"#[0-9A-Fa-f]{3}", h):
        r, g, b = h[1], h[2], h[3]
        return f"#{r}{r}{g}{g}{b}{b}".upper()
    if re.fullmatch(r"#[0-9A-Fa-f]{6}", h):
        return h.upper()
    if re.fullmatch(r"#[0-9A-Fa-f]{8}", h):
        return ("#" + h[1:7]).upper()  # drop alpha
    raise ValueError(f"Invalid hex color: {h}")


def _clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def _rgb_to_hex_float(r: float, g: float, b: float) -> str:
    r = int(round(_clamp01(r) * 255))
    g = int(round(_clamp01(g) * 255))
    b = int(round(_clamp01(b) * 255))
    return f"#{r:02X}{g:02X}{b:02X}"


def _parse_number(tok: str) -> float:
    tok = tok.strip()
    if tok.endswith("%"):
        return float(tok[:-1]) / 100.0
    return float(tok)


def _parse_rgb(text: str) -> str:
    # rgb(r,g,b) with r,g,b in 0..255 or 0..1 or percent
    inner = text[text.find("(") + 1 : text.rfind(")")]
    parts = [p.strip() for p in inner.split(",")]
    if len(parts) < 3:
        raise ValueError("rgb() requires 3 components")
    vals = [_parse_number(p) for p in parts[:3]]
    # if any > 1, assume 0..255 range
    if any(v > 1 for v in vals):
        r, g, b = [v / 255.0 for v in vals]
    else:
        r, g, b = vals
    return _rgb_to_hex_float(r, g, b)


def _parse_hsv(text: str) -> str:
    import colorsys

    inner = text[text.find("(") + 1 : text.rfind(")")]
    parts = [p.strip() for p in inner.split(",")]
    if len(parts) < 3:
        raise ValueError("hsv() requires 3 components")
    h = _parse_number(parts[0])
    s = _parse_number(parts[1])
    v = _parse_number(parts[2])
    # h in degrees or 0..1
    if h > 1:
        h = (h % 360.0) / 360.0
    # s,v percent -> 0..1 already handled
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return _rgb_to_hex_float(r, g, b)


def _parse_hsl(text: str) -> str:
    import colorsys

    inner = text[text.find("(") + 1 : text.rfind(")")]
    parts = [p.strip() for p in inner.split(",")]
    if len(parts) < 3:
        raise ValueError("hsl() requires 3 components")
    h = _parse_number(parts[0])
    s = _parse_number(parts[1])
    l = _parse_number(parts[2])
    if h > 1:
        h = (h % 360.0) / 360.0
    r, g, b = colorsys.hls_to_rgb(h, l, s)  # note: colorsys uses HLS
    return _rgb_to_hex_float(r, g, b)


def _parse_hcl(text: str) -> str:
    # Attempt proper LCHuv -> sRGB1 via colorspacious if available
    inner = text[text.find("(") + 1 : text.rfind(")")]
    parts = [p.strip() for p in inner.split(",")]
    if len(parts) < 3:
        raise ValueError("hcl() requires 3 components")
    h = _parse_number(parts[0])  # degrees or 0..1
    c = _parse_number(parts[1])  # chroma 0..1 or 0..100%
    l = _parse_number(parts[2])  # lightness 0..1 or 0..100%

    # Normalize ranges
    if h > 1:
        h = (h % 360.0)
    else:
        h = h * 360.0
    if c <= 1:
        c = c * 100.0
    if l <= 1:
        l = l * 100.0

    try:
        import numpy as np
        from colorspacious import cspace_convert

        LCH = np.array([[l, c, h]])  # L in 0..100, C, H in degrees
        rgb = cspace_convert(LCH, "LCHuv", "sRGB1")  # clipped later
        r, g, b = [float(_clamp01(x)) for x in rgb[0]]
        return _rgb_to_hex_float(r, g, b)
    except Exception:
        # Fallback approximation via HSL using C as S
        import colorsys
        s = max(0.0, min(1.0, c / 100.0))
        hh = (h % 360.0) / 360.0
        ll = max(0.0, min(1.0, l / 100.0))
        r, g, b = colorsys.hls_to_rgb(hh, ll, s)
        return _rgb_to_hex_float(r, g, b)


def to_hex(color: str) -> str:
    """Parse a color specification to #RRGGBB.

    Supports:
    - Hex forms: #RGB/#RRGGBB/#RRGGBBAA
    - Named colors (matplotlib/CSS4): 'red', 'tab:blue', 'xkcd:salmon', etc.
    - rgb()/rgba() with 0..255, 0..1, or % values
    - hsv(h,s,v), hsl(h,s,l) with h in degrees or 0..1; s,v,l in 0..1 or %
    - hcl(h,c,l): uses colorspacious for LCHuv->sRGB1 if available, otherwise approximates via HSL
    """
    c = color.strip()
    # Hex
    if re.match(r"^#?[0-9A-Fa-f]{3}([0-9A-Fa-f]{3})?([0-9A-Fa-f]{2})?$", c):
        return _hex6(c)

    # functional syntax
    lower = c.lower()
    if lower.startswith("rgb(") or lower.startswith("rgba("):
        return _parse_rgb(c)
    if lower.startswith("hsv("):
        return _parse_hsv(c)
    if lower.startswith("hsl("):
        return _parse_hsl(c)
    if lower.startswith("hcl("):
        return _parse_hcl(c)

    # Named colors via matplotlib
    try:
        import matplotlib.colors as mc
        r, g, b = mc.to_rgb(c)
        return _rgb_to_hex_float(r, g, b)
    except Exception:
        # Minimal fallback named colors
        NAMED = {
            'red': '#FF0000','green':'#008000','blue':'#0000FF','black':'#000000','white':'#FFFFFF',
            'gray':'#808080','grey':'#808080','yellow':'#FFFF00','cyan':'#00FFFF','magenta':'#FF00FF',
            'purple':'#800080','orange':'#FFA500','brown':'#A52A2A','pink':'#FFC0CB','lime':'#00FF00',
            'navy':'#000080','teal':'#008080','olive':'#808000','maroon':'#800000','silver':'#C0C0C0',
            'gold':'#FFD700'
        }
        if c.lower() in NAMED:
            return NAMED[c.lower()].upper()
        raise ValueError(f"Unrecognized color: {color}")


def validate_colors(colors: Iterable[str]) -> List[str]:
    out: List[str] = []
    for s in colors:
        out.append(to_hex(str(s)))
    return out
