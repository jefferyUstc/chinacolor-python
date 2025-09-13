from __future__ import annotations

import os
import webbrowser
from pathlib import Path
from typing import Optional

from .dataset import load_chinacolor, load_palette_list
from importlib.resources import files
from .frames import colors_df as _colors_df, palettes_df as _palettes_df


BASE_STYLE = """
body { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Noto Sans, Arial; margin: 20px; }/* base style handled by templates; keep for dt pages */
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #ddd; padding: 6px 8px; font-size: 13px; }
th { background: #f5f5f5; position: sticky; top: 0; }
.swatch { width: 48px; height: 18px; border: 1px solid #222; display: inline-block; }
.palette { margin: 12px 0; padding: 8px; border: 1px solid #e0e0e0; background: #fff; }
.row { display: flex; gap: 2px; align-items: center; flex-wrap: wrap; }
.pill { display:inline-block; width: 28px; height: 18px; border:1px solid #222; }
.head { font-weight: 600; margin-bottom: 6px; }
input[type='search'] { padding: 6px 8px; width: 280px; }
"""


def _write_file(path: Path, html: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def generate_colors_html(output: Optional[str] = None, open_in_browser: bool = True) -> Path:
    colors = load_chinacolor()
    output = output or "colors.html"
    out = Path(output)

    # Build rows
    rows = []
    for c in colors:
        rows.append(
            f"<tr><td>{c.get('color_id')}</td>"
            f"<td><span class='swatch' style='background:{c.get('hex')}'></span></td>"
            f"<td>{c.get('hex')}</td>"
            f"<td>{c.get('name','')}</td>"
            f"<td>{c.get('group_id','')}</td>"
            f"<td>{c.get('subgroup_id','')}</td>"
            f"<td>{c.get('solar_term_c','')}</td>"
            f"<td>{c.get('solar_term_e','')}</td>"
            f"</tr>"
        )
    tpl = files('chinacolor').joinpath('templates','colors_basic.html').read_text(encoding='utf-8')
    html = tpl.replace("{{ROWS}}", "".join(rows))
    _write_file(out, html)
    if open_in_browser:
        webbrowser.open(out.resolve().as_uri())
    return out


def generate_palettes_html(output: Optional[str] = None, open_in_browser: bool = True) -> Path:
    pl_map, order = load_palette_list()
    output = output or "palettes.html"
    out = Path(output)
    blocks = []
    for key in order:
        p = pl_map[key]
        colors = p.get("hex", [])
        head = f"{key} · {p.get('palette_name','')} · {p.get('palette_name_e','')} · {p.get('type','')} ({p.get('color_count','')})"
        pills = "".join([f"<span class='pill' style='background:{h}' title='{h}'></span>" for h in colors])
        blocks.append(f"<div class='palette'><div class='head'>{head}</div><div class='row'>{pills}</div></div>")
    tpl = files('chinacolor').joinpath('templates','palettes_basic.html').read_text(encoding='utf-8')
    html = tpl.replace("{{BLOCKS}}", "".join(blocks))
    _write_file(out, html)
    if open_in_browser:
        webbrowser.open(out.resolve().as_uri())
    return out


def generate_site(output_dir: str = "site",
                  open_index: bool = True,
                  include_basic: bool = True,
                  include_datatables: bool = False) -> Path:
    outdir = Path(output_dir)
    colors_path = outdir / "colors.html"
    palettes_path = outdir / "palettes.html"
    colors_dt_path = outdir / "colors_dt.html"
    palettes_dt_path = outdir / "palettes_dt.html"

    # Generate basic pages
    if include_basic:
        generate_colors_html(colors_path, open_in_browser=False)
        generate_palettes_html(palettes_path, open_in_browser=False)

    # Generate advanced DataTables pages
    has_dt = False
    if include_datatables:
        try:
            generate_colors_datatable(colors_dt_path, open_in_browser=False)
            generate_palettes_datatable(palettes_dt_path, open_in_browser=False)
            has_dt = True
        except Exception:
            has_dt = False
    index = outdir / "index.html"
    tpl_idx = files('chinacolor').joinpath('templates','index.html').read_text(encoding='utf-8')
    from datetime import datetime
    html_idx = tpl_idx.replace("{{DT_COLORS}}", ("<div class=\"card\"><h3>Colors (DataTables)</h3><p>Sortable, filterable, paginated table.</p><a class=\"btn\" href=\"colors_dt.html\">Open</a></div>" if has_dt else "")) \
                     .replace("{{DT_PALETTES}}", ("<div class=\"card\"><h3>Palettes (DataTables)</h3><p>Sortable, filterable, paginated table.</p><a class=\"btn\" href=\"palettes_dt.html\">Open</a></div>" if has_dt else "")) \
                     .replace("{{TIMESTAMP}}", datetime.now().strftime("%Y-%m-%d %H:%M")) \
                     .replace("{{EXTRA_HEAD}}", "")
    index.write_text(html_idx, encoding='utf-8')
    if open_index:
        webbrowser.open(index.resolve().as_uri())
    return index


# ----- DataTables versions (requires internet to load CDN assets) -----

DATATABLES_HEAD = """
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.1/css/jquery.dataTables.min.css" />
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script src="https://cdn.datatables.net/1.13.1/js/jquery.dataTables.min.js"></script>
"""


def _datatable_init_script(table_id: str, page_length: int = 25) -> str:
    return f"""
<script>
$(document).ready(function() {{
  // Add per-column search inputs
  $('#{table_id} tfoot th').each(function() {{
    var title = $(this).text();
    $(this).html('<input type="text" placeholder="Search '+title+'" style="width:100%" />');
  }});
  var table = $('#{table_id}').DataTable({{
    pageLength: {page_length},
    scrollX: true,
    deferRender: true
  }});
  // Apply column search
  table.columns().every(function () {{
    var that = this;
    $('input', this.footer()).on('keyup change clear', function() {{
      if (that.search() !== this.value) {{ that.search(this.value).draw(); }}
    }});
  }});
}});
</script>
"""


def generate_colors_datatable(output: Optional[str] = None, open_in_browser: bool = True, page_length: int = 25) -> Path:
    output = output or "colors_dt.html"
    out = Path(output)
    # Prefer pandas DataFrame (if available)
    try:
        df = _colors_df()
    except Exception:
        # Fallback to plain list
        df = None
        rows = load_chinacolor()

    # Build table body
    body_rows = []
    data_rows = df.to_dict(orient='records') if df is not None else rows
    for c in data_rows:
        body_rows.append(
            f"<tr>"
            f"<td>{c.get('color_id','')}</td>"
            f"<td><span class='swatch' style='background:{c.get('hex','')}'></span></td>"
            f"<td>{c.get('hex','')}</td>"
            f"<td>{c.get('name','')}</td>"
            f"<td>{c.get('group_id','')}</td>"
            f"<td>{c.get('subgroup_id','')}</td>"
            f"<td>{c.get('solar_term_c','')}</td>"
            f"<td>{c.get('solar_term_e','')}</td>"
            f"</tr>"
        )

    tpl = files('chinacolor').joinpath('templates','colors_dt.html').read_text(encoding='utf-8')
    html = tpl.replace('{{BODY_ROWS}}', ''.join(body_rows)).replace('{{PAGE_LENGTH}}', str(page_length))
    _write_file(out, html)
    if open_in_browser:
        webbrowser.open(out.resolve().as_uri())
    return out


def generate_palettes_datatable(output: Optional[str] = None, open_in_browser: bool = True, page_length: int = 20) -> Path:
    output = output or "palettes_dt.html"
    out = Path(output)
    try:
        df = _palettes_df()
        records = df.to_dict(orient='records')
    except Exception:
        pl_map, order = load_palette_list()
        records = []
        for idx, key in enumerate(order, start=1):
            p = pl_map[key]
            records.append({
                'index': idx,
                'element_name': key,
                'palette_name': p.get('palette_name',''),
                'palette_name_e': p.get('palette_name_e',''),
                'type': p.get('type',''),
                'color_count': p.get('color_count',''),
                'hex': p.get('hex', [])
            })

    body_rows = []
    for r in records:
        preview = ''.join([f"<span class='pill' style='background:{h}' title='{h}'></span>" for h in r.get('hex', [])])
        body_rows.append(
            f"<tr>"
            f"<td>{r.get('index','')}</td>"
            f"<td>{r.get('element_name','')}</td>"
            f"<td>{r.get('palette_name','')}</td>"
            f"<td>{r.get('palette_name_e','')}</td>"
            f"<td>{r.get('type','')}</td>"
            f"<td>{r.get('color_count','')}</td>"
            f"<td>{preview}</td>"
            f"</tr>"
        )

    tpl = files('chinacolor').joinpath('templates','palettes_dt.html').read_text(encoding='utf-8')
    html = tpl.replace('{{BODY_ROWS}}', ''.join(body_rows)).replace('{{PAGE_LENGTH}}', str(page_length))
    _write_file(out, html)
    if open_in_browser:
        webbrowser.open(out.resolve().as_uri())
    return out
