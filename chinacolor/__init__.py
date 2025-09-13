from .dataset import load_chinacolor, load_palette_list
from .palettes import (
    list_palettes,
    find_palette,
    get_palette,
    custom_palette,
    create_color_pick,
    custom_palette_pick,
)
from .frames import colors_df, palettes_df, list_colors
from .themes import (
    theme_ctc_ink,
    theme_ctc_mineral,
    theme_ctc_paper,
    theme_ctc_bronze,
    theme_ctc_dunhuang,
    get_packaged_font_path,
    enable_packaged_chinese_font,
    set_default_font_to_packaged,
    get_theme,
    set_theme,
    theme_context,
    use_theme_ctc_ink,
    use_theme_ctc_mineral,
    use_theme_ctc_paper,
    use_theme_ctc_bronze,
    use_theme_ctc_dunhuang,
)
def recommended_palettes_for_theme(name):
    from .recommend import recommended_palettes_for_theme as _fn
    return _fn(name)

def pick_palette_for_theme(name, kind="categorical", n=None, direction=1):
    from .recommend import pick_palette_for_theme as _fn
    return _fn(name, kind=kind, n=n, direction=direction)

def pick_cmap_for_theme(name, kind="sequential", direction=1):
    from .recommend import pick_cmap_for_theme as _fn
    return _fn(name, kind=kind, direction=direction)

def generate_colors_html(output=None, open_in_browser=True):
    from .browser import generate_colors_html as _fn
    return _fn(output=output, open_in_browser=open_in_browser)

def generate_palettes_html(output=None, open_in_browser=True):
    from .browser import generate_palettes_html as _fn
    return _fn(output=output, open_in_browser=open_in_browser)

def generate_site(output_dir="site", open_index=True, include_basic=True, include_datatables=False):
    from .browser import generate_site as _fn
    return _fn(output_dir=output_dir, open_index=open_index, include_basic=include_basic, include_datatables=include_datatables)

# DataTables variants
def generate_colors_datatable(output=None, open_in_browser=True, page_length=25):
    from .browser import generate_colors_datatable as _fn
    return _fn(output=output, open_in_browser=open_in_browser, page_length=page_length)

def generate_palettes_datatable(output=None, open_in_browser=True, page_length=20):
    from .browser import generate_palettes_datatable as _fn
    return _fn(output=output, open_in_browser=open_in_browser, page_length=page_length)

# ctc_palette wrapper
def ctc_palette(type="built_in", palette_name=None, n=None, direction=1, color_pick=None, show_colors=False, palette_title=None):
    from .ctc import ctc_palette as _fn
    return _fn(type=type, palette_name=palette_name, n=n, direction=direction, color_pick=color_pick, show_colors=show_colors, palette_title=palette_title)
def plot_palette(identifier, n=None, direction=1, name=None, show_text=False):
    from .plotting import plot_palette as _plot_palette
    return _plot_palette(identifier, n=n, direction=direction, name=name, show_text=show_text)

def plot_palettes(identifiers, direction=1):
    from .plotting import plot_palettes as _plot_palettes
    return _plot_palettes(identifiers, direction=direction)

def plot_color_grid(show_group=False):
    from .plotting import plot_color_grid as _plot_color_grid
    return _plot_color_grid(show_group=show_group)

def get_cmap(identifier, n=None, direction=1):
    # Lazy import to avoid hard dependency at import time
    from .cmap import get_cmap as _get_cmap
    return _get_cmap(identifier, n=n, direction=direction)

__all__ = [
    "load_chinacolor",
    "load_palette_list",
    "list_palettes",
    "find_palette",
    "get_palette",
    "custom_palette",
    "create_color_pick",
    "custom_palette_pick",
    "get_cmap",
    "plot_palette",
    "plot_palettes",
    "plot_color_grid",
    "colors_df",
    "palettes_df",
    "list_colors",
    # Themes
    "theme_ctc_ink",
    "theme_ctc_mineral",
    "theme_ctc_paper",
    "theme_ctc_bronze",
    "theme_ctc_dunhuang",
    "get_packaged_font_path",
    "enable_packaged_chinese_font",
    "set_default_font_to_packaged",
    "get_theme",
    "set_theme",
    "theme_context",
    "use_theme_ctc_ink",
    "use_theme_ctc_mineral",
    "use_theme_ctc_paper",
    "use_theme_ctc_bronze",
    "use_theme_ctc_dunhuang",
    # Recommendations
    "recommended_palettes_for_theme",
    "pick_palette_for_theme",
    "pick_cmap_for_theme",
    # Browser
    "generate_colors_html",
    "generate_palettes_html",
    "generate_site",
]
