from __future__ import annotations

from contextlib import contextmanager
from typing import Dict, Optional
from importlib.resources import files


def _font_defaults(base_family: Optional[str]) -> Dict[str, object]:
    """Build a reasonable cross‑platform font fallback list.

    Strategy:
    - If a base_family is provided, place it first.
    - Try to enable packaged 'Noto Sans SC' (quietly); if available, include it early to support Chinese.
    - Prefer widely available families next: 'DejaVu Sans', then typical OS CJK fonts, then 'sans-serif'.
    This minimizes findfont warnings while preserving good CJK support.
    """
    families: list[str] = []
    if base_family:
        families.append(base_family)
    # Quietly register packaged font if present
    try:
        fam = enable_packaged_chinese_font()
        if fam:
            families.append(fam)
    except Exception:
        print('failed to load chinese font')
        pass
    # Generic fallbacks
    families += [
        "DejaVu Sans",           # ships with Matplotlib
    ]
    return {"font.family": families, "axes.unicode_minus": False}


def get_packaged_font_path() -> Optional[str]:
    """Return absolute path to the packaged Chinese font if available."""
    try:
        p = files("chinacolor").joinpath("data", "NotoSansSC-VariableFont_wght.ttf")
        if p.is_file():
            return str(p)
    except Exception:
        return None
    return None


def enable_packaged_chinese_font() -> str:
    """Register the packaged Noto Sans SC font with matplotlib and return its family name.

    Usage:
      fam = enable_packaged_chinese_font()
      set_theme('paper', base_family=fam)
    """
    import matplotlib.font_manager as fm

    path = get_packaged_font_path()
    if not path:
        # If not available, return a reasonable family hint
        return "Noto Sans SC"
    try:
        fm.fontManager.addfont(path)
    except Exception:
        # addfont may not exist on older mpl; ignore gracefully
        pass
    return "Noto Sans SC"


def set_default_font_to_packaged() -> None:
    """Set rcParams to use packaged Chinese font as default sans-serif."""
    import matplotlib as mpl
    fam = enable_packaged_chinese_font()
    families = [fam, "Source Han Sans SC", "Microsoft YaHei", "PingFang SC", "WenQuanYi Micro Hei", "SimHei", "DejaVu Sans", "sans-serif"]
    mpl.rcParams.update({"font.family": families, "axes.unicode_minus": False})


def _size_defaults(base_size: float) -> Dict[str, object]:
    # Map ggplot-like base_size to mpl sizes
    return {
        "font.size": base_size,  # base text
        "axes.titlesize": base_size * 1.3,
        "axes.labelsize": base_size * 0.95,
        "xtick.labelsize": base_size * 0.85,
        "ytick.labelsize": base_size * 0.85,
        "legend.fontsize": base_size * 0.85,
        "legend.title_fontsize": base_size * 0.9,
    }


def _grid(style_color: str, linestyle: str, lw: float, enable: bool) -> Dict[str, object]:
    return {
        "axes.grid": bool(enable),
        "grid.color": style_color,
        "grid.linestyle": linestyle,
        "grid.linewidth": lw,
        "grid.alpha": 1.0,
        # minor visibility left to user per-axes; we expose a helper below
        "xtick.minor.visible": False,
        "ytick.minor.visible": False,
    }


def _common_text_colors(title: str, subtitle: str, caption: str, label: str, tick: str) -> Dict[str, object]:
    return {
        "text.color": label,
        "axes.titlecolor": title,
        "axes.titleweight": "bold",
        "axes.labelcolor": label,
        "xtick.color": tick,
        "ytick.color": tick,
    }


def _with_recommended_cycle(style: Dict[str, object], theme_name: str,
                            with_colors: bool,
                            color_cycle_n: Optional[int],
                            direction: int = 1) -> Dict[str, object]:
    if not with_colors:
        return style
    try:
        from matplotlib import cycler
        from .recommend import pick_palette_for_theme
        n = color_cycle_n if color_cycle_n is not None else 10
        colors = pick_palette_for_theme(theme_name, kind="categorical", n=n, direction=direction)
        style.update({"axes.prop_cycle": cycler(color=colors)})
    except Exception:
        # If matplotlib not available or any error, skip silently
        pass
    return style


def theme_ctc_ink(base_size: float = 12, base_family: Optional[str] = None,
                  grid_major: bool = True, grid_minor: bool = False,
                  with_colors: bool = False,
                  color_cycle_n: Optional[int] = None,
                  direction: int = 1) -> Dict[str, object]:
    # Colors from the R theme_ctc_ink
    plot_bg = "#86908A"     # 千山翠
    panel_bg = "#6B7D73"    # 结绿
    border = "#C7C6B6"      # 霜地
    title = "#422517"       # 青骊
    subtitle = "#A46244"    # 老僧衣
    caption = "#C7C6B6"     # 霜地
    label = "#422517"       # 青骊
    tick = "#775039"        # 栗壳
    major = "#45493D"       # 绿云
    minor = "#D3CBC5"       # 藕丝秋半
    axis_line = "#A46244"   # 老僧衣

    style = {
        "figure.facecolor": plot_bg,
        "axes.facecolor": panel_bg,
        "axes.edgecolor": border,
        "axes.linewidth": 0.6,
        "legend.facecolor": panel_bg,
        "legend.edgecolor": border,
        "axes.titlepad": 10.0,
    }
    style.update(_font_defaults(base_family))
    style.update(_size_defaults(base_size))
    style.update(_grid(major if grid_major else panel_bg, "--", 0.3, grid_major))
    style.update(_common_text_colors(title, subtitle, caption, label, tick))
    # Axis line color
    style.update({
        "axes.edgecolor": border,
        "axes.labelweight": "bold",
    })
    # Minor grid visibility toggles
    if grid_minor:
        style.update({"xtick.minor.visible": True, "ytick.minor.visible": True})
    return _with_recommended_cycle(style, "ink", with_colors, color_cycle_n, direction)


def theme_ctc_mineral(base_size: float = 12, base_family: Optional[str] = None,
                      grid_major: bool = True, grid_minor: bool = False,
                      with_colors: bool = False,
                      color_cycle_n: Optional[int] = None,
                      direction: int = 1) -> Dict[str, object]:
    plot_bg = "#CAD7C5"   # 葭菼
    panel_bg = "#BECAB7"  # 冰台
    border = "#C7C6B6"    # 霜地
    title = "#422517"     # 青骊
    subtitle = "#A46244"  # 老僧衣
    caption = "#C7C6B6"   # 霜地
    label = "#422517"     # 青骊
    tick = "#775039"      # 栗壳
    major = "#B3BDA9"     # 青古
    minor = "#C0AD5E"     # 栾华

    style = {
        "figure.facecolor": plot_bg,
        "axes.facecolor": panel_bg,
        "axes.edgecolor": border,
        "axes.linewidth": 0.6,
        "legend.facecolor": plot_bg,
        "legend.edgecolor": border,
        "axes.titlepad": 10.0,
    }
    style.update(_font_defaults(base_family))
    style.update(_size_defaults(base_size))
    style.update(_grid(major if grid_major else panel_bg, "--", 0.3, grid_major))
    style.update(_common_text_colors(title, subtitle, caption, label, tick))
    if grid_minor:
        style.update({"xtick.minor.visible": True, "ytick.minor.visible": True, "grid.linestyle": ":", "grid.color": minor})
    return _with_recommended_cycle(style, "mineral", with_colors, color_cycle_n, direction)


def theme_ctc_paper(base_size: float = 12, base_family: Optional[str] = None,
                    grid_major: bool = True, grid_minor: bool = False,
                    with_colors: bool = False,
                    color_cycle_n: Optional[int] = None,
                    direction: int = 1) -> Dict[str, object]:
    plot_bg = "#F5F2E9"   # 凝脂
    panel_bg = "#EAE4D1"  # 玉色
    border = "#C7C6B6"    # 霜地
    title = "#422517"     # 青骊
    subtitle = "#A46244"  # 老僧衣
    caption = "#C7C6B6"   # 霜地
    label = "#422517"     # 青骊
    tick = "#775039"      # 栗壳
    major = "#E0E0D0"     # 韶粉
    minor = "#EBEDDF"     # 吉量
    axis_line = "#A46244"  # 老僧衣

    style = {
        "figure.facecolor": plot_bg,
        "axes.facecolor": panel_bg,
        "axes.edgecolor": border,
        "axes.linewidth": 0.6,
        "legend.facecolor": plot_bg,
        "legend.edgecolor": border,
        "axes.titlepad": 10.0,
    }
    style.update(_font_defaults(base_family))
    style.update(_size_defaults(base_size))
    style.update(_grid(major if grid_major else panel_bg, "--", 0.3, grid_major))
    style.update(_common_text_colors(title, subtitle, caption, label, tick))
    # Axis edge resembles accent color
    style.update({"axes.edgecolor": border})
    if grid_minor:
        style.update({"xtick.minor.visible": True, "ytick.minor.visible": True, "grid.linestyle": ":", "grid.color": minor})
    return _with_recommended_cycle(style, "paper", with_colors, color_cycle_n, direction)


def theme_ctc_bronze(base_size: float = 12, base_family: Optional[str] = None,
                     grid_major: bool = True, grid_minor: bool = False,
                     oxidation_level: str = "heavy",
                     with_colors: bool = False,
                     color_cycle_n: Optional[int] = None,
                     direction: int = 1) -> Dict[str, object]:
    if oxidation_level == "heavy":
        plot_bg = "#E6D9BE"
        panel_bg = "#D4BE98"
        text_color = "#301A12"
        grid_color = "#4A9E96"  # dark bronze blue
        border_color = "#3D8E86"
        tick = text_color
        title = text_color
        subtitle = text_color
        caption = text_color
        label = text_color
    else:
        plot_bg = "#DFD6B8"
        panel_bg = "#C4B798"
        text_color = "#422517"
        grid_color = "#756C4B"
        border_color = "#3D8E86"
        tick = "#775039"
        title = text_color
        subtitle = "#A46244"
        caption = "#C7C6B6"
        label = text_color

    style = {
        "figure.facecolor": plot_bg,
        "axes.facecolor": panel_bg,
        "axes.edgecolor": border_color,
        "axes.linewidth": 0.4,
        "legend.facecolor": plot_bg,
        "legend.edgecolor": border_color,
        "axes.titlepad": 10.0,
    }
    style.update(_font_defaults(base_family))
    style.update(_size_defaults(base_size))
    style.update(_grid(grid_color if grid_major else panel_bg, "--", 0.3, grid_major))
    style.update(_common_text_colors(title, subtitle, caption, label, tick))
    if grid_minor:
        style.update({"xtick.minor.visible": True, "ytick.minor.visible": True})
    return _with_recommended_cycle(style, "bronze", with_colors, color_cycle_n, direction)


def theme_ctc_dunhuang(base_size: float = 12, base_family: Optional[str] = None,
                       grid_major: bool = True, grid_minor: bool = False,
                       border_style: str = "ornate",
                       with_colors: bool = False,
                       color_cycle_n: Optional[int] = None,
                       direction: int = 1) -> Dict[str, object]:
    # Colors sourced from R theme
    plot_bg = "#DFD6B8"   # Huangrun
    panel_bg = "#D5C8A0"  # Jianxiang
    border = "#206864"    # Shilu (malachite)
    title = "#C12C1F"     # Shanhuhe (cinnabar)
    subtitle = "#1A2847"  # Huaqing
    caption = "#775039"   # Lique
    label = subtitle
    tick = "#206864"
    grid_major_color = "#3D8E86"  # Tongqing
    grid_minor_color = "#5DA39D"  # Erlu

    linew = 0.6 if border_style == "ornate" else 0.3

    style = {
        "figure.facecolor": plot_bg,
        "axes.facecolor": panel_bg,
        "axes.edgecolor": border,
        "axes.linewidth": linew,
        "legend.facecolor": plot_bg,
        "legend.edgecolor": border,
        "axes.titlepad": 12.0,
    }
    style.update(_font_defaults(base_family))
    # Slightly larger titles (murals readability)
    s = _size_defaults(base_size)
    s["axes.titlesize"] = base_size * 1.4
    s["legend.title_fontsize"] = base_size * 0.95
    style.update(s)
    style.update(_grid(grid_major_color if grid_major else panel_bg, "--", 0.25, grid_major))
    style.update(_common_text_colors(title, subtitle, caption, label, tick))
    if grid_minor:
        style.update({"xtick.minor.visible": True, "ytick.minor.visible": True, "grid.linestyle": ":", "grid.color": grid_minor_color, "grid.linewidth": 0.15})
    return _with_recommended_cycle(style, "dunhuang", with_colors, color_cycle_n, direction)


def get_theme(name: str, **kwargs) -> Dict[str, object]:
    name = name.lower()
    if name in ("ink", "ctc_ink", "theme_ctc_ink"):
        return theme_ctc_ink(**kwargs)
    if name in ("mineral", "ctc_mineral", "theme_ctc_mineral"):
        return theme_ctc_mineral(**kwargs)
    if name in ("paper", "ctc_paper", "theme_ctc_paper"):
        return theme_ctc_paper(**kwargs)
    if name in ("bronze", "ctc_bronze", "theme_ctc_bronze"):
        return theme_ctc_bronze(**kwargs)
    if name in ("dunhuang", "ctc_dunhuang", "theme_ctc_dunhuang"):
        return theme_ctc_dunhuang(**kwargs)
    raise KeyError(f"Unknown theme: {name}")


def set_theme(name: str, **kwargs) -> None:
    import matplotlib as mpl
    rc = get_theme(name, **kwargs)
    mpl.rcParams.update(rc)


@contextmanager
def theme_context(name: str, **kwargs):
    import matplotlib.pyplot as plt
    rc = get_theme(name, **kwargs)
    with plt.rc_context(rc):
        yield


# Convenience context managers
def use_theme_ctc_ink(**kwargs):
    return theme_context("ink", **kwargs)


def use_theme_ctc_mineral(**kwargs):
    return theme_context("mineral", **kwargs)


def use_theme_ctc_paper(**kwargs):
    return theme_context("paper", **kwargs)


def use_theme_ctc_bronze(**kwargs):
    return theme_context("bronze", **kwargs)


def use_theme_ctc_dunhuang(**kwargs):
    return theme_context("dunhuang", **kwargs)
